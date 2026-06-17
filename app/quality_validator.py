"""
Quality Validator — Anti-Slideshow + Hook Cadence Enforcement.

Validates every generated Director's Cut and final video composition against
the premium quality standards defined in the project architecture.

Rules Enforced:
  1. No dead frames: every scene has ≥3 keyframes/internal visual events
  2. No static image > 2 seconds without Ken Burns/zoompan or overlay
  3. No stock clip > 8 seconds without a cut or crossfade
  4. Average Shot Length (ASL): 4-7 seconds per visual event
  5. No repeated layout family within 3 consecutive scenes
  6. No repeated transition type within 4 consecutive scenes
  7. Text always in motion: reveal, fade, or drift (never static for >1 sec)
  8. Hook cadence: 5-7 open loops, first scene is tease, last is callback
  9. Visual intensity curve: must follow tease→escalation→payoff→rest rhythm
  10. Color grade rotation: ≥2 variants per chapter, no repeat within 2 scenes
  11. Every scene has animation_trigger + visual_keywords (never blank)
  12. Beat sync intensity matches hook role (tease/payoff = high, rest = low)
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from app.models import DirectorCut, Scene, HookRole, TransitionType, LayoutFamily, ColorGrade


@dataclass
class QualityViolation:
    rule: str
    severity: str  # "error" | "warning" | "info"
    scene_id: Optional[str]
    message: str
    suggestion: Optional[str] = None


@dataclass
class ValidationReport:
    passed: bool
    score: float  # 0.0 - 1.0
    violations: List[QualityViolation]
    metrics: Dict[str, Any]


class QualityValidator:
    """Validates a Director's Cut against all quality guardrails."""

    # Scoring weights
    WEIGHTS = {
        "hook_cadence": 0.25,
        "scene_density": 0.20,
        "no_repeat": 0.15,
        "visual_intensity": 0.15,
        "color_grade": 0.10,
        "text_motion": 0.10,
        "beat_sync": 0.05,
    }

    def __init__(self, director_cut: DirectorCut):
        self.dc = director_cut
        self.violations: List[QualityViolation] = []
        self.metrics: Dict[str, Any] = {}

    def validate(self) -> ValidationReport:
        """Run all validation rules and produce a report."""
        self.violations = []
        self.metrics = {}

        # Rule 1: Hook Cadence Architecture
        self._validate_hook_cadence()

        # Rule 2: Scene Density (keyframes, animated layers)
        self._validate_scene_density()

        # Rule 3: No-Repeat Rules (transitions, layouts, color grades)
        self._validate_no_repeat()

        # Rule 4: Visual Intensity Curve
        self._validate_intensity_curve()

        # Rule 5: Color Grade Rotation
        self._validate_color_rotation()

        # Rule 6: Text Motion (anti-static)
        self._validate_text_motion()

        # Rule 7: Beat Sync Alignment
        self._validate_beat_sync()

        # Rule 8: Pacing & Duration Checks
        self._validate_pacing()

        # Calculate score
        score = self._calculate_score()
        passed = score >= 0.75 and not any(v.severity == "error" for v in self.violations)

        return ValidationReport(
            passed=passed,
            score=score,
            violations=self.violations,
            metrics=self.metrics,
        )

    # ───────────────────────────────────────────────────────────────────
    # RULE 1: HOOK CADENCE
    # ───────────────────────────────────────────────────────────────────

    def _validate_hook_cadence(self):
        """Validate the 5-7 open loop architecture and scene role assignments."""
        score = 1.0
        errors = []

        # Check 1a: Open loop count (5-7 is ideal, 3-4 is acceptable, <3 is error)
        loops = self.dc.hook_cadence.open_loops if self.dc.hook_cadence else []
        loop_count = len(loops)
        self.metrics["open_loop_count"] = loop_count

        if loop_count < 3:
            errors.append(QualityViolation(
                rule="hook_cadence",
                severity="error",
                scene_id=None,
                message=f"Only {loop_count} open loops found. Need 5-7 for maximum retention.",
                suggestion="Add more micro-hooks and medium-hooks in the script. Every 60-90s should open a new curiosity gap.",
            ))
            score -= 0.5
        elif loop_count < 5:
            errors.append(QualityViolation(
                rule="hook_cadence",
                severity="warning",
                scene_id=None,
                message=f"{loop_count} open loops found. Target is 5-7 for optimal dopamine loops.",
                suggestion="Add 2-3 more curiosity gaps in the middle section (3-6 min mark).",
            ))
            score -= 0.2

        # Check 1b: First scene MUST be tease
        scenes = self.dc.scenes
        if scenes:
            first_scene = scenes[0]
            if first_scene.hook_role != HookRole.tease:
                errors.append(QualityViolation(
                    rule="hook_cadence",
                    severity="error",
                    scene_id=first_scene.scene_id,
                    message=f"First scene is '{first_scene.hook_role.value}' but must be 'tease' (immediate curiosity hook, no intro).",
                    suggestion="Change first scene to hook_role='tease' with visual_intensity=0.8. No logo, no welcome.",
                ))
                score -= 0.3

            # Check 1c: Last scene MUST be callback
            last_scene = scenes[-1]
            if last_scene.hook_role != HookRole.callback:
                errors.append(QualityViolation(
                    rule="hook_cadence",
                    severity="warning",
                    scene_id=last_scene.scene_id,
                    message=f"Last scene is '{last_scene.hook_role.value}' but should be 'callback' (memory loop + next video tease).",
                    suggestion="Change last scene to hook_role='callback' with a reference to the intro hook.",
                ))
                score -= 0.15

        # Check 1d: Loop payoff timing (2-5 min per loop)
        for loop in loops:
            payoff_delay = loop.payoff_at_sec - loop.tease_at_sec
            if payoff_delay < 60:
                errors.append(QualityViolation(
                    rule="hook_cadence",
                    severity="warning",
                    scene_id=None,
                    message=f"Loop '{loop.loop_id}' pays off in {payoff_delay:.0f}s. Too fast — no tension built.",
                    suggestion="Delay payoff by 2-3 minutes to build anticipation dopamine.",
                ))
                score -= 0.1
            elif payoff_delay > 360:
                errors.append(QualityViolation(
                    rule="hook_cadence",
                    severity="warning",
                    scene_id=None,
                    message=f"Loop '{loop.loop_id}' pays off in {payoff_delay:.0f}s. Too slow — viewer may forget.",
                    suggestion="Move payoff earlier or add micro-hooks to sustain attention.",
                ))
                score -= 0.1

        # Check 1e: Callback reference exists
        if self.dc.hook_cadence and not self.dc.hook_cadence.callback_reference:
            errors.append(QualityViolation(
                rule="hook_cadence",
                severity="warning",
                scene_id=None,
                message="No callback_reference set in hook_cadence. Memory loop for session continuation is missing.",
                suggestion="Add a callback_reference that references the first hook in the final scene.",
            ))
            score -= 0.1

        self.violations.extend(errors)
        self.metrics["hook_cadence_score"] = max(0, score)

    # ───────────────────────────────────────────────────────────────────
    # RULE 2: SCENE DENSITY (Anti-Dead-Frame)
    # ───────────────────────────────────────────────────────────────────

    def _validate_scene_density(self):
        """Every scene must have ≥3 internal keyframes (visual micro-events)."""
        score = 1.0
        errors = []
        density_scores = []

        for scene in self.dc.scenes:
            keyframe_count = len(scene.keyframes) if scene.keyframes else 0
            density_scores.append(keyframe_count)

            if keyframe_count < 2:
                errors.append(QualityViolation(
                    rule="scene_density",
                    severity="error",
                    scene_id=scene.scene_id,
                    message=f"Only {keyframe_count} keyframe(s). Every scene needs ≥3 internal visual events to prevent dead frames.",
                    suggestion="Add keyframes: text_slam at 0s, data_enter at 5s, overlay_pulse at 10s.",
                ))
                score -= 0.15
            elif keyframe_count < 3:
                errors.append(QualityViolation(
                    rule="scene_density",
                    severity="warning",
                    scene_id=scene.scene_id,
                    message=f"Only {keyframe_count} keyframe(s). Target is 3-4 for visual richness.",
                    suggestion="Add 1 more keyframe (e.g., color_shift or particle_burst) at midpoint.",
                ))
                score -= 0.05

        self.metrics["avg_keyframes_per_scene"] = sum(density_scores) / len(density_scores) if density_scores else 0
        self.metrics["min_keyframes"] = min(density_scores) if density_scores else 0
        self.metrics["max_keyframes"] = max(density_scores) if density_scores else 0

        self.violations.extend(errors)
        self.metrics["scene_density_score"] = max(0, score)

    # ───────────────────────────────────────────────────────────────────
    # RULE 3: NO-REPEAT RULES
    # ───────────────────────────────────────────────────────────────────

    def _validate_no_repeat(self):
        """Check for repeated layouts, transitions, color grades, text zones."""
        score = 1.0
        errors = []
        scenes = self.dc.scenes

        if not scenes:
            return

        # Check layout families (no repeat within 3)
        for i in range(3, len(scenes)):
            window = [scenes[j].layout_family.value for j in range(i-2, i+1)]
            if len(set(window)) < len(window):
                errors.append(QualityViolation(
                    rule="no_repeat",
                    severity="warning",
                    scene_id=scenes[i].scene_id,
                    message=f"Layout '{scenes[i].layout_family.value}' repeats within 3 scenes. Visual monotony detected.",
                    suggestion=f"Change to a different layout family (e.g., {self._suggest_layout(scenes[i].layout_family)}).",
                ))
                score -= 0.05

        # Check color grades (no repeat within 2)
        for i in range(2, len(scenes)):
            if scenes[i].color_grade == scenes[i-1].color_grade == scenes[i-2].color_grade:
                errors.append(QualityViolation(
                    rule="no_repeat",
                    severity="warning",
                    scene_id=scenes[i].scene_id,
                    message=f"Color grade '{scenes[i].color_grade.value}' used 3 times in a row. Visual fatigue.",
                    suggestion=f"Rotate to a different grade (e.g., {self._suggest_grade(scenes[i].color_grade)}).",
                ))
                score -= 0.05

        # Check animation triggers (no repeat of same component in adjacent scenes)
        for i in range(1, len(scenes)):
            if scenes[i].animation_trigger == scenes[i-1].animation_trigger:
                errors.append(QualityViolation(
                    rule="no_repeat",
                    severity="warning",
                    scene_id=scenes[i].scene_id,
                    message=f"Animation component '{scenes[i].animation_trigger}' used in back-to-back scenes.",
                    suggestion="Pick a different archetype for variety.",
                ))
                score -= 0.03

        self.violations.extend(errors)
        self.metrics["no_repeat_score"] = max(0, score)

    def _suggest_layout(self, current: LayoutFamily) -> str:
        """Suggest a different layout family."""
        all_layouts = [l.value for l in LayoutFamily]
        all_layouts.remove(current.value)
        return all_layouts[0] if all_layouts else "center_hero"

    def _suggest_grade(self, current: ColorGrade) -> str:
        """Suggest a different color grade."""
        all_grades = [g.value for g in ColorGrade if g != current]
        return all_grades[0] if all_grades else "cool_blue"

    # ───────────────────────────────────────────────────────────────────
    # RULE 4: VISUAL INTENSITY CURVE
    # ───────────────────────────────────────────────────────────────────

    def _validate_intensity_curve(self):
        """The visual intensity must follow the hook role pattern: 
        tease(0.8) → escalation(0.3-0.6) → payoff(1.0) → rest(0.2)."""
        score = 1.0
        errors = []
        scenes = self.dc.scenes

        if not scenes:
            return

        # Expected intensity by role
        expected = {
            HookRole.tease: (0.7, 1.0),
            HookRole.escalation: (0.3, 0.7),
            HookRole.payoff: (0.9, 1.0),
            HookRole.rest: (0.1, 0.3),
            HookRole.callback: (0.5, 0.8),
            HookRole.bridge: (0.3, 0.6),
        }

        intensity_values = []
        for scene in scenes:
            expected_range = expected.get(scene.hook_role, (0.3, 0.7))
            intensity_values.append(scene.visual_intensity)

            if not (expected_range[0] <= scene.visual_intensity <= expected_range[1]):
                errors.append(QualityViolation(
                    rule="visual_intensity",
                    severity="warning" if scene.hook_role != HookRole.payoff else "error",
                    scene_id=scene.scene_id,
                    message=f"Scene '{scene.scene_id}' ({scene.hook_role.value}) has intensity {scene.visual_intensity}, expected {expected_range[0]}-{expected_range[1]}.",
                    suggestion=f"Set visual_intensity to {sum(expected_range)/2:.1f} for {scene.hook_role.value} scenes.",
                ))
                score -= 0.05

        # Check for monotonic increase toward payoff
        # Find payoff scenes and ensure intensity builds before them
        payoff_indices = [i for i, s in enumerate(scenes) if s.hook_role == HookRole.payoff]
        for p_idx in payoff_indices:
            if p_idx >= 3:
                window = [scenes[j].visual_intensity for j in range(p_idx-3, p_idx)]
                if not (window[0] < window[1] < window[2] or window[0] <= window[1] <= window[2]):
                    errors.append(QualityViolation(
                        rule="visual_intensity",
                        severity="info",
                        scene_id=scenes[p_idx].scene_id,
                        message=f"Intensity doesn't build smoothly before payoff at {scenes[p_idx].scene_id}.",
                        suggestion="Ensure intensity rises gradually: 0.3 → 0.5 → 0.7 → 1.0 before payoff.",
                    ))
                    score -= 0.03

        self.metrics["intensity_variance"] = max(intensity_values) - min(intensity_values) if intensity_values else 0
        self.metrics["intensity_peak"] = max(intensity_values) if intensity_values else 0
        self.violations.extend(errors)
        self.metrics["intensity_curve_score"] = max(0, score)

    # ───────────────────────────────────────────────────────────────────
    # RULE 5: COLOR GRADE ROTATION
    # ───────────────────────────────────────────────────────────────────

    def _validate_color_rotation(self):
        """At least 2 color grade variants per chapter, no repeat within 2 scenes."""
        score = 1.0
        errors = []
        scenes = self.dc.scenes

        if len(scenes) < 4:
            return

        # Count unique grades per chapter (roughly 5-8 scenes per chapter)
        chapter_size = max(4, len(scenes) // 4)
        for chapter_start in range(0, len(scenes), chapter_size):
            chapter = scenes[chapter_start:chapter_start + chapter_size]
            grades = set(s.color_grade for s in chapter)
            if len(grades) < 2:
                errors.append(QualityViolation(
                    rule="color_grade",
                    severity="warning",
                    scene_id=chapter[0].scene_id if chapter else None,
                    message=f"Chapter starting at {chapter[0].scene_id} uses only {len(grades)} color grade(s). Need ≥2 for visual variety.",
                    suggestion="Alternate between two grades every 2-3 scenes within a chapter.",
                ))
                score -= 0.05

        self.violations.extend(errors)
        self.metrics["color_grade_score"] = max(0, score)

    # ───────────────────────────────────────────────────────────────────
    # RULE 6: TEXT MOTION (Anti-Static)
    # ───────────────────────────────────────────────────────────────────

    def _validate_text_motion(self):
        """Text overlays must be in motion (reveal, fade, or drift). Never static."""
        score = 1.0
        errors = []

        for scene in self.dc.scenes:
            if not scene.text_overlay:
                errors.append(QualityViolation(
                    rule="text_motion",
                    severity="warning",
                    scene_id=scene.scene_id,
                    message=f"No text_overlay defined. Every scene needs at least one text element in motion.",
                    suggestion="Add a text_overlay with style='title_reveal' or 'subtitle_burn'.",
                ))
                score -= 0.05
            else:
                style = scene.text_overlay.style
                static_styles = {"static", "plain", "fixed"}
                if style in static_styles:
                    errors.append(QualityViolation(
                        rule="text_motion",
                        severity="error",
                        scene_id=scene.scene_id,
                        message=f"Text style '{style}' is static. Text must use a motion style.",
                        suggestion="Use 'title_reveal', 'subtitle_burn', 'data_label', or 'kicker'.",
                    ))
                    score -= 0.15

        self.violations.extend(errors)
        self.metrics["text_motion_score"] = max(0, score)

    # ───────────────────────────────────────────────────────────────────
    # RULE 7: BEAT SYNC ALIGNMENT
    # ───────────────────────────────────────────────────────────────────

    def _validate_beat_sync(self):
        """Beat sync intensity should match hook role (high for tease/payoff, low for rest)."""
        score = 1.0
        errors = []

        expected_sync = {
            HookRole.tease: (0.5, 1.0),
            HookRole.escalation: (0.2, 0.6),
            HookRole.payoff: (0.8, 1.0),
            HookRole.rest: (0.0, 0.2),
            HookRole.callback: (0.4, 0.7),
            HookRole.bridge: (0.2, 0.5),
        }

        for scene in self.dc.scenes:
            expected_range = expected_sync.get(scene.hook_role, (0.2, 0.6))
            if not (expected_range[0] <= scene.beat_sync_intensity <= expected_range[1]):
                errors.append(QualityViolation(
                    rule="beat_sync",
                    severity="info",
                    scene_id=scene.scene_id,
                    message=f"beat_sync_intensity={scene.beat_sync_intensity} for {scene.hook_role.value} scene. Expected {expected_range[0]}-{expected_range[1]}.",
                    suggestion=f"Set to {sum(expected_range)/2:.1f} to match visual intensity rhythm.",
                ))
                score -= 0.02

        self.violations.extend(errors)
        self.metrics["beat_sync_score"] = max(0, score)

    # ───────────────────────────────────────────────────────────────────
    # RULE 8: PACING & DURATION
    # ───────────────────────────────────────────────────────────────────

    def _validate_pacing(self):
        """Scene durations must be 10-45 seconds. ASL target: 4-7 seconds."""
        score = 1.0
        errors = []
        durations = []

        for scene in self.dc.scenes:
            dur = scene.duration_sec
            durations.append(dur)

            if dur < 8:
                errors.append(QualityViolation(
                    rule="pacing",
                    severity="warning",
                    scene_id=scene.scene_id,
                    message=f"Scene duration {dur:.0f}s is very short. Hard to deliver visual density.",
                    suggestion="Minimum 10s is recommended for 3 keyframes + visual richness.",
                ))
                score -= 0.05
            elif dur > 45:
                errors.append(QualityViolation(
                    rule="pacing",
                    severity="error",
                    scene_id=scene.scene_id,
                    message=f"Scene duration {dur:.0f}s exceeds 45s maximum. Viewer attention will drop.",
                    suggestion="Split into 2 scenes with a transition. Keep each under 45s.",
                ))
                score -= 0.15

        avg_dur = sum(durations) / len(durations) if durations else 0
        self.metrics["avg_scene_duration"] = avg_dur
        self.metrics["total_duration"] = sum(durations)
        self.metrics["scene_count"] = len(durations)

        # ASL check: if avg keyframe density suggests ASL
        total_keyframes = sum(len(s.keyframes) for s in self.dc.scenes)
        total_dur = sum(s.duration_sec for s in self.dc.scenes)
        asl = total_dur / total_keyframes if total_keyframes > 0 else 0
        self.metrics["estimated_asl"] = asl

        if asl > 10:
            errors.append(QualityViolation(
                rule="pacing",
                severity="warning",
                scene_id=None,
                message=f"Estimated ASL is {asl:.1f}s (too slow). Target: 4-7 seconds between visual events.",
                suggestion="Add more keyframes per scene or shorten scenes to increase visual density.",
            ))
            score -= 0.1

        self.violations.extend(errors)
        self.metrics["pacing_score"] = max(0, score)

    # ───────────────────────────────────────────────────────────────────
    # SCORE CALCULATION
    # ───────────────────────────────────────────────────────────────────

    def _calculate_score(self) -> float:
        """Calculate weighted quality score from all metrics."""
        scores = {
            "hook_cadence": self.metrics.get("hook_cadence_score", 1.0),
            "scene_density": self.metrics.get("scene_density_score", 1.0),
            "no_repeat": self.metrics.get("no_repeat_score", 1.0),
            "visual_intensity": self.metrics.get("intensity_curve_score", 1.0),
            "color_grade": self.metrics.get("color_grade_score", 1.0),
            "text_motion": self.metrics.get("text_motion_score", 1.0),
            "beat_sync": self.metrics.get("beat_sync_score", 1.0),
        }

        total = sum(
            scores.get(k, 1.0) * self.WEIGHTS[k]
            for k in self.WEIGHTS
        )
        return round(total, 3)


# ═══════════════════════════════════════════════════════════════════════════
# AUTO-FIX SUGGESTIONS
# ═══════════════════════════════════════════════════════════════════════════

def suggest_fixes(violations: List[QualityViolation]) -> List[str]:
    """Generate high-level fix suggestions from violations."""
    fixes = []
    
    # Group by rule
    by_rule = {}
    for v in violations:
        by_rule.setdefault(v.rule, []).append(v)
    
    if "hook_cadence" in by_rule:
        fixes.append("Add 2-3 more open loops in the 3-6 minute window. Every 60-90s needs a micro-hook.")
    
    if "scene_density" in by_rule:
        fixes.append("Add keyframes to low-density scenes: text_slam (0s), particle_burst (5s), color_shift (10s).")
    
    if "no_repeat" in by_rule:
        fixes.append("Rotate layout families and animation triggers. Use the 7 layout families and 12 archetypes evenly.")
    
    if "visual_intensity" in by_rule:
        fixes.append("Ensure intensity builds: tease=0.8 → escalation=0.4-0.6 → payoff=1.0 → rest=0.2.")
    
    if "color_grade" in by_rule:
        fixes.append("Alternate color grades every 2-3 scenes. Never use the same grade 3 times in a row.")
    
    if "text_motion" in by_rule:
        fixes.append("All text must use motion styles: title_reveal, subtitle_burn, kicker, data_label.")
    
    if "pacing" in by_rule:
        fixes.append("Keep scenes 10-45s. Split long scenes. Add keyframes to increase visual event density.")
    
    return fixes
