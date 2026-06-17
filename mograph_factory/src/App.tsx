import React, { useEffect, useState } from 'react';
import { ThemeProvider, ThemeContextType } from './components/ThemeProvider';

// ─── Foundation Layers ───
import ParticleField from './components/ParticleField';
import MeshGradient from './components/MeshGradient';

// ─── Hook Archetypes ───
import QuestionBomb from './components/QuestionBomb';
import StatShock from './components/StatShock';

// ─── Evidence Archetypes ───
import BrainSVG from './components/BrainSVG';
import ComparisonSplit from './components/ComparisonSplit';
import BarRaceChart from './components/BarRaceChart';
import NeuralNetwork from './components/NeuralNetwork';

// ─── Action Archetypes ───
import StepCard from './components/StepCard';
import KineticType from './components/KineticType';
import TimerRing from './components/TimerRing';
import ProgressTaskList from './components/ProgressTaskList';

// ─── Payoff Archetypes ───
import ActionPill from './components/ActionPill';
import FloatingCard from './components/FloatingCard';
import FlourishLines from './components/FlourishLines';

// ─── Decorative & Transitions ───
import LightLeakSweep from './components/LightLeakSweep';
import GlitchText from './components/GlitchText';

// Registry of all available components for the Animation Factory
const COMPONENT_REGISTRY: Record<string, React.FC<any>> = {
  // Foundation
  'ParticleField': ParticleField,
  'MeshGradient': MeshGradient,

  // Hook Archetypes
  'QuestionBomb': QuestionBomb,
  'StatShock': StatShock,

  // Evidence Archetypes
  'BrainSVG': BrainSVG,
  'ComparisonSplit': ComparisonSplit,
  'BarRaceChart': BarRaceChart,
  'NeuralNetwork': NeuralNetwork,

  // Action Archetypes
  'StepCard': StepCard,
  'KineticType': KineticType,
  'TimerRing': TimerRing,
  'ProgressTaskList': ProgressTaskList,

  // Payoff Archetypes
  'ActionPill': ActionPill,
  'FloatingCard': FloatingCard,
  'FlourishLines': FlourishLines,

  // Decorative & Transitions
  'LightLeakSweep': LightLeakSweep,
  'GlitchText': GlitchText,
};

declare global {
  interface Window {
    CORTEX_RENDER?: {
      componentId: string;
      props: any;
      durationMs: number;
      width: number;
      height: number;
      fps: number;
    };
    CORTEX_DEMO?: boolean;
  }
}

const defaultTheme: ThemeContextType = {
  color_system: {
    void: '#0a0e27',
    primary: '#14b8a6',
    secondary: '#f472b6',
    tertiary: '#818cf8',
    accent: '#fbbf24',
    text: '#f4f4f5',
    text_dim: '#a1a1aa',
  },
  typography: {
    headline: 'Space Grotesk, sans-serif',
    body: 'Inter, sans-serif',
    accent_font: 'Fraunces, serif',
  },
  motion_language: {
    easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
    stagger_base: 0.15,
    particle_density: 130,
    grid_opacity: 0.025,
    grain_intensity: 0.06,
  },
};

