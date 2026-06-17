# CORTEX RENDER — The Hook Cadence System

> This is the **most important design document** in the project. It defines how the engine creates narrative tension that keeps viewers watching to the end. Read this before building any module.

---

## The Core Insight

**Pure "fast cuts + no dead air" gets 60% retention. Nested open loops (curiosity gaps) get 80%+ retention.**

The most successful documentary channels (Psych2Go, BE AMAZED, Top Fives, Bright Side) don't just cut fast. They create a **rhythm of curiosity** that keeps the viewer's brain constantly asking "what happens next?"

This is based on:
- **George Loewenstein's Information Gap Theory** — curiosity is an aversive state like hunger; we must close gaps
- **The Zeigarnik Effect** — uncompleted tasks are remembered better than completed ones
- **Dopamine Anticipation** — dopamine releases during anticipation, not reward

---

## The Three-Layer Hook System

Every 8–10 minute video must contain **5–7 nested open loops** (curiosity gaps) at three time scales.

### 1. Micro-Hooks (Every 15–30 Seconds)

**What:** A single sentence or visual element that raises a micro-question.

**Script Example:**
> "But here's the problem — your brain doesn't know the difference between scrolling Instagram and winning a lottery."

**Visual Match:** Sudden cut to a brain scan lighting up, or a split-screen comparison animation.

**Implementation:** Every scene contains 2–4 `keyframes` that are micro-hooks. The `visual_action` must create a "snap" of attention.

```json
{
  "keyframes": [
    {"at_sec": 0, "visual_action": "text_slam", "element": "provocative_question"},
    {"at_sec": 8, "visual_action": "split_screen_compare", "element": "instagram_vs_lottery"},
    {"at_sec": 15, "visual_action": "counter_tick_start", "element": "live_statistic"}
  ]
}
```

**Visual Intensity for Micro-Hooks:** 0.6–0.8

---

### 2. Medium Hooks (Every 60–90 Seconds)

**What:** A bigger open loop that won't pay off for 2–3 minutes.

**Script Example:**
> "There's one brain region that makes this decision for you. And if you know how to hack it, you'll never procrastinate again. We'll get to that in a minute. First, let me show you why willpower is a myth."

**Visual Match:** Full visual reset — new layout family, new color grade, dramatic typography entrance. The scene becomes visually different from what came before, signaling "something important is coming."

**Implementation:** The `hook_role` field is `tease` for the opening scene, and `escalation` for scenes that build toward the payoff. The `visual_intensity` gradually rises from 0.3 to 0.7.

```json
{
  "scene_id": "S03",
  "hook_role": "tease",
  "visual_intensity": 0.8,
  "narration": "There's one brain region... We'll get to that in a minute."
}
```

---

### 3. Big Hooks / Cliffhangers (Every 3–4 Minutes)

**What:** The major revelation that the entire chapter has been building toward.

**Script Example:**
> "Remember that 2-minute rule I mentioned at the start? It works because of something called 'task initiation energy' — and once I explain this, you'll understand why every productivity app you've ever used was wrong."

**Visual Match:** The most intense animation in the chapter. Full-screen takeover. Beat-synced pulse. Color grade shifts to `revelatory` or `euphoric`. All animation systems fire simultaneously.

**Implementation:** The payoff scene has `hook_role: "payoff"` and `visual_intensity: 1.0`. It should close 2–3 open loops simultaneously for maximum dopamine release.

```json
{
  "scene_id": "S22",
  "hook_role": "payoff",
  "visual_intensity": 1.0,
  "narration": "The 2-Minute Initiation Protocol. Here's how it works."
}
```

---

## The Open Loop Script Template (The Golden Structure)

This is the **exact narrative structure** the Groq Director must produce for every video. It is not a suggestion. It is a constraint.

