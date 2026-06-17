import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface Region {
  id: string;
  label: string;
  cx: number;
  cy: number;
  color: string;
  delay: number;
}

interface BrainSVGProps {
  active_regions?: string[];
  show_labels?: boolean;
  pulse_rings?: boolean;
}

export const BrainSVG: React.FC<BrainSVGProps> = ({ 
  active_regions = ['prefrontal', 'amygdala'],
  show_labels = true,
  pulse_rings = true
}) => {
  const theme = useTheme();

  const regions: Region[] = [
    { id: 'prefrontal', label: 'Prefrontal Cortex', cx: -25, cy: -20, color: theme.color_system.primary, delay: 1.5 },
    { id: 'amygdala', label: 'Amygdala', cx: 30, cy: 20, color: theme.color_system.secondary, delay: 1.8 },
    { id: 'hippocampus', label: 'Hippocampus', cx: 0, cy: -40, color: theme.color_system.tertiary, delay: 2.1 },
  ];

  const active = regions.filter(r => active_regions.includes(r.id));

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: theme.color_system.void,
    }}>
      <div style={{ position: 'relative', width: '50%', height: '80%' }}>
        <svg viewBox="0 0 300 300" style={{ width: '100%', height: '100%' }}>
          <defs>
            <radialGradient id="brainGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor={theme.color_system.primary} stopOpacity="0.3" />
              <stop offset="100%" stopColor={theme.color_system.primary} stopOpacity="0" />
            </radialGradient>
            <linearGradient id="brainStroke" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor={theme.color_system.primary} />
              <stop offset="100%" stopColor={theme.color_system.secondary} />
            </linearGradient>
          </defs>

          {/* Background glow */}
          <circle cx="150" cy="150" r="120" fill="url(#brainGlow)">
            <animate attributeName="r" values="110;130;110" dur="4s" repeatCount="indefinite" />
          </circle>

          <g transform="translate(150,150)">
            {/* Brain outline */}
            <path
              d="M 0 -80 Q -40 -80 -55 -50 Q -85 -40 -75 -10 Q -90 25 -55 45 Q -45 80 -10 75 Q 10 90 35 70 Q 75 75 80 35 Q 95 -5 70 -30 Q 80 -65 40 -70 Q 30 -85 0 -80 Z"
              fill="rgba(20,184,166,0.08)"
              stroke="url(#brainStroke)"
              strokeWidth="2"
            />

            {/* Neural connections */}
            <path
              d="M 0 -50 Q -25 -40 -30 -10 M 20 -50 Q 35 -25 25 5 M -30 10 Q -10 25 10 20 M -10 35 Q 5 50 25 40"
              fill="none"
              stroke={theme.color_system.primary}
              strokeWidth="1.5"
              opacity="0.6"
            >
              <animate attributeName="opacity" values="0.3;0.8;0.3" dur="3s" repeatCount="indefinite" />
            </path>

            {/* Active region dots */}
            {active.map((region) => (
              <g key={region.id}>
                <circle cx={region.cx} cy={region.cy} r="4" fill={region.color}>
                  <animate attributeName="r" values="3;6;3" dur="2s" begin={`${region.delay}s`} repeatCount="indefinite" />
                  <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" begin={`${region.delay}s`} repeatCount="indefinite" />
                </circle>
              </g>
            ))}
          </g>

          {/* Connection lines */}
          <line x1="80" y1="100" x2="220" y2="100" stroke={theme.color_system.primary} strokeWidth="1" opacity="0.4">
            <animate attributeName="opacity" values="0.1;0.8;0.1" dur="2.5s" repeatCount="indefinite" />
          </line>
          <line x1="100" y1="200" x2="200" y2="180" stroke={theme.color_system.secondary} strokeWidth="1" opacity="0.4">
            <animate attributeName="opacity" values="0.1;0.8;0.1" dur="2.5s" begin="1.25s" repeatCount="indefinite" />
          </line>
        </svg>

        {/* Pulse rings */}
        {pulse_rings && active.map((region) => {
          const screenX = 150 + (region.cx / 150) * 50;
          const screenY = 150 + (region.cy / 150) * 50;
          return (
            <motion.div
              key={`ring-${region.id}`}
              initial={{ scale: 0.5, opacity: 1 }}
              animate={{ scale: 1.8, opacity: 0 }}
              transition={{ 
                duration: 2.5, 
                repeat: Infinity, 
                delay: region.delay,
                ease: "easeOut"
              }}
              style={{
                position: 'absolute',
                left: `${screenX}%`,
                top: `${screenY}%`,
                width: 40,
                height: 40,
                border: `1px solid ${region.color}40`,
                borderRadius: '50%',
                transform: 'translate(-50%, -50%)',
                pointerEvents: 'none',
              }}
            />
          );
        })}

        {/* Region labels */}
        {show_labels && active.map((region) => {
          const screenX = region.cx < 0 ? '10%' : region.cx > 0 ? '75%' : '50%';
          const screenY = region.cy < 0 ? '20%' : '65%';
          return (
            <motion.div
              key={`label-${region.id}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: region.delay + 0.5, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              style={{
                position: 'absolute',
                left: screenX,
                top: screenY,
                padding: '6px 12px',
                background: 'rgba(255,255,255,0.05)',
                border: `1px solid ${region.color}40`,
                borderRadius: 6,
                color: region.color,
                fontSize: 11,
                fontWeight: 500,
                letterSpacing: '0.22em',
                textTransform: 'uppercase' as const,
                fontFamily: theme.typography.headline,
                whiteSpace: 'nowrap',
                backdropFilter: 'blur(8px)',
              }}
            >
              {region.label}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default BrainSVG;
