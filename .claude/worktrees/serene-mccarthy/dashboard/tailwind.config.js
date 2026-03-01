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
          50: '#fdf4f0',
          100: '#fbe4d9',
          200: '#f6c3b0',
          300: '#ed9a7d',
          400: '#e46d4e',
          500: '#d94d29',
          600: '#c43d1f',
          700: '#a3321a',
          800: '#872d1a',
          900: '#702b19',
        }
      }
    },
  },
  plugins: [],
}
