import { useEffect, useMemo, useState } from 'react'

/**
 * Хук-обгортка над window.Telegram.WebApp.
 * Повертає сам об'єкт tg, дані користувача (unsafe, лише для UI) та прапорець готовності.
 */
export function useTelegram() {
  const [isReady, setIsReady] = useState(false)

  const tg = useMemo(() => {
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      return window.Telegram.WebApp
    }
    return null
  }, [])

  useEffect(() => {
    if (!tg) {
      // Немає SDK (наприклад, відкрито у звичайному браузері для розробки) —
      // все одно позначаємо "готово", компоненти нижче мають fallback-логіку.
      setIsReady(true)
      return
    }

    tg.ready()
    tg.expand() // розгортає Mini App на весь екран
    setIsReady(true)
  }, [tg])

  return {
    tg,
    isReady,
    initData: tg?.initData ?? '',
    user: tg?.initDataUnsafe?.user ?? null,
  }
}