// Demo mode: rotate through all components for visual testing
const DEMO_COMPONENTS = [
  { id: 'QuestionBomb', props: { question: "Why do you procrastinate?", accent_words: ["procrastinate"] }, duration: 4000 },
  { id: 'StatShock', props: { number: "1", suffix: "/5", caption: "adults are chronic procrastinators", context: "That's roughly 1.4 billion people" }, duration: 4000 },
  { id: 'BrainSVG', props: { active_regions: ['prefrontal', 'amygdala'], show_labels: true }, duration: 4000 },
  { id: 'ComparisonSplit', props: { leftLabel: "Low Dopamine", rightLabel: "Healthy Brain", leftValue: 85, rightValue: 25, unit: "%" }, duration: 4000 },
  { id: 'BarRaceChart', props: { data: [
    { label: "Dopamine", value: 85 },
    { label: "Serotonin", value: 62 },
    { label: "Cortisol", value: 78 },
    { label: "Oxytocin", value: 45 },
    { label: "Endorphin", value: 70 },
  ], title: "Neurotransmitter Levels" }, duration: 4000 },
  { id: 'NeuralNetwork', props: { nodes: 12, connections: 20 }, duration: 4000 },
  { id: 'StepCard', props: { steps: [
    { number: 1, title: "Pick the task", description: "The one you've been avoiding all day." },
    { number: 2, title: "Set 2 minutes", description: "Promise yourself: just two minutes." },
    { number: 3, title: "Just begin", description: "Action creates motivation." },
  ]}, duration: 4000 },
  { id: 'TimerRing', props: { duration: 120, label: "timer starts" }, duration: 3000 },
  { id: 'ProgressTaskList', props: { tasks: [
    { icon: "✉", text: "Reply to important emails", progress: 15 },
    { icon: "📋", text: "File taxes", progress: 35 },
    { icon: "🏥", text: "Schedule doctor visit", progress: 65 },
    { icon: "💪", text: "Start exercise routine", progress: 90 },
  ]}, duration: 4000 },
  { id: 'ActionPill', props: { pills: [{ text: "Subscribe" }, { text: "Try it today" }] }, duration: 3000 },
  { id: 'KineticType', props: { text: "Start now. Just two minutes.", style: 'title', position: 'center' }, duration: 3000 },
  { id: 'FloatingCard', props: { label: "Cognitive Load", value: "↑ 47%", sub: "during stress" }, duration: 3000 },
  { id: 'FlourishLines', props: {}, duration: 3000 },
  { id: 'GlitchText', props: { text: "SYSTEM OVERRIDE", intensity: 'medium' }, duration: 3000 },
  { id: 'LightLeakSweep', props: { direction: 'left' }, duration: 3000 },
  { id: 'MeshGradient', props: {}, duration: 4000 },
  { id: 'ParticleField', props: { count: 130 }, duration: 4000 },
];

const App: React.FC = () => {
  const [props, setProps] = useState<any>(null);
  const [demoIndex, setDemoIndex] = useState(0);
  const [isDemo, setIsDemo] = useState(false);

  useEffect(() => {
    const renderData = window.CORTEX_RENDER;
    if (renderData) {
      setProps(renderData);
      return;
    }

    // Auto demo mode if no props injected
    if (window.CORTEX_DEMO !== false) {
      setIsDemo(true);
      setProps({
        componentId: DEMO_COMPONENTS[0].id,
        props: DEMO_COMPONENTS[0].props,
        width: 1920,
        height: 1080,
      });
    }
  }, []);

  useEffect(() => {
    if (!isDemo) return;
    const timer = setInterval(() => {
      setDemoIndex(prev => {
        const next = (prev + 1) % DEMO_COMPONENTS.length;
        const comp = DEMO_COMPONENTS[next];
        setProps({
          componentId: comp.id,
          props: comp.props,
          width: 1920,
          height: 1080,
        });
        return next;
      });
    }, 4000);
    return () => clearInterval(timer);
  }, [isDemo]);

  if (!props) {
    return (
      <div style={{
        width: 1920, height: 1080,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: '#0a0e27', color: '#14b8a6',
        fontFamily: 'Space Grotesk, sans-serif', fontSize: 24,
        flexDirection: 'column',
        gap: 12,
      }}>
        CORTEX RENDER — Animation Factory Ready
        <span style={{ fontSize: 14, color: '#a1a1aa' }}>
          Set window.CORTEX_RENDER to render a component, or append ?demo=1 to auto-cycle
        </span>
      </div>
    );
  }

  const Component = COMPONENT_REGISTRY[props.componentId];
  if (!Component) {
    return (
      <div style={{
        width: 1920, height: 1080,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: '#0a0e27', color: '#f472b6',
        fontFamily: 'Space Grotesk, sans-serif', fontSize: 24,
      }}>
        Unknown component: {props.componentId}
      </div>
    );
  }

  return (
    <ThemeProvider theme={defaultTheme}>
      <div style={{ width: 1920, height: 1080, position: 'relative', overflow: 'hidden', background: '#0a0e27' }}>
        <Component {...props.props} />
        {isDemo && (
          <div style={{
            position: 'absolute', bottom: 20, left: 20, zIndex: 100,
            padding: '8px 16px', background: 'rgba(0,0,0,0.5)',
            borderRadius: 8, fontFamily: 'Space Grotesk, sans-serif',
            fontSize: 12, color: '#a1a1aa', letterSpacing: '0.1em',
            border: '1px solid rgba(255,255,255,0.08)',
          }}>
            DEMO MODE: {props.componentId} ({demoIndex + 1}/{DEMO_COMPONENTS.length})
            <br />
            <span style={{ color: '#14b8a6' }}>CORTEX RENDER — Animation Factory</span>
          </div>
        )}
      </div>
    </ThemeProvider>
  );
};

export default App;
