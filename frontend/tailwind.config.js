/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          50: '#eaeaea',
          100: '#bebebf',
          200: '#929293',
          300: '#666667',
          400: '#373737',
          500: '#1a1a1a',
          600: '#212121',
          700: '#2a2a2a',
          800: '#1c1c1c',
          900: '#141414',
        },
        accent: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06fdd8',
          600: '#04d9ba',
          700: '#03b69e',
        },
        surface: {
          primary: '#212121',
          secondary: '#2a2a2a',
          tertiary: '#303030',
          hover: '#323232',
          active: '#383838',
        }
      },
      boxShadow: {
        'inner-sm': 'inset 0 1px 2px 0 rgb(0 0 0 / 0.1)',
      }
    },
  },
  plugins: [],
} 