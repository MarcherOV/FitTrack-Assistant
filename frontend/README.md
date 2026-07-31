# Telegram Fitness Dashboard (Mini App)

Фронтенд для Telegram Web App — дашборд фітнес-трекера на React + Vite + Tailwind + Recharts.

## Структура проекту

```
telegram-fitness-app/
├── index.html                  # підключає telegram-web-app.js
├── src/
│   ├── main.jsx                 # точка входу
│   ├── App.jsx                  # головний дашборд, оркестрація auth + fetch
│   ├── index.css                # Tailwind + fallback-стилі під тему Telegram
│   ├── api/
│   │   ├── client.js            # axios instance + interceptor для JWT
│   │   ├── auth.js               # POST /api/v1/auth/telegram
│   │   ├── trainings.js          # GET /users/{id}/trainings/
│   │   └── measurements.js       # GET /body-info/users/{id}/measurements
│   ├── hooks/
│   │   ├── useTelegram.js        # обгортка над window.Telegram.WebApp
│   │   └── useAuth.js            # логіка обміну initData -> JWT
│   ├── components/
│   │   ├── Header.jsx            # привітання + аватар
│   │   ├── Card.jsx               # базова картка-контейнер
│   │   ├── WeightChart.jsx        # Line Chart прогресу ваги
│   │   ├── MeasurementsRadar.jsx  # Radar Chart замірів тіла
│   │   ├── TrainingsList.jsx      # Timeline тренувань
│   │   └── StatusScreen.jsx       # екрани Loading / Error
│   └── utils/
│       └── duration.js            # парсинг ISO 8601 Duration (P3D і т.п.)
```

## Запуск локально

```bash
npm install
npm run dev
```

Vite підніме дев-сервер на `http://localhost:5173` (host: true — доступний і в локальній мережі).

### Бекенд

За замовчуванням фронтенд ходить на `http://127.0.0.1:8000` (див. `src/api/client.js`, константа `BASE_URL`). Переконайтесь, що бекенд запущений і там налаштований CORS для origin вашого дев-сервера.

### Тестування всередині самого Telegram

Telegram Mini App не можна відкрити просто по `localhost` — потрібен публічний HTTPS-урл. Найпростіший спосіб для розробки:

1. Запустіть `npm run dev`.
2. Прокиньте порт назовні, напр. через `ngrok http 5173` (або Cloudflare Tunnel).
3. В @BotFather для вашого бота виконайте `/setmenubutton` (або `/newapp`) і вкажіть отриманий https-урл.
4. Відкрийте бота в Telegram і натисніть кнопку Mini App — тепер `window.Telegram.WebApp.initData` буде реальним, не порожнім.

> Без відкриття через сам Telegram-клієнт `initData` буде пустим рядком, і крок авторизації в `useAuth` покаже помилку — це очікувана поведінка, а не баг.

## Продакшн-збірка

```bash
npm run build
npm run preview   # локальний перегляд збірки
```
Готові статичні файли опиняться в `dist/` — їх можна віддавати з будь-якого HTTPS-хостингу (Nginx, Vercel, Netlify тощо), який потім і вказується як урл Mini App у BotFather.

## Що реалізовано

- **Авторизація**: `initData` з Telegram SDK → `POST /api/v1/auth/telegram` → JWT зберігається в `localStorage` → всі подальші запити йдуть з `Authorization: Bearer <token>` через axios-interceptor. При 401 токен автоматично чиститься.
- **Тема Telegram**: усі кольори прив'язані до CSS-змінних `--tg-theme-*` через `tailwind.config.js` (з fallback на темну палітру, якщо додаток відкритий поза Telegram).
- **Секція 1 — Прогрес ваги**: `LineChart` з Recharts, записи з `weight: null` відфільтровуються.
- **Секція 2 — Тренування**: timeline з датою, тривалістю (розпарсеною з ISO 8601 Duration, напр. `P3D`) і бейджами вправ у форматі `Назва: N підходів`.
- **Секція 3 — Заміри тіла**: `RadarChart` будується з останнього запису, у якого є вкладений масив `measurements` (chest/biceps/waist/…); підписи показників перекладені на українську з fallback на сирий ключ, якщо переклад невідомий.

## Що варто донастроїти під ваш бекенд

- Якщо бекенд не в `http://127.0.0.1:8000`, зміните `BASE_URL` в `src/api/client.js` (або винесіть у `.env` через `import.meta.env.VITE_API_URL`).
- Формат помилок бекенду (`detail`) — підлаштуйте парсинг у `useAuth.js` / `App.jsx`, якщо структура помилок інша.
- Список можливих ключів замірів у `MeasurementsRadar.jsx` (`LABELS`) — доповніть, якщо на бекенді з'являться нові показники.
