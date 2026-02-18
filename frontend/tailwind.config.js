/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6366f1',
          dark: '#4f46e5',
          light: '#818cf8',
        },
        secondary: {
          DEFAULT: '#8b5cf6',
        },
        background: {
          DEFAULT: '#f8fafc',
          light: '#f1f5f9',
        },
        surface: {
          DEFAULT: '#ffffff',
        },
        text: {
          primary: '#1e293b',
          secondary: '#64748b',
          light: '#94a3b8',
        },
        border: {
          DEFAULT: '#e2e8f0',
          light: '#f1f5f9',
        },
        'input-background': {
          DEFAULT: '#ffffff',
        },
        success: {
          DEFAULT: '#10b981',
          light: '#d1fae5',
        },
        error: {
          DEFAULT: '#ef4444',
          light: '#fee2e2',
        },
        warning: {
          DEFAULT: '#f59e0b',
          light: '#fef3c7',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

