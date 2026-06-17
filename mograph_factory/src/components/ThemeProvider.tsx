import React, { createContext, useContext } from 'react';

export interface ThemeContextType {
  color_system: {
    void: string;
    primary: string;
    secondary: string;
    tertiary: string;
    accent: string;
    text: string;
    text_dim: string;
  };
  typography: {
    headline: string;
    body: string;
    accent_font: string;
  };
  motion_language: {
    easing: string;
    stagger_base: number;
    particle_density: number;
    grid_opacity: number;
    grain_intensity: number;
  };
}

const defaultTheme: ThemeContextType = {
  color_system: {
    void: '#0a0e27',
    primary: '#14b8a6',
    secondary: '#f472b6',
    tertiary: '#818cf8',
    accent: '#fbbf24',
    text: '#f4f4f5',
    text_dim: '#a1a1aa',
  },
  typography: {
    headline: 'Space Grotesk, sans-serif',
    body: 'Inter, sans-serif',
    accent_font: 'Fraunces, serif',
  },
  motion_language: {
    easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
    stagger_base: 0.15,
    particle_density: 130,
    grid_opacity: 0.025,
    grain_intensity: 0.06,
  },
};

const ThemeContext = createContext<ThemeContextType>(defaultTheme);

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider: React.FC<{ theme: ThemeContextType; children: React.ReactNode }> = ({ theme, children }) => {
  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeProvider;
