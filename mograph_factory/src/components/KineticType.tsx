import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface KineticTypeProps {
  text: string;
  revealType?: 'word' | 'line' | 'char';
  stagger?: number;
  style?: 'title' | 'subtitle' | 'kicker' | 'stat';
  color?: string;
  position?: 'center' | 'left' | 'right';
}

export const KineticType: React.FC<KineticTypeProps> = ({ 
  text = "Why You Procrastinate",
  revealType = 'word',
  stagger = 0.15,
  style = 'title',
  color,
  position = 'center'
}) => {
  const theme = useTheme();
  const accentColor = color || theme.color_system.primary;
  
  const styleMap = {
    title: { fontSize: 'clamp(72px, 8vw, 120px)', fontWeight: 500, letterSpacing: '-0.03em' },
    subtitle: { fontSize: 'clamp(18px, 2vw, 28px)', fontWeight: 400, letterSpacing: '0.01em' },
    kicker: { fontSize: 14, fontWeight: 500, letterSpacing: '0.36em', textTransform: 'uppercase' as const },
    stat: { fontSize: 'clamp(120px, 18vw, 240px)', fontWeight: 500, letterSpacing: '-0.06em' },
  };

  const elements = revealType === 'char' ? text.split('') : text.split(' ');
  const isWord = revealType === 'word' || revealType === 'char';

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: position === 'center' ? 'center' : position === 'left' ? 'flex-start' : 'flex-end',
      background: 'transparent',
      fontFamily: theme.typography.headline,
      padding: '0 10%',
    }}>
      <div style={{ overflow: 'hidden' }}>
        {isWord ? (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3em' }}>
            {elements.map((word, i) => (
              <motion.span
                key={i}
                initial={{ y: '110%', opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ 
                  duration: 1.1,
                  delay: 0.5 + i * stagger,
                  ease: [0.16, 1, 0.3, 1]
                }}
                style={{
                  display: 'inline-block',
                  ...styleMap[style],
                  color: style === 'kicker' ? accentColor : theme.color_system.text,
                  lineHeight: 1.1,
                  fontFamily: style === 'kicker' ? theme.typography.headline : styleMap[style].fontSize && styleMap[style].fontSize > '100px' ? theme.typography.headline : theme.typography.headline,
                  textShadow: style === 'title' ? '0 2px 40px rgba(0,0,0,0.8)' : undefined,
                }}
              >
                {word}{revealType === 'word' ? '\u00A0' : ''}
              </motion.span>
            ))}
          </div>
        ) : (
          <motion.div
            initial={{ y: '100%', opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
            style={{
              ...styleMap[style],
              color: theme.color_system.text,
            }}
          >
            {text}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default KineticType;