```
OPEN LOOP 1 (The Big Promise): [0:00]
"There's a 2-minute brain hack that makes procrastination impossible. 
I'm going to show you exactly how it works, but first you need to understand 
why your brain is wired to sabotage you."
→ LOOP 1 stays open until 7:30 (the hack reveal)

OPEN LOOP 2 (The Science Mystery): [0:45]
"Scientists at MIT discovered that this isn't about willpower. 
It's about something called 'dopamine prediction error.'"
→ LOOP 2 stays open until 2:30 (the brain scan reveal)

OPEN LOOP 3 (The Stat Shock): [2:30]
"One in five adults are chronic procrastinators. But that's not the scary number. 
The scary number is what happens after 24 hours of avoidance."
→ LOOP 3 stays open until 4:00 (the neural pathway animation)

OPEN LOOP 4 (The Paradox): [4:00]
"Here's the paradox: the more you tell yourself 'I need to focus,' 
the less you actually focus. Why? Because your prefrontal cortex 
and your amygdala are in a literal tug-of-war."
→ LOOP 4 stays open until 6:00 (the trick reveal)

OPEN LOOP 5 (The Trick Tease): [6:00]
"It's called the '2-Minute Initiation Protocol.' Not the 5-minute rule. Not the Pomodoro. 
Two minutes. And it works because it bypasses the amygdala entirely."
→ LOOP 5 stays open until 7:30 (the protocol reveal + demo)

CLOSURE 1: [7:30] — ALL LOOPS CLOSE AT ONCE. Dopamine payoff.
"The 2-Minute Initiation Protocol. Here's how it works. Step 1..."
→ LOOP 1, 4, and 5 all close here. This is the dopamine cascade moment.

CLOSURE 2: [8:30] — Emotional resolution + CTA
"Try it right now. Pick one task you've been avoiding. Set a timer for 2 minutes. 
That's it. Just start. Because action doesn't follow motivation — motivation follows action."

CLOSURE 3: [9:15] — Next video hook (session continuation)
"Next week: Why your first instinct is usually wrong — and how to hack your intuition."
→ Drives session continuation (algorithm's #1 signal)
```

### The Viewer Experience

| Time | State | Why They Keep Watching |
|------|-------|------------------------|
| 0:00 | "There's a hack? I need to know." | Open Loop 1 opened |
| 0:45 | "Dopamine prediction error? What's that?" | Open Loop 2 opened |
| 2:30 | "Scary number? What happens after 24 hours?" | Open Loop 3 opened |
| 4:00 | "The paradox? Why does focusing make it worse?" | Open Loop 4 opened |
| 6:00 | "The 2-minute protocol? How does it bypass the amygdala?" | Open Loop 5 opened |
| 7:30 | **ALL LOOPS CLOSE AT ONCE.** | Dopamine cascade. Massive satisfaction. |
| 8:30 | "I should try this." | Emotional resolution + CTA |
| 9:15 | "Next video sounds interesting." | Session continuation |

**The viewer has 5 open questions and needs the answers. This is why they watch to the end.**

---

## The Visual Tension Curve

The Compositor maps `visual_intensity` to `hook_role` to create a visual rhythm that matches the narrative tension.

```
Narrative Tension:  ██████░░░░░░████████░░░░░░████████░░░░░░████████████
Visual Intensity:  ███░░░░░██░░░░░░███░░░██░░░░░░███░░░██░░░░░░░███████
Beat Sync Intensity: ▲░░▲░░▲▲░░▲░░▲░▲▲░░▲░░▲▲░░▲░░▲░▲▲░░▲░░▲▲░░▲░▲▲▲▲▲▲▲
```

### Rules for Visual Tension

1. **Visual intensity rises BEFORE narrative payoff.** The animation starts building 5 seconds before the narrator says the payoff line.
2. **At the hook tease, the visual "stretches":** slow motion, longer takes, bigger text. This creates tension.
3. **At the hook payoff, the visual "snaps":** fast cuts, particle bursts, color grade shifts, beat drops.
4. **Between hooks, visual intensity rests:** ambient particles, slow drift, breathing text. But NEVER to zero.

### Mapping Table

