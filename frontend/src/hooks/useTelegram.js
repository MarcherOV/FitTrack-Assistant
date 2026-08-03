import { useEffect, useMemo, useState } from 'react'

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
      setIsReady(true)
      return
    }

    tg.ready()
    tg.expand()
    setIsReady(true)
  }, [tg])

  return {
    tg,
    isReady,
    initData: tg?.initData ?? '',
    user: tg?.initDataUnsafe?.user ?? null,
  }
}
