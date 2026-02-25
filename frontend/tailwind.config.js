/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#f0f4ff',
          100: '#e0e9ff',
          500: '#667eea',
          600: '#5a67d8',
          700: '#4c51bf',
        },
        accent: '#764ba2',
      },
      fontFamily: {
        sans: ['"Noto Sans TC"', 'Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