| Hook Role | Visual Intensity | Beat Sync Intensity | Visual Behavior |
|-----------|-----------------|---------------------|-----------------|
| `tease` | 0.8 | 0.6 | Immediate impact, full-screen kinetic text, particle burst |
| `escalation` | 0.3 → 0.6 | 0.2 → 0.5 | Slow build, longer takes, bigger text, tension mounting |
| `payoff` | 1.0 | 0.9 | All animation systems fire, fastest cuts, color shift, beat drop |
| `rest` | 0.2 | 0.1 | Ambient particles, slow drift, breathing text — alive but calm |
| `callback` | 0.7 | 0.5 | Nostalgic reference to earlier hook, visual echo with escalation |

---

## The Groq Prompt Engineering (Pass 2)

The Director's Cut Pass 2 prompt must be rewritten to force this Hook Cadence structure. The LLM must:

1. **Identify 5–7 open loops** BEFORE writing any scene descriptions
2. **Map the tension arc** — which scenes escalate, which scenes pay off
3. **Assign `hook_role` and `visual_intensity`** to each scene
4. **Place micro-hooks** at 15–30 second intervals within scenes (via `keyframes`)
5. **Only THEN generate** the scene list with narration, visual keywords, and archetypes

### System Prompt Addition (Mandatory)

```
You are a cinematic director AI. Before generating any scene list, you MUST:

1. Write 5–7 OPEN LOOPS for this video. Each loop must have:
   - A tease line (question, promise, or mystery)
   - A tease timestamp (when it first appears)
   - A payoff line (the answer or revelation)
   - A payoff timestamp (when it resolves, 2–5 minutes later)

2. Map the TENSION ARC:
   - Which scenes are TEASES (open a loop)?
   - Which scenes are ESCALATIONS (build tension)?
   - Which scenes are PAYOFFS (close a loop)?
   - Which scenes are RESTS (let the viewer breathe)?

3. Assign VISUAL INTENSITY (0.0–1.0) to each scene based on its hook role:
   - Tease: 0.8
   - Escalation: 0.3–0.6 (rising)
   - Payoff: 1.0
   - Rest: 0.2

4. Place MICRO-HOOKS within scenes:
   - Every 15–30 seconds, a keyframe that creates a visual "snap"
   - At 0 sec: text slam or particle burst
   - At 5–8 sec: new data element or comparison
   - At 10–15 sec: live counter or animation trigger
   - At 15–20 sec: transition buildup or light leak

5. Include a CALLBACK REFERENCE at the end that references the intro hook.

ONLY after completing steps 1–5 should you generate the scene list.
```

---

## The Pattern Interrupt as a Hook Device

Every time the viewer's brain starts to habituate to the visual style, a **pattern interrupt** occurs. But the pattern interrupt IS the hook — it is not random.

| Time | Hook Type | Pattern Interrupt | Why It Works |
|------|-----------|---------------------|--------------|
| 0:00 | Big Promise | Full-screen kinetic text, no intro | Instant dopamine anticipation |
| 0:45 | Science Mystery | Cut to footage + lower third (was full text before) | Brain goes "new information channel" |
| 2:30 | Stat Shock | Giant number slam + live counter (was calm explanation before) | Surprise + curiosity |
| 4:00 | Paradox | Split screen: "MYTH" vs "TRUTH" (was single POV before) | Cognitive dissonance creates engagement |
| 6:00 | Trick Tease | Step card animation (was brain scans before) | Practical promise shifts brain to "how do I use this?" |
| 7:30 | **PAYOFF** | All animation systems fire simultaneously | Dopamine release = satisfaction + share impulse |

**Rule:** The pattern interrupt must be triggered by the script's hook structure, not by a random timer. The visual system serves the narrative, not the other way around.

---

## The Internal Keyframe System

Every scene must have **3–4 internal visual micro-changes** within its 10–25 second duration. These are not scene transitions. They are keyframe events that keep the scene alive.

