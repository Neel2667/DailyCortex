import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface QuestionBombProps {
  question: string;
  accent_words?: string[];
  particle_burst?: boolean;
}

export const QuestionBomb: React.FC<QuestionBombProps> = ({ 
  question = "Why do you procrastinate?",
  accent_words = ["procrastinate"],
  particle_burst = true
}) => {
  const theme = useTheme();
  const words = question.split(' ');

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: theme.color_system.void,
      overflow: 'hidden',
      fontFamily: theme.typography.headline,
    }}>
      {/* Ambient background particles burst */}
      {particle_burst && (
        <div style={{ position: 'absolute', inset: 0, zIndex: 1 }}>
          {Array.from({ length: 20 }).map((_, i) => (
            <motion.div
              key={i}
              initial={{ 
                x: 960, 
                y: 540, 
                scale: 0, 
                opacity: 0 
              }}
              animate={{ 
                x: 960 + (Math.random() - 0.5) * 800,
                y: 540 + (Math.random() - 0.5) * 600,
                scale: Math.random() * 2 + 0.5,
                opacity: [0, 0.8, 0]
              }}
              transition={{ 
                duration: 2,
                delay: i * 0.05,
                ease: [0.16, 1, 0.3, 1]
              }}
              style={{
                position: 'absolute',
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: i % 3 === 0 ? theme.color_system.primary : 
                          i % 3 === 1 ? theme.color_system.secondary : 
                          theme.color_system.tertiary,
                boxShadow: `0 0 20px ${i % 3 === 0 ? theme.color_system.primary : theme.color_system.secondary}`,
              }}
            />
          ))}
        </div>
      )}

      {/* Question text */}
      <div style={{ 
        position: 'relative',
        zIndex: 10,
        textAlign: 'center',
        padding: '0 10%'
      }}>
        <div style={{ overflow: 'hidden', marginBottom: 16 }}>
          {words.map((word, i) => {
            const isAccent = accent_words.some(aw => word.toLowerCase().includes(aw.toLowerCase()));
            return (
              <motion.span
                key={i}
                initial={{ y: '110%', opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ 
                  duration: 1.1,
                  delay: 0.5 + i * 0.15,
                  ease: [0.16, 1, 0.3, 1]
                }}
                style={{
                  display: 'inline-block',
                  fontSize: 'clamp(72px, 8vw, 120px)',
                  fontWeight: 500,
                  letterSpacing: '-0.03em',
                  lineHeight: 1.1,
                  color: isAccent ? theme.color_system.primary : theme.color_system.text,
                  marginRight: '0.3em',
                  fontFamily: isAccent ? theme.typography.accent_font : theme.typography.headline,
                  fontStyle: isAccent ? 'italic' : 'normal',
                  textShadow: '0 2px 40px rgba(0,0,0,0.8)',
                }}
              >
                {word}
              </motion.span>
            );
          })}
        </div>

        {/* Kicker line */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          style={{
            fontSize: 14,
            letterSpacing: '0.36em',
            textTransform: 'uppercase' as const,
            color: theme.color_system.primary,
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 12,
            fontFamily: theme.typography.headline,
          }}
        >
          <span style={{ width: 24, height: 1, background: theme.color_system.primary, opacity: 0.6 }} />
          Brain Hacks · Episode 03
          <span style={{ width: 24, height: 1, background: theme.color_system.primary, opacity: 0.6 }} />
        </motion.div>
      </div>
    </div>
  );
};

export default QuestionBomb;
