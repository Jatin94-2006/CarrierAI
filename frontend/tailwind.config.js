/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#050c14',
          900: '#07121e',
          800: '#0b1928',
          700: '#102235',
          600: '#18314a',
        },
        cream: {
          50: '#fffdfa',
          100: '#fffaf5',
          200: '#f7f3ed',
          300: '#eee8df',
          400: '#ded8ce',
        },
        coral: {
          light: '#ffe1d9',
          DEFAULT: '#ff806b',
          hover: '#ff6b52',
          dark: '#dc6653',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Georgia', 'serif'],
        mono: ['Fira Code', 'Courier New', 'monospace'],
      },
      boxShadow: {
        'subtle': '0 4px 20px -2px rgba(16, 24, 40, 0.06), 0 2px 8px -2px rgba(16, 24, 40, 0.04)',
        'premium': '0 20px 50px -12px rgba(7, 18, 30, 0.12), 0 0 1px 1px rgba(7, 18, 30, 0.05)',
        'glow-coral': '0 0 35px -5px rgba(255, 128, 107, 0.35)',
        'glow-blue': '0 0 35px -5px rgba(56, 189, 248, 0.35)',
      },
      borderRadius: {
        '2xl': '18px',
        '3xl': '24px',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        pulseSlow: {
          '0%, 100%': { opacity: '0.4', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.05)' },
        },
        orbSpin: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        }
      },
      animation: {
        float: 'float 4s ease-in-out infinite',
        'float-slow': 'float 7s ease-in-out infinite',
        'pulse-slow': 'pulseSlow 3s ease-in-out infinite',
        'orb-spin': 'orbSpin 12s linear infinite',
      }
    },
  },
  plugins: [],
}
