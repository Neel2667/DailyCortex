import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface LightLeakSweepProps {
  colors?: string[];
  direction?: 'left' | 'right';
}

export const LightLeakSweep: React.FC<LightLeakSweepProps> = ({ 
  colors,
  direction = 'left',
}) => {
  const theme = useTheme();
  const sweepColors = colors || [
    theme.color_system.primary,
    theme.color_system.tertiary,
    theme.color_system.secondary,
  ];

  const gradient = `linear-gradient(115deg, transparent 0%, transparent 35%, ${sweepColors[0]}40 45%, ${sweepColors[1]}30 55%, transparent 65%, transparent 100%)`;

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      mixBlendMode: 'screen',
      pointerEvents: 'none',
    }}>
      <motion.div
        initial={{ backgroundPosition: direction === 'left' ? '100% 0' : '-100% 0', opacity: 1 }}
        animate={{ backgroundPosition: direction === 'left' ? '-100% 0' : '100% 0', opacity: 0 }}
        transition={{ duration: 1.4, ease: [0.4, 0, 0.2, 1] }}
        style={{
          width: '100%',
          height: '100%',
          background: gradient,
          backgroundSize: '300% 100%',
        }}
      />
    </div>
  );
};

export default LightLeakSweep;
