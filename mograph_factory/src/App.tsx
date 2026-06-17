import React, { useEffect, useState } from 'react';

/**
 * Animation Factory Entry Point
 * Receives render props via a global window.CORTEX_RENDER props object
 * injected by the Playwright capture script.
 */

// Registry of available components (lazy-loaded stubs for Phase 0)
const COMPONENT_REGISTRY: Record<string, React.FC<any>> = {
  'ParticleField': () => <div style={{color:'#14b8a6',fontFamily:'Space Grotesk',padding:40}}>ParticleField: waiting for props</div>,
  'KineticType': () => <div style={{color:'#f4f4f5',fontFamily:'Space Grotesk',padding:40}}>KineticType: waiting for props</div>,
  'BrainSVG': () => <div style={{color:'#f472b6',fontFamily:'Space Grotesk',padding:40}}>BrainSVG: waiting for props</div>,
  'BarRaceChart': () => <div style={{color:'#fbbf24',fontFamily:'Space Grotesk',padding:40}}>BarRaceChart: waiting for props</div>,
  'FloatingCard': () => <div style={{color:'#818cf8',fontFamily:'Space Grotesk',padding:40}}>FloatingCard: waiting for props</div>,
  'StepCard': () => <div style={{color:'#14b8a6',fontFamily:'Space Grotesk',padding:40}}>StepCard: waiting for props</div>,
  'TimerRing': () => <div style={{color:'#fbbf24',fontFamily:'Space Grotesk',padding:40}}>TimerRing: waiting for props</div>,
  'ComparisonBars': () => <div style={{color:'#f4f4f5',fontFamily:'Space Grotesk',padding:40}}>ComparisonBars: waiting for props</div>,
  'NeuralNetwork': () => <div style={{color:'#14b8a6',fontFamily:'Space Grotesk',padding:40}}>NeuralNetwork: waiting for props</div>,
  'ProgressTaskList': () => <div style={{color:'#a1a1aa',fontFamily:'Space Grotesk',padding:40}}>ProgressTaskList: waiting for props</div>,
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
  }
}

const App: React.FC = () => {
  const [props, setProps] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const renderData = window.CORTEX_RENDER;
    if (!renderData) {
      setError('No CORTEX_RENDER props found. This page should be driven by the capture script.');
      return;
    }
    setProps(renderData);
  }, []);

  if (error) {
    return (
      <div style={{width:'100%',height:'100%',display:'flex',alignItems:'center',justifyContent:'center',background:'#0a0e27',color:'#f472b6',fontFamily:'Space Grotesk',fontSize:24}}>
        {error}
      </div>
    );
  }

  if (!props) {
    return (
      <div style={{width:'100%',height:'100%',display:'flex',alignItems:'center',justifyContent:'center',background:'#0a0e27',color:'#14b8a6',fontFamily:'Space Grotesk',fontSize:24}}>
        CORTEX RENDER — Animation Factory Ready
      </div>
    );
  }

  const Component = COMPONENT_REGISTRY[props.componentId];
  if (!Component) {
    return (
      <div style={{width:'100%',height:'100%',display:'flex',alignItems:'center',justifyContent:'center',background:'#0a0e27',color:'#f472b6',fontFamily:'Space Grotesk',fontSize:24}}>
        Unknown component: {props.componentId}
      </div>
    );
  }

  return (
    <div style={{width:props.width,height:props.height,background:'transparent',overflow:'hidden'}}>
      <Component {...props.props} />
    </div>
  );
};

export default App;
