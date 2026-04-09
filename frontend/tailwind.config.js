/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        driven: {
          navy: '#1B2A4A',
          red: '#D94F3B',
          orange: '#E8734A',
          gray: {
            50: '#F8F9FA',
            100: '#F1F3F5',
            200: '#E9ECEF',
            300: '#DEE2E6',
            400: '#ADB5BD',
            500: '#868E96',
          },
        },
      },
    },
  },
  plugins: [],
}
