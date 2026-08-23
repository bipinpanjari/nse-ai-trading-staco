/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'trading-black': '#0a0b0d',
        'trading-gray': '#16171a',
        'trading-green': '#00c805',
        'trading-red': '#ff3b3b',
      }
    },
  },
  plugins: [],
}
