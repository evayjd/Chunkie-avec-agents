/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        /* Ballet palette ─────────────────────────────── */
        petal: {
          50:  '#ffffff',
          100: '#fbf8f0',
          200: '#f7f3ea',
          300: '#f2eee4',
          400: '#ebe6da',  // 按钮颜色
          500: '#e3ddd0',
          600: '#d8d1c2',
        },
        blush: {
          50:  '#fffdf7',  // 页面背景
          100: '#f8f5ec',
          200: '#f1ede2',
          300: '#e7e2d4',
        },
        stone: {
          50:  '#fafaf9',
          100: '#f4f4f3',
          200: '#e8e8e6',
          300: '#d4d4d0',
          400: '#a8a8a3',
          500: '#74746e',
          600: '#52524d',
          700: '#3a3a36',   // main text
          800: '#242420',
          900: '#121210',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card:  '0 2px 12px rgba(0,0,0,0.06)',
        panel: '0 4px 24px rgba(0,0,0,0.08)',
        glow:  '0 0 0 3px rgba(248,143,168,0.25)',
      },
      borderRadius: {
        xl2: '1.25rem',
        xl3: '1.5rem',
      },
      keyframes: {
        'fade-in': {
          '0%':   { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '.5' },
        },
        'spin-slow': {
          '0%':   { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      animation: {
        'fade-in':    'fade-in 0.3s ease-out both',
        'pulse-soft': 'pulse-soft 2s ease-in-out infinite',
        'spin-slow':  'spin-slow 2s linear infinite',
      },
    },
  },
  plugins: [],
};
