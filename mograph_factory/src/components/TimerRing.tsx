import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface TimerRingProps {
  duration?: number;
  color?: string;
  label?: string;
}

export const TimerRing: React.FC<TimerRingProps> = ({ 
  duration = 120,
  color,
  label = "timer starts"
}) => {
  const theme = useTheme();
  const accentColor = color || theme.color_system.accent;
  const minutes = Math.floor(duration / 60).toString().padStart(2, '0');
  const seconds = (duration % 60).toString().padStart(2, '0');
  const circumference = 2 * Math.PI * 14; // r=14
  const strokeDashoffset = circumference;

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
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.6, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 18,
          padding: '16px 28px',
          background: `${accentColor}08`,
          border: `1px solid ${accentColor}25`,
          borderRadius: 999,
        }}
      >
        <div style={{ width: 32, height: 32, position: 'relative' }}>
          <svg width="32" height="32" viewBox="0 0 32 32" style={{ transform: 'rotate(-90deg)' }}>
            <circle cx="16" cy="16" r="14" fill="none" stroke={`${accentColor}18`} strokeWidth={3} />
            <circle cx="16" cy="16" r="14" fill="none" stroke={accentColor} strokeWidth={3} strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={circumference}
            >
              <animate attributeName="stroke-dashoffset" from={circumference} to="0" dur={`${duration}s`} fill="freeze" />
            </circle>
          </svg>
        </div>
        <div>
          <div style={{
            fontFamily: theme.typography.headline,
            fontSize: 24,
            fontWeight: 500,
            letterSpacing: '-0.02em',
            color: accentColor,
            fontVariantNumeric: 'tabular-nums',
          }}>
            {minutes}:{seconds}
          </div>
          <div style={{
            fontFamily: theme.typography.headline,
            fontSize: 10,
            fontWeight: 500,
            letterSpacing: '0.24em',
            textTransform: 'uppercase',
            color: theme.color_system.text_dim,
          }}>
            {label}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default TimerRing;
