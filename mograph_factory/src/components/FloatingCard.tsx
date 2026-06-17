import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface FloatingCardProps {
  label: string;
  value: string;
  sub?: string;
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  accent?: boolean;
}

export const FloatingCard: React.FC<FloatingCardProps> = ({ 
  label = "Cognitive Load",
  value = "↑ 47%",
  sub = "during stress",
  position = 'top-left',
  accent = true
}) => {
  const theme = useTheme();
  const posMap = {
    'top-left': { top: '12%', left: '6%' },
    'top-right': { top: '18%', right: '6%' },
    'bottom-left': { bottom: '18%', left: '8%' },
    'bottom-right': { bottom: '22%', right: '8%' },
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: 0.5, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      style={{
        position: 'absolute',
        ...posMap[position],
        padding: '14px 18px',
        background: 'rgba(255,255,255,0.04)',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: 12,
        backdropFilter: 'blur(12px)',
        fontFamily: theme.typography.headline,
        zIndex: 50,
      }}
    >
      <div style={{
        fontSize: 9,
        fontWeight: 500,
        letterSpacing: '0.28em',
        textTransform: 'uppercase',
        color: accent ? theme.color_system.primary : theme.color_system.text_dim,
        marginBottom: 4,
      }}>
        {label}
      </div>
      <div style={{
        fontSize: 22,
        fontWeight: 500,
        letterSpacing: '-0.02em',
        color: theme.color_system.text,
      }}>
        {value}
      </div>
      {sub && (
        <div style={{
          fontSize: 10,
          color: theme.color_system.text_dim,
          marginTop: 2,
        }}>
          {sub}
        </div>
      )}
    </motion.div>
  );
};

export default FloatingCard;
