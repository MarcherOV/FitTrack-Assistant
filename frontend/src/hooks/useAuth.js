import { useCallback, useEffect, useState } from 'react'
import { authWithTelegram, authWithTelegramWidget } from '../api/auth'
import { getToken } from '../api/client'
import { useTelegram } from './useTelegram'

/**
 * Керує процесом авторизації.
 *
 * status:
 *  - 'loading'        — ще визначаємось
 *  - 'success'        — авторизовані, є dbUserId
 *  - 'widget-required' — немає initData (звичайний браузер поза Telegram),
 *                         потрібно показати Telegram Login Widget
 *  - 'error'          — авторизація впала (напр. Telegram Mini App без initData,
 *                         або помилка бекенду)
 */
export function useAuth() {
  const { isReady, initData, user: tgUser } = useTelegram()
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [dbUserId, setDbUserId] = useState(null)
  const [widgetUser, setWidgetUser] = useState(null)

  useEffect(() => {
    if (!isReady) return

    if (getToken()) {
      const savedUserId = localStorage.getItem('db_user_id')
      if (savedUserId && savedUserId !== 'undefined') {
        setDbUserId(Number(savedUserId))
        setStatus('success')
        return
      }
      localStorage.removeItem('fitness_jwt_token')
    }

    if (initData) {
      authWithTelegram(initData)
        .then((data) => {
          setDbUserId(data.user_id)
          setStatus('success')
        })
        .catch((err) => {
          setStatus('error')
          setError(err?.response?.data?.detail || err.message || 'Помилка авторизації')
        })
      return
    }

    setStatus('widget-required')
  }, [isReady, initData])

  const loginWithWidget = useCallback((telegramUser) => {
    setWidgetUser(telegramUser)
    setStatus('loading')
    setError(null)

    authWithTelegramWidget(telegramUser)
      .then((data) => {
        setDbUserId(data.user_id)
        setStatus('success')
      })
      .catch((err) => {
        setStatus('error')
        setError(
          err?.response?.data?.detail || err.message || 'Помилка авторизації через Telegram'
        )
      })
  }, [])

  const user = tgUser || widgetUser

  return { status, error, user, dbUserId, loginWithWidget }
}
