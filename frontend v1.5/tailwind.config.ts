import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{vue,ts,tsx}'],
  theme: {
    extend: {
      colors: {

        primary: {
          50:  '#f7fbfd',
          100: '#eef7fb',
          500: '#9ec6d3',
          600: '#86b3c2',
          700: '#6fa0b1',
          900: '#4f7f91',
        },

        accent: {
          100: '#fdf2f8',
          200: '#fce7f3',
          300: '#fbcfe8',
          400: '#f9a8d4',

        },

        cream: {
          100: '#fef9c3',
          200: '#fef08a',
          300: '#fde047',
        },

      },
      

      fontFamily: {
        sans: ['system-ui', '-apple-system', 'Segoe UI', 'Arial', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        kaeru: ['KaeruKaeru', 'cursive'],
      },
    },
  },
  plugins: [],
} satisfies Config