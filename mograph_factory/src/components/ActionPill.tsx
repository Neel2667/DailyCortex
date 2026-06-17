import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface ActionPillProps {
  pills?: Array<{ text: string; color?: string }>;
}

export const ActionPill: React.FC<ActionPillProps> = ({ 
  pills = [
    { text: "Subscribe" },
    { text: "Try it today" },
  ]
}) => {
  const theme = useTheme();
  
  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 20,
      background: theme.color_system.void,
    }}>
      {pills.map((pill, i) => {
        const pillColor = pill.color || (i === 0 ? theme.color_system.primary : theme.color_system.secondary);
        return (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1.4 + i * 0.2, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 10,
              padding: '12px 24px',
              background: `${pillColor}12`,
              border: `1px solid ${pillColor}30`,
              borderRadius: 999,
              fontFamily: theme.typography.headline,
              fontSize: 13,
              fontWeight: 500,
              letterSpacing: '0.18em',
              textTransform: 'uppercase',
              color: pillColor,
              animation: `pulsePill 2s ease-in-out ${2 + i * 0.5}s infinite`,
            }}
          >
            <span style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: pillColor,
              boxShadow: `0 0 12px ${pillColor}`,
              animation: 'pulse 1.5s ease-in-out infinite',
            }} />
            {pill.text}
          </motion.div>
        );
      })}
      <style>{`
        @keyframes pulsePill { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.4); } }
      `}</style>
    </div>
  );
};

export default ActionPill;
