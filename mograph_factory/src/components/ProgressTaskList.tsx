import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';

interface Task {
  icon: string;
  text: string;
  progress: number;
}

interface ProgressTaskListProps {
  tasks?: Task[];
}

export const ProgressTaskList: React.FC<ProgressTaskListProps> = ({ 
  tasks = [
    { icon: "✉", text: "Reply to important emails", progress: 15 },
    { icon: "📋", text: "File taxes", progress: 35 },
    { icon: "🏥", text: "Schedule doctor visit", progress: 65 },
    { icon: "💪", text: "Start exercise routine", progress: 90 },
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
      background: theme.color_system.void,
      padding: '0 8%',
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, width: '100%', maxWidth: 600 }}>
        {tasks.map((task, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.2 + i * 0.2, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              padding: '10px 14px',
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.06)',
              borderRadius: 10,
              fontSize: 13,
              color: '#d4d4d8',
              fontFamily: theme.typography.body,
            }}
          >
            <span style={{
              width: 24,
              height: 24,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: 6,
              background: `${theme.color_system.primary}15`,
              color: theme.color_system.primary,
              flexShrink: 0,
              fontSize: 12,
            }}>
              {task.icon}
            </span>
            <span style={{ flex: 1 }}>{task.text}</span>
            <div style={{ width: 80, height: 3, background: 'rgba(255,255,255,0.08)', borderRadius: 999, overflow: 'hidden' }}>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${task.progress}%` }}
                transition={{ delay: 2 + i * 0.2, duration: 2, ease: [0.16, 1, 0.3, 1] }}
                style={{ height: '100%', background: `linear-gradient(90deg, ${theme.color_system.primary}, ${theme.color_system.tertiary})`, borderRadius: 999 }}
              />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default ProgressTaskList;
