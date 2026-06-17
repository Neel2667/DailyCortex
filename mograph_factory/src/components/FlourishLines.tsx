import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface FlourishLinesProps {
  color?: string;
}

export const FlourishLines: React.FC<FlourishLinesProps> = ({ color }) => {
  const theme = useTheme();
  const accentColor = color || theme.color_system.primary;

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: theme.color_system.void,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 1.7, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          style={{
            width: 80,
            height: 1,
            background: accentColor,
            opacity: 0.5,
            transformOrigin: 'right center',
          }}
        />
        <motion.div
          initial={{ opacity: 0, scale: 0, rotate: 0 }}
          animate={{ opacity: 1, scale: 1, rotate: 45 }}
          transition={{ delay: 1.9, duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            width: 10,
            height: 10,
            background: accentColor,
            boxShadow: `0 0 20px ${accentColor}`,
          }}
        />
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 1.85, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          style={{
            width: 80,
            height: 1,
            background: accentColor,
            opacity: 0.5,
            transformOrigin: 'left center',
          }}
        />
      </div>
    </div>
  );
};

export default FlourishLines;
