import React, { useState, useEffect } from 'react';
import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface StatShockProps {
  number: string;
  suffix?: string;
  caption: string;
  context?: string;
  color?: string;
}

export const StatShock: React.FC<StatShockProps> = ({ 
  number = "1",
  suffix = "/5",
  caption = "adults are chronic procrastinators",
  context = "That's roughly 1.4 billion people",
  color
}) => {
  const theme = useTheme();
  const [count, setCount] = useState(0);
  const targetNum = parseInt(number) || 1;
  const accentColor = color || theme.color_system.primary;

  useEffect(() => {
    const controls = animate(0, targetNum, {
      duration: 1.2,
      ease: [0.34, 1.56, 0.64, 1],
      onUpdate: (latest) => setCount(Math.round(latest)),
    });
    return controls.stop;
  }, [targetNum]);

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
      <div style={{ textAlign: 'left', padding: '0 8%', width: '100%' }}>
        {/* Kicker */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          style={{
            fontSize: 13,
            letterSpacing: '0.32em',
            textTransform: 'uppercase' as const,
            color: accentColor,
            marginBottom: 24,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            fontWeight: 500,
          }}
        >
          <span style={{ width: 24, height: 1, background: accentColor }} />
          The Number
        </motion.div>

        {/* Big stat */}
        <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: 20 }}>
          <motion.span
            initial={{ scale: 0.3, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.4, duration: 1, ease: [0.34, 1.56, 0.64, 1] }}
            style={{
              fontSize: 'clamp(120px, 18vw, 240px)',
              fontWeight: 500,
              lineHeight: 0.88,
              letterSpacing: '-0.06em',
              color: theme.color_system.text,
              fontVariantNumeric: 'tabular-nums',
              display: 'inline-block',
            }}
          >
            {count}
          </motion.span>
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            style={{
              fontSize: 'clamp(48px, 6vw, 96px)',
              color: accentColor,
              fontFamily: theme.typography.accent_font,
              fontStyle: 'italic',
              fontWeight: 400,
              verticalAlign: 'top',
              marginLeft: 8,
            }}
          >
            {suffix}
          </motion.span>
        </div>

        {/* Caption */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.1, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          style={{
            fontSize: 'clamp(18px, 2vw, 24px)',
            color: theme.color_system.text_dim,
            lineHeight: 1.5,
            maxWidth: 500,
            fontFamily: theme.typography.accent_font,
            fontStyle: 'italic',
          }}
        >
          {caption}
          {context && (
            <span style={{ color: theme.color_system.text, fontWeight: 500, marginLeft: 8 }}>
              — {context}
            </span>
          )}
        </motion.div>

        {/* Live counter simulation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.5 }}
          style={{
            marginTop: 40,
            padding: '16px 20px',
            background: 'rgba(20,184,166,0.05)',
            border: `1px solid ${accentColor}25`,
            borderRadius: 12,
            display: 'inline-flex',
            alignItems: 'baseline',
            gap: 14,
          }}
        >
          <span style={{ 
            fontSize: 10, 
            fontWeight: 500, 
            letterSpacing: '0.28em', 
            textTransform: 'uppercase' as const, 
            color: accentColor 
          }}>
            ● Live
          </span>
          <span style={{ fontSize: 24, fontWeight: 500, color: theme.color_system.text, fontVariantNumeric: 'tabular-nums' }}>
            214,673,891
          </span>
          <span style={{ fontSize: 14, color: theme.color_system.text_dim }}>and counting</span>
        </motion.div>
      </div>
    </div>
  );
};

export default StatShock;
