/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fdf8e1',
          100: '#fcf0b4',
          200: '#fae682',
          300: '#f8dc50',
          400: '#f6d32b',
          500: '#f4c91a', // EVMORE Gold
          600: '#e5b514',
          700: '#c9940f',
          800: '#a6730c',
          900: '#7d5409'
        },
        evmore: {
          gold: '#f4c91a',
          dark: '#1a1a2e',
          darker: '#0f0f1a'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 3s linear infinite',
        'mining': 'mining 1.5s ease-in-out infinite'
      },
      keyframes: {
        mining: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' }
        }
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms')
  ]
}