### Keyframe JSON Schema
```json
{
  "keyframes": [
    {
      "at_sec": 0.0,
      "visual_action": "text_slam",
      "element": "hero_title",
      "description": "Big text slams into center screen with spring physics"
    },
    {
      "at_sec": 5.0,
      "visual_action": "data_enter",
      "element": "stat_counter",
      "description": "A number starts ticking up from 0 to target value"
    },
    {
      "at_sec": 10.0,
      "visual_action": "overlay_pulse",
      "element": "brain_scan_glow",
      "description": "Brain region lights up with a pulse ring"
    },
    {
      "at_sec": 15.0,
      "visual_action": "text_shift",
      "element": "subtitle",
      "description": "Subtitle moves from center to lower third, new text enters"
    }
  ]
}
```

### Visual Action Types

| Action | Description | When to Use |
|--------|-------------|-------------|
| `text_slam` | Text enters with spring physics, full screen | Scene open, hook tease |
| `data_enter` | Chart element, number, or bar grows from zero | Evidence scenes |
| `overlay_pulse` | Motion graphic element flashes or glows | Brain scans, neural networks |
| `text_shift` | Text moves position, new text replaces old | Mid-scene transition |
| `counter_tick` | Number ticks up rapidly | Stat shock, live data |
| `comparison_reveal` | Second half of comparison appears | Myth bust, before/after |
| `particle_burst` | Particle system temporarily increases velocity | Energy spikes, beat drops |
| `color_shift` | Subtle color grade changes within scene | Mood shifts, escalations |
| `zoom_in` | Camera zooms into a detail | Focus moments, reveals |
| `zoom_out` | Camera pulls back for big picture | Payoff moments, summaries |
| `icon_appear` | Icon or badge pops in with bounce | Step reveals, checklists |
| `line_draw` | SVG path draws itself on screen | Timelines, neural connections |
| `split_open` | Split screen opens from center | Comparisons, before/after |
| `fade_swap` | Crossfade between two visual states | Data updates, state changes |

---

## The Callback System

At the end of the video, the script must **reference an earlier hook** to create a "memory loop." This is not just a CTA. It is a psychological device.

**Script Example:**
> "Remember when I said your brain doesn't know the difference between Instagram and a lottery? That's the same mechanism we're going to hack next week."

**Visual Match:** The exact visual from the intro hook (the split screen) briefly flashes, then morphs into the "next video" teaser.

**Implementation:** The `callback_reference` field in the `DirectorCut` contains the text of the original hook. The final scene's `animation_trigger` is a `CallbackMorph` component that transitions from the old visual to the new teaser.

---

## Why This Is Better Than Pure "Fast Cuts"

| Approach | Viewer Feel | Retention Curve | Algorithm Result |
|----------|-------------|-----------------|------------------|
| **Fast cuts only** | "This is energetic but... why am I watching?" | High at 0:30, crash at 2:00 | 40% AVD, low satisfaction |
| **One hook at start** | "Great start, then... nothing?" | Spike at 0:30, flatline at 3:00 | 50% AVD, mid satisfaction |
| **Hook cadence (ours)** | "I HAVE to know the answer." | Steady rise, peak at payoff | 70%+ AVD, high satisfaction, high session continuation |

---

## Implementation Checklist for Next AI

- [ ] Extend `app/models.py` `Scene` with `hook_role`, `visual_intensity`, `keyframes`, `micro_hooks`
- [ ] Extend `app/models.py` `DirectorCut` with `hook_cadence` (open_loops, micro_hooks, callback_reference)
- [ ] Rewrite `app/brain.py` Pass 2 system prompt to force Hook Cadence generation before scenes
- [ ] Add `visual_intensity` to `compositor.py` beat sync mapping (higher intensity = more sync events)
- [ ] Add `keyframes` to `compositor.py` scene rendering (generate internal micro-changes via FFmpeg)
- [ ] Build `Keyframe` React components in Animation Factory (text_slam, data_enter, overlay_pulse, etc.)
- [ ] Test: Generate a full Director's Cut JSON and validate that it contains 5–7 open loops
- [ ] Test: Generate a 10-minute video and check that every scene has 3–4 keyframes
- [ ] Test: Verify that no two consecutive scenes share the same hook_role (tease → escalation → payoff → rest → tease)

---

*This document is the soul of the project. Everything else is infrastructure. Build this right, and the videos will be addictive. Build this wrong, and no amount of fast cuts will save them.*
