import { useEffect, useRef } from 'react'

const BOT_USERNAME = 'fitness1_tracker_bot'

/**
 * Integrates the official Telegram Login Widget (script telegram-widget.js).
 * After a successful login, Telegram triggers a global callback with a
 * user object {id, first_name, last_name, username, photo_url, auth_date, hash}.
 *
 * Documentation: https://core.telegram.org/widgets/login
 */
export default function TelegramLoginWidget({ onAuth }) {
  const containerRef = useRef(null)

  useEffect(() => {
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
