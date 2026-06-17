import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface GlitchTextProps {
  text: string;
  intensity?: 'low' | 'medium' | 'high';
}

export const GlitchText: React.FC<GlitchTextProps> = ({ 
  text = "SYSTEM OVERRIDE",
  intensity = 'medium',
}) => {
  const theme = useTheme();
  
  const glitchKeyframes = {
    low: ['0%', '2%', '-1%', '0%', '1%', '0%'],
    medium: ['0%', '5%', '-3%', '2%', '-4%', '0%', '3%', '0%'],
    high: ['0%', '8%', '-5%', '3%', '-7%', '2%', '-6%', '0%', '4%', '0%'],
  };

  const offsets = glitchKeyframes[intensity];

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: theme.color_system.void,
      fontFamily: theme.typography.headline,
    }}>
      <div style={{ position: 'relative', textAlign: 'center' }}>
        {/* Main text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.1 }}
          style={{
            fontSize: 'clamp(48px, 6vw, 96px)',
            fontWeight: 600,
            letterSpacing: '0.05em',
            color: theme.color_system.text,
            textTransform: 'uppercase',
          }}
        >
          {text}
        </motion.div>

        {/* Glitch layers */}
        {[
          { color: theme.color_system.primary, offset: -2 },
          { color: theme.color_system.secondary, offset: 2 },
        ].map((layer, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0 }}
            animate={{
              opacity: [0, 0.8, 0, 0.6, 0, 0.9, 0],
              x: offsets.map(o => parseFloat(o) * layer.offset),
            }}
            transition={{ duration: 1.5, delay: 0.5 + i * 0.1, repeat: 0 }}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              fontSize: 'clamp(48px, 6vw, 96px)',
              fontWeight: 600,
              letterSpacing: '0.05em',
              color: layer.color,
              textTransform: 'uppercase',
              mixBlendMode: 'screen',
              pointerEvents: 'none',
              clipPath: 'inset(0 0 50% 0)',
            }}
          >
            {text}
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default GlitchText;
