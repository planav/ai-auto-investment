/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary colors - Electric Blue & Neon
        primary: {
          DEFAULT: '#00D4AA',
          light: '#00F0FF',
          dark: '#00B894',
          glow: 'rgba(0, 212, 170, 0.5)',
        },
        // Secondary colors - Neon Purple & Pink
        secondary: {
          DEFAULT: '#7B61FF',
          light: '#A78BFA',
          dark: '#6D28D9',
          glow: 'rgba(123, 97, 255, 0.5)',
        },
        // Accent colors - Gold/Amber
        accent: {
          DEFAULT: '#FFD700',
          light: '#FFEA00',
          dark: '#FFAA00',
          glow: 'rgba(255, 215, 0, 0.5)',
        },
        // Dark backgrounds
        dark: {
          DEFAULT: '#0A0A0F',
          light: '#12121A',
          lighter: '#1A1A2E',
          card: 'rgba(26, 26, 46, 0.8)',
        },
        // Semantic colors
        success: '#00D4AA',
        warning: '#FFA500',
        danger: '#FF4757',
        info: '#00F0FF',
      },
      fontFamily: {
        display: ['Space Grotesk', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'spin-slow': 'spin 8s linear infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(0, 212, 170, 0.5), 0 0 20px rgba(0, 212, 170, 0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 212, 170, 0.8), 0 0 40px rgba(0, 212, 170, 0.5)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'mesh-gradient': 'linear-gradient(135deg, rgba(0,212,170,0.1) 0%, rgba(123,97,255,0.1) 50%, rgba(255,215,0,0.1) 100%)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
