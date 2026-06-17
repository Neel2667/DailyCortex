import React, { useEffect, useState } from 'react';
import { ThemeProvider, ThemeContextType } from './components/ThemeProvider';

// Lazy loaded real components (available when built)
import ParticleField from './components/ParticleField';
import QuestionBomb from './components/QuestionBomb';
import StatShock from './components/StatShock';
import BrainSVG from './components/BrainSVG';
import StepCard from './components/StepCard';
import KineticType from './components/KineticType';
import MeshGradient from './components/MeshGradient';
import ComparisonSplit from './components/ComparisonSplit';
import FloatingCard from './components/FloatingCard';

// Registry of all available components
const COMPONENT_REGISTRY: Record<string, React.FC<any>> = {
  'ParticleField': ParticleField,
  'QuestionBomb': QuestionBomb,
  'StatShock': StatShock,
  'BrainSVG': BrainSVG,
  'StepCard': StepCard,
  'KineticType': KineticType,
  'MeshGradient': MeshGradient,
  'ComparisonSplit': ComparisonSplit,
  'FloatingCard': FloatingCard,
  // Stubs for components not yet built
  'BarRaceChart': () => <div style={{ color: '#fbbf24', fontFamily: 'Space Grotesk', padding: 40 }}>BarRaceChart: building</div>,
  'NeuralNetwork': () => <div style={{ color: '#14b8a6', fontFamily: 'Space Grotesk', padding: 40 }}>NeuralNetwork: building</div>,
  'ProgressTaskList': () => <div style={{ color: '#a1a1aa', fontFamily: 'Space Grotesk', padding: 40 }}>ProgressTaskList: building</div>,
  'TimerRing': () => <div style={{ color: '#fbbf24', fontFamily: 'Space Grotesk', padding: 40 }}>TimerRing: building</div>,
  'ActionPill': () => <div style={{ color: '#14b8a6', fontFamily: 'Space Grotesk', padding: 40 }}>ActionPill: building</div>,
  'FlourishLines': () => <div style={{ color: '#f4f4f5', fontFamily: 'Space Grotesk', padding: 40 }}>FlourishLines: building</div>,
  'LightLeakSweep': () => <div style={{ color: '#818cf8', fontFamily: 'Space Grotesk', padding: 40 }}>LightLeakSweep: building</div>,
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

// Demo mode: rotate through all components
const DEMO_COMPONENTS = [
  { id: 'QuestionBomb', props: { question: "Why do you procrastinate?", accent_words: ["procrastinate"] }, duration: 4000 },
  { id: 'StatShock', props: { number: "1", suffix: "/5", caption: "adults are chronic procrastinators", context: "That's roughly 1.4 billion people" }, duration: 4000 },
  { id: 'BrainSVG', props: { active_regions: ['prefrontal', 'amygdala'], show_labels: true }, duration: 4000 },
  { id: 'ComparisonSplit', props: { leftLabel: "Low Dopamine", rightLabel: "Healthy Brain", leftValue: 85, rightValue: 25, unit: "%" }, duration: 4000 },
  { id: 'StepCard', props: { steps: [
    { number: 1, title: "Pick the task", description: "The one you've been avoiding all day." },
    { number: 2, title: "Set 2 minutes", description: "Promise yourself: just two minutes." },
    { number: 3, title: "Just begin", description: "Action creates motivation." },
  ]}, duration: 4000 },
  { id: 'KineticType', props: { text: "Start now. Just two minutes.", style: 'title', position: 'center' }, duration: 3000 },
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
      }}>
        CORTEX RENDER — Animation Factory Ready
        <br />
        <span style={{ fontSize: 14, color: '#a1a1aa', marginTop: 12 }}>
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
