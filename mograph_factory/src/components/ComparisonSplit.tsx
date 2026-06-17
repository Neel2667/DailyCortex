import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface ComparisonSplitProps {
  leftLabel: string;
  rightLabel: string;
  leftValue: number;
  rightValue: number;
  leftColor?: string;
  rightColor?: string;
  unit?: string;
}

export const ComparisonSplit: React.FC<ComparisonSplitProps> = ({ 
  leftLabel = "Low Dopamine",
  rightLabel = "Healthy Brain",
  leftValue = 85,
  rightValue = 25,
  leftColor,
  rightColor,
  unit = "%"
}) => {
  const theme = useTheme();
  const leftC = leftColor || theme.color_system.secondary;
  const rightC = rightColor || theme.color_system.primary;
  const maxVal = Math.max(leftValue, rightValue) * 1.2;

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 60,
      alignItems: 'center',
      padding: '0 8%',
      background: theme.color_system.void,
      fontFamily: theme.typography.headline,
    }}>
      {/* Left side */}
      <motion.div
        initial={{ opacity: 0, x: -40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.4, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        <div style={{ 
          fontSize: 13, 
          letterSpacing: '0.28em', 
          textTransform: 'uppercase' as const, 
          color: leftC, 
          marginBottom: 16,
          fontWeight: 500,
        }}>
          {leftLabel}
        </div>
        <div style={{ 
          fontSize: 'clamp(72px, 10vw, 140px)', 
          fontWeight: 500, 
          color: theme.color_system.text, 
          letterSpacing: '-0.04em',
          lineHeight: 0.9,
          marginBottom: 12,
        }}>
          {leftValue}{unit}
        </div>
        <div style={{ height: 6, background: 'rgba(255,255,255,0.08)', borderRadius: 999, overflow: 'hidden' }}>
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${(leftValue / maxVal) * 100}%` }}
            transition={{ delay: 0.8, duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
            style={{ height: '100%', background: leftC, borderRadius: 999 }}
          />
        </div>
      </motion.div>

      {/* VS Divider */}
      <div style={{ position: 'absolute', left: '50%', top: '50%', transform: 'translate(-50%, -50%)', zIndex: 2 }}>
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 1.2, type: 'spring', stiffness: 400, damping: 15 }}
          style={{
            width: 48,
            height: 48,
            borderRadius: '50%',
            background: 'rgba(255,255,255,0.08)',
            border: '1px solid rgba(255,255,255,0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 12,
            fontWeight: 700,
            color: theme.color_system.text_dim,
            letterSpacing: '0.1em',
            backdropFilter: 'blur(8px)',
          }}
        >
          VS
        </motion.div>
      </div>

      {/* Right side */}
      <motion.div
        initial={{ opacity: 0, x: 40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.6, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        <div style={{ 
          fontSize: 13, 
          letterSpacing: '0.28em', 
          textTransform: 'uppercase' as const, 
          color: rightC, 
          marginBottom: 16,
          fontWeight: 500,
          textAlign: 'right',
        }}>
          {rightLabel}
        </div>
        <div style={{ 
          fontSize: 'clamp(72px, 10vw, 140px)', 
          fontWeight: 500, 
          color: theme.color_system.text, 
          letterSpacing: '-0.04em',
          lineHeight: 0.9,
          marginBottom: 12,
          textAlign: 'right',
        }}>
          {rightValue}{unit}
        </div>
        <div style={{ height: 6, background: 'rgba(255,255,255,0.08)', borderRadius: 999, overflow: 'hidden' }}>
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${(rightValue / maxVal) * 100}%` }}
            transition={{ delay: 1.0, duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
            style={{ height: '100%', background: rightC, borderRadius: 999 }}
          />
        </div>
      </motion.div>
    </div>
  );
};

export default ComparisonSplit;
