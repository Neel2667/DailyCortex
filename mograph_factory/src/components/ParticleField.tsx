import React, { useRef, useEffect } from 'react';
import { useTheme } from './ThemeProvider';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  opacity: number;
  twinkleSpeed: number;
  twinkleOffset: number;
  color: string;
}

interface ParticleFieldProps {
  count?: number;
  speed?: number;
  direction?: 'up' | 'down' | 'random';
}

export const ParticleField: React.FC<ParticleFieldProps> = ({ 
  count = 130,
  speed = 1,
  direction = 'up'
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const theme = useTheme();
  const particlesRef = useRef<Particle[]>([]);
  const frameRef = useRef(0);
  const animRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = 1920;
    const h = 1080;
    canvas.width = w;
    canvas.height = h;

    const colors = [
      theme.color_system.primary,
      theme.color_system.secondary,
      theme.color_system.tertiary,
      theme.color_system.accent,
      '#ffffff'
    ];

    particlesRef.current = Array.from({ length: count }, () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.25 * speed,
      vy: direction === 'up' ? -0.08 - Math.random() * 0.2 * speed :
          direction === 'down' ? 0.08 + Math.random() * 0.2 * speed :
          (Math.random() - 0.5) * 0.2 * speed,
      size: Math.random() * 1.8 + 0.3,
      opacity: Math.random() * 0.5 + 0.15,
      twinkleSpeed: Math.random() * 0.025 + 0.005,
      twinkleOffset: Math.random() * Math.PI * 2,
      color: colors[Math.floor(Math.random() * colors.length)]
    }));

    const draw = (t: number) => {
      frameRef.current = t;
      ctx.clearRect(0, 0, w, h);
      
      particlesRef.current.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        
        if (p.y < -10) { p.y = h + 10; p.x = Math.random() * w; }
        if (p.y > h + 10) { p.y = -10; p.x = Math.random() * w; }
        if (p.x < -10) p.x = w + 10;
        if (p.x > w + 10) p.x = -10;
        
        const twinkle = Math.sin(t * p.twinkleSpeed + p.twinkleOffset) * 0.3 + 0.7;
        ctx.globalAlpha = p.opacity * twinkle;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      });
      
      ctx.globalAlpha = 1;
      animRef.current = requestAnimationFrame(draw);
    };

    animRef.current = requestAnimationFrame(draw);

    return () => cancelAnimationFrame(animRef.current);
  }, [count, speed, direction, theme]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        zIndex: 60,
        pointerEvents: 'none'
      }}
    />
  );
};

export default ParticleField;
