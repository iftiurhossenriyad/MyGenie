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
          DEFAULT: '#1a2a4a',
          light: '#2d4470',
          dark: '#0f1a30',
          50: '#f0f2f7',
          100: '#d9dfec',
          500: '#1a2a4a',
          700: '#0f1a30',
          900: '#080f1c',
        },
        gold: {
          DEFAULT: '#f0a500',
          light: '#ffc233',
          dark: '#c47f00',
          50: '#fff8e6',
          100: '#ffedb8',
          500: '#f0a500',
          600: '#d18f00',
          700: '#a67000',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans Bengali', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}