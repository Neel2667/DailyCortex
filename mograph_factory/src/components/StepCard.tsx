import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface StepCardProps {
  steps: Array<{
    number: number;
    title: string;
    description: string;
    icon?: string;
  }>;
  color?: string;
}

export const StepCard: React.FC<StepCardProps> = ({ 
  steps = [
    { number: 1, title: "Pick the task", description: "The one you've been avoiding all day." },
    { number: 2, title: "Set 2 minutes", description: "Promise yourself: just two minutes." },
    { number: 3, title: "Just begin", description: "Action creates motivation. Not the other way around." },
  ],
  color
}) => {
  const theme = useTheme();
  const accentColor = color || theme.color_system.accent;

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
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: `repeat(${steps.length}, 1fr)`, 
        gap: 24, 
        padding: '0 8%',
        width: '100%',
        maxWidth: 1200,
      }}>
        {steps.map((step, i) => (
          <motion.div
            key={step.number}
            initial={{ opacity: 0, y: 40, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ 
              delay: 1.4 + i * 0.3, 
              duration: 0.7, 
              ease: [0.16, 1, 0.3, 1] 
            }}
            style={{
              position: 'relative',
              padding: '36px 28px',
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 16,
              textAlign: 'left',
            }}
          >
            {/* Bouncing number */}
            <motion.div
              initial={{ y: -20, scale: 0.5 }}
              animate={{ y: 0, scale: 1 }}
              transition={{ 
                delay: 1.4 + i * 0.3, 
                type: "spring",
                stiffness: 500,
                damping: 15
              }}
              style={{
                position: 'absolute',
                top: -20,
                left: 28,
                width: 44,
                height: 44,
                background: accentColor,
                color: theme.color_system.void,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 18,
                fontWeight: 700,
                fontFamily: theme.typography.headline,
                boxShadow: `0 0 30px ${accentColor}60`,
                zIndex: 2,
              }}
            >
              {step.number}
            </motion.div>

            <div style={{ marginTop: 16 }}>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.6 + i * 0.3, duration: 0.5 }}
                style={{
                  fontSize: 20,
                  fontWeight: 500,
                  color: theme.color_system.text,
                  marginBottom: 8,
                  letterSpacing: '-0.01em',
                }}
              >
                {step.title}
              </motion.div>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.8 + i * 0.3, duration: 0.5 }}
                style={{
                  fontSize: 14,
                  color: theme.color_system.text_dim,
                  lineHeight: 1.5,
                  fontFamily: theme.typography.body,
                }}
              >
                {step.description}
              </motion.div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default StepCard;
