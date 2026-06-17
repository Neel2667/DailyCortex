import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface BarData {
  label: string;
  value: number;
  color?: string;
}

interface BarRaceChartProps {
  data?: BarData[];
  title?: string;
}

export const BarRaceChart: React.FC<BarRaceChartProps> = ({ 
  data = [
    { label: "Dopamine", value: 85 },
    { label: "Serotonin", value: 62 },
    { label: "Cortisol", value: 78 },
    { label: "Oxytocin", value: 45 },
    { label: "Endorphin", value: 70 },
  ],
  title = "Neurotransmitter Levels"
}) => {
  const theme = useTheme();
  const maxValue = Math.max(...data.map(d => d.value)) * 1.2;
  const sortedData = [...data].sort((a, b) => b.value - a.value);
  const colors = [
    theme.color_system.primary,
    theme.color_system.secondary,
    theme.color_system.tertiary,
    theme.color_system.accent,
    '#ffffff',
  ];

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: theme.color_system.void,
      padding: '0 8%',
      fontFamily: theme.typography.headline,
    }}>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        style={{
          fontSize: 13,
          fontWeight: 500,
          letterSpacing: '0.32em',
          textTransform: 'uppercase',
          color: theme.color_system.primary,
          marginBottom: 40,
          textAlign: 'center',
        }}
      >
        {title}
      </motion.div>

      <div style={{ width: '100%', maxWidth: 800, display: 'flex', flexDirection: 'column', gap: 16 }}>
        <AnimatePresence>
          {sortedData.map((item, i) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, x: -40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.15, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
              style={{ display: 'flex', alignItems: 'center', gap: 16 }}
            >
              <div style={{
                width: 120,
                textAlign: 'right',
                fontSize: 14,
                fontWeight: 500,
                color: theme.color_system.text,
                fontFamily: theme.typography.headline,
                letterSpacing: '-0.01em',
              }}>
                {item.label}
              </div>
              
              <div style={{ flex: 1, height: 28, background: 'rgba(255,255,255,0.04)', borderRadius: 6, overflow: 'hidden', position: 'relative' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(item.value / maxValue) * 100}%` }}
                  transition={{ delay: 0.8 + i * 0.15, duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
                  style={{
                    height: '100%',
                    background: item.color || colors[i % colors.length],
                    borderRadius: 6,
                    opacity: 0.8,
                    boxShadow: `0 0 20px ${(item.color || colors[i % colors.length])}40`,
                  }}
                />
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1.5 + i * 0.15, duration: 0.5 }}
                  style={{
                    position: 'absolute',
                    right: 12,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    fontSize: 13,
                    fontWeight: 600,
                    color: theme.color_system.text,
                    fontFamily: theme.typography.headline,
                    fontVariantNumeric: 'tabular-nums',
                  }}
                >
                  {item.value}%
                </motion.div>
              </div>

              <div style={{
                width: 40,
                fontSize: 12,
                color: theme.color_system.text_dim,
                fontFamily: theme.typography.headline,
              }}>
                #{i + 1}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default BarRaceChart;
