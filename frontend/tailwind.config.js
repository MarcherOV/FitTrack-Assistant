/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Мапимо кольори Telegram Web App на утиліти Tailwind.
        // Якщо тема Telegram не підвантажилась (напр. запуск у звичайному браузері),
        // спрацюють fallback-значення, прописані в src/index.css
        tg: {
          bg: 'var(--tg-theme-bg-color, #0f1115)',
          'secondary-bg': 'var(--tg-theme-secondary-bg-color, #171a21)',
          text: 'var(--tg-theme-text-color, #f5f6f7)',
          hint: 'var(--tg-theme-hint-color, #8b93a1)',
          link: 'var(--tg-theme-link-color, #5eb2f7)',
          button: 'var(--tg-theme-button-color, #5eb2f7)',
          'button-text': 'var(--tg-theme-button-text-color, #ffffff)',
          'section-bg': 'var(--tg-theme-section-bg-color, #1c2028)',
          accent: 'var(--tg-theme-accent-text-color, #5eb2f7)',
          destructive: 'var(--tg-theme-destructive-text-color, #f16a6a)',
        },
        brand: {
          lime: '#c6ff3d',
          coral: '#ff6b5b',
          violet: '#7c5cff',
        },
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        card: '20px',
      },
      boxShadow: {
        card: '0 8px 24px -12px rgba(0,0,0,0.45)',
      },
    },
  },
  plugins: [],
}
