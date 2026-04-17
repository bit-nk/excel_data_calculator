/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['SF Mono', 'Fira Code', 'Cascadia Code', 'monospace'],
      },
      colors: {
        ink: {
          900: '#0B0B15',
          800: '#1A1A2E',
        },
        accent: {
          DEFAULT: '#7C3AED',
          hover: '#6D28D9',
          soft: 'rgba(124,58,237,0.10)',
        },
        body: '#F5F6FA',
        surface: '#FFFFFF',
        input: '#F0F1F5',
        line: '#E5E7EB',
        muted: {
          DEFAULT: '#6B7280',
          soft: '#9CA3AF',
        },
        ok: {
          DEFAULT: '#10B981',
          soft: 'rgba(16,185,129,0.10)',
        },
        warn: {
          DEFAULT: '#F59E0B',
          soft: 'rgba(245,158,11,0.10)',
        },
        danger: {
          DEFAULT: '#EF4444',
          soft: 'rgba(239,68,68,0.10)',
        },
        info: {
          DEFAULT: '#3B82F6',
          soft: 'rgba(59,130,246,0.10)',
        },
        platform: {
          aws: '#FF9900',
          datadog: '#632CA6',
          confluent: '#1A73E8',
          mongodb: '#00684A',
          singlestore: '#AA00FF',
          harness: '#0095F7',
        },
      },
      boxShadow: {
        card: '0 1px 2px rgba(0,0,0,0.04)',
        'card-hover': '0 8px 30px rgba(0,0,0,0.08)',
        lift: '0 8px 30px rgba(0,0,0,0.12)',
        accent: '0 4px 14px rgba(124,58,237,0.35)',
      },
      borderRadius: {
        card: '12px',
      },
      keyframes: {
        pulseDot: {
          '0%,100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
        fadeInUp: {
          from: { opacity: '0', transform: 'translateY(16px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        pulseDot: 'pulseDot 2s ease-in-out infinite',
        fadeInUp: 'fadeInUp 0.5s ease forwards',
      },
    },
  },
  plugins: [],
}
