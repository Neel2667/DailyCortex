import React from 'react';
import { useTheme } from './ThemeProvider';

interface MeshGradientProps {
  stops?: string[];
  duration?: number;
  drift?: boolean;
}

export const MeshGradient: React.FC<MeshGradientProps> = ({ 
  stops,
  duration = 25,
  drift = true
}) => {
  const theme = useTheme();
  const colors = stops || [
    theme.color_system.primary,
    theme.color_system.secondary,
    theme.color_system.tertiary,
  ];

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      zIndex: 2,
      overflow: 'hidden',
      background: theme.color_system.void,
    }}>
      <svg 
        viewBox="0 0 800 450" 
        preserveAspectRatio="xMidYMid slice"
        style={{ width: '100%', height: '100%', filter: 'blur(50px)' }}
      >
        <defs>
          {colors.map((color, i) => (
            <radialGradient 
              key={i} 
              id={`mesh-${i}`} 
              cx={`${20 + i * 30}%`} 
              cy={`${30 + i * 20}%`} 
              r="55%"
            >
              <stop offset="0%" stopColor={color} stopOpacity={i === 0 ? 0.4 : 0.3} />
              <stop offset="100%" stopColor={color} stopOpacity="0" />
            </radialGradient>
          ))}
        </defs>
        {drift && (
          <style>{`
            @keyframes meshDrift {
              from { transform: translate(0,0) rotate(0deg) scale(1); }
              to { transform: translate(3%,-2%) rotate(4deg) scale(1.05); }
            }
            .mesh-drift { animation: meshDrift ${duration}s ease-in-out infinite alternate; }
          `}</style>
        )}
        <g className={drift ? 'mesh-drift' : ''}>
          <rect width="800" height="450" fill={theme.color_system.void} />
          {colors.map((_, i) => (
            <rect key={i} width="800" height="450" fill={`url(#mesh-${i})`} />
          ))}
        </g>
      </svg>
    </div>
  );
};

export default MeshGradient;
