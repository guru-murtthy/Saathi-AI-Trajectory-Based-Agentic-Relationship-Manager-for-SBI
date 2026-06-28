/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        sbi: { blue: '#1e3a8a', teal: '#0d9488' },
      },
    },
  },
  plugins: [],
};
