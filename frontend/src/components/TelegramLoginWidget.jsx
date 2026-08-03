import { useEffect, useRef } from 'react'

// Замініть на юзернейм вашого бота БЕЗ символу @
const BOT_USERNAME = 'fitness1_tracker_bot'

/**
 * Вбудовує офіційний Telegram Login Widget (script telegram-widget.js).
 * Після успішного логіну Telegram викликає глобальний callback з об'єктом
 * користувача {id, first_name, last_name, username, photo_url, auth_date, hash}.
 *
 * Документація: https://core.telegram.org/widgets/login
 */
export default function TelegramLoginWidget({ onAuth }) {
  const containerRef = useRef(null)

  useEffect(() => {
    // Глобальний callback, на який посилається сам скрипт віджета
    // (data-onauth="onTelegramAuth(user)")
    window.onTelegramAuth = (user) => {
      onAuth(user)
    }

    const script = document.createElement('script')
    script.src = 'https://telegram.org/js/telegram-widget.js?22'
    script.async = true
    script.setAttribute('data-telegram-login', BOT_USERNAME)
    script.setAttribute('data-size', 'large')
    script.setAttribute('data-radius', '12')
    script.setAttribute('data-onauth', 'onTelegramAuth(user)')
    script.setAttribute('data-request-access', 'write')

    const container = containerRef.current
    container?.appendChild(script)

    return () => {
      delete window.onTelegramAuth
      if (container) container.innerHTML = ''
    }
  }, [onAuth])

  return <div ref={containerRef} className="flex justify-center" />
}
