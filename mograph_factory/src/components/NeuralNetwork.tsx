import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface NeuralNetworkProps {
  nodes?: number;
  connections?: number;
}

export const NeuralNetwork: React.FC<NeuralNetworkProps> = ({ 
  nodes = 12,
  connections = 20,
}) => {
  const theme = useTheme();
  const w = 1920;
  const h = 1080;

  // Generate random node positions
  const nodePositions = Array.from({ length: nodes }, (_, i) => ({
    id: i,
    x: 200 + (i % 4) * 400 + (Math.random() - 0.5) * 100,
    y: 200 + Math.floor(i / 4) * 250 + (Math.random() - 0.5) * 100,
  }));

  // Generate connections between nearby nodes
  const connectionPairs = Array.from({ length: connections }, (_, i) => {
    const a = Math.floor(Math.random() * nodes);
    let b = Math.floor(Math.random() * nodes);
    while (b === a) b = Math.floor(Math.random() * nodes);
    return { a, b, delay: i * 0.15 };
  });

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      background: theme.color_system.void,
      overflow: 'hidden',
    }}>
      <svg width="100%" height="100%" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="xMidYMid slice">
        <defs>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <linearGradient id="connectionGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={theme.color_system.primary} />
            <stop offset="100%" stopColor={theme.color_system.tertiary} />
          </linearGradient>
        </defs>

        {/* Connection lines */}
        {connectionPairs.map((conn, i) => {
          const na = nodePositions[conn.a];
          const nb = nodePositions[conn.b];
          return (
            <line
              key={i}
              x1={na.x} y1={na.y}
              x2={nb.x} y2={nb.y}
              stroke="url(#connectionGrad)"
              strokeWidth="1"
              opacity="0.4"
            >
              <animate attributeName="opacity" values="0.1;0.8;0.1" dur={`${2 + (i % 3)}s`} begin={`${conn.delay}s`} repeatCount="indefinite" />
            </line>
          );
        })}

        {/* Nodes */}
        {nodePositions.map((node, i) => (
          <g key={node.id}>
            <circle cx={node.x} cy={node.y} r="6" fill={theme.color_system.primary} filter="url(#glow)" opacity="0.6">
              <animate attributeName="r" values="4;8;4" dur={`${2.5 + (i % 3) * 0.5}s`} begin={`${i * 0.2}s`} repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.4;1;0.4" dur={`${2.5 + (i % 3) * 0.5}s`} begin={`${i * 0.2}s`} repeatCount="indefinite" />
            </circle>
            <circle cx={node.x} cy={node.y} r="2" fill={theme.color_system.text} opacity="0.8" />
          </g>
        ))}

        {/* Animated data packets */}
        {connectionPairs.slice(0, 8).map((conn, i) => {
          const na = nodePositions[conn.a];
          const nb = nodePositions[conn.b];
          return (
            <circle key={`packet-${i}`} r="3" fill={theme.color_system.accent} opacity="0.8">
              <animateMotion
                dur={`${1.5 + i * 0.3}s`}
                repeatCount="indefinite"
                begin={`${i * 0.4}s`}
              >
                <mpath href={`#path-${i}`} />
              </animateMotion>
            </circle>
          );
        })}
        
        {/* Define paths for packets */}
        {connectionPairs.slice(0, 8).map((conn, i) => {
          const na = nodePositions[conn.a];
          const nb = nodePositions[conn.b];
          return (
            <path key={`path-${i}`} id={`path-${i}`} d={`M ${na.x} ${na.y} L ${nb.x} ${nb.y}`} fill="none" stroke="none" />
          );
        })}
      </svg>
    </div>
  );
};

export default NeuralNetwork;
