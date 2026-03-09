/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          navy:         '#1E3A5F',
          'navy-dark':  '#152B47',
          'navy-light': '#264875',
          blue:         '#4A90D9',
          'blue-light': '#6BA8E3',
          'blue-dark':  '#357ABD',
          teal:         '#0D9488',
          'teal-light': '#14B8A6',
          'teal-dark':  '#0a7a70',
          gold:         '#D4A843',
          'gold-light': '#E8C066',
          'gold-dark':  '#b8902e',
          coral:        '#E85454',
          purple:       '#7C3AED',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card:           '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)',
        'card-hover':   '0 8px 24px rgba(30,58,95,0.10), 0 2px 8px rgba(0,0,0,0.06)',
        enterprise:     '0 0 0 1px rgba(30,58,95,0.08), 0 4px 16px rgba(30,58,95,0.10)',
        glow:           '0 0 20px rgba(74,144,217,0.25)',
        'glow-teal':    '0 0 20px rgba(13,148,136,0.25)',
        'inner-sm':     'inset 0 1px 2px rgba(0,0,0,0.05)',
        float:          '0 20px 60px rgba(30,58,95,0.15), 0 4px 16px rgba(0,0,0,0.08)',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.25rem',
        '4xl': '2rem',
      },
      backgroundImage: {
        'gradient-navy':   'linear-gradient(135deg, #1E3A5F 0%, #264875 100%)',
        'gradient-teal':   'linear-gradient(135deg, #0D9488 0%, #14B8A6 100%)',
        'gradient-blue':   'linear-gradient(135deg, #357ABD 0%, #6BA8E3 100%)',
        'gradient-gold':   'linear-gradient(135deg, #D4A843 0%, #E8C066 100%)',
        'gradient-purple': 'linear-gradient(135deg, #6d28d9 0%, #9460f5 100%)',
        'dot-pattern':     'radial-gradient(circle, rgba(255,255,255,0.15) 1px, transparent 1px)',
      },
      backgroundSize: {
        'dot-sm': '16px 16px',
        'dot-md': '24px 24px',
      },
      animation: {
        'fade-in':    'fadeIn 0.25s ease-out',
        'slide-up':   'slideUp 0.35s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in':   'scaleIn 0.2s ease-out',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
        'shimmer':    'shimmer 1.5s linear infinite',
      },
      keyframes: {
        fadeIn:    { from: { opacity: '0' },                              to: { opacity: '1' } },
        slideUp:   { from: { opacity: '0', transform: 'translateY(8px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        slideDown: { from: { opacity: '0', transform: 'translateY(-8px)'},  to: { opacity: '1', transform: 'translateY(0)' } },
        scaleIn:   { from: { opacity: '0', transform: 'scale(0.95)' },    to: { opacity: '1', transform: 'scale(1)' } },
        pulseSoft: { '0%,100%': { opacity: '1' }, '50%': { opacity: '0.7' } },
        shimmer:   { from: { backgroundPosition: '-200% 0' }, to: { backgroundPosition: '200% 0' } },
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        '88': '22rem',
      },
      transitionTimingFunction: {
        'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
    },
  },
  plugins: [],
}
