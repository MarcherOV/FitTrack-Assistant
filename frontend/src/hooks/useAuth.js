import { useEffect, useState } from 'react'
import { authWithTelegram } from '../api/auth'
import { getToken } from '../api/client'
import { useTelegram } from './useTelegram'

/**
 * Керує процесом авторизації: якщо валідного токена ще немає,
 * бере initData з Telegram SDK і обмінює його на JWT.
 */
export function useAuth() {
  const { isReady, initData, user } = useTelegram()
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [dbUserId, setDbUserId] = useState(null) // <-- ОСЬ ЦЬОГО РЯДКА НЕ ВИСТАЧАЛО

  useEffect(() => {
    if (!isReady) return

    // Якщо токен вже є (наприклад, з попередньої сесії) — дістаємо збережений ID
    if (getToken()) {
      const savedUserId = localStorage.getItem('db_user_id')
      if (savedUserId && savedUserId !== 'undefined') {
        setDbUserId(Number(savedUserId))
        setStatus('success')
        return
      } else {
        localStorage.removeItem('token')
      }
    }

    if (!initData) {
      setStatus('error')
      setError(
        'Не вдалося отримати initData. Відкрийте додаток через Telegram, а не напряму в браузері.'
      )
      return
    }

    authWithTelegram(initData)
      .then((data) => {
        setDbUserId(data.user_id) // Тепер змінна існує і метод спрацює успішно
        setStatus('success')
      })
      .catch((err) => {
        setStatus('error')
        setError(err?.response?.data?.detail || err.message || 'Помилка авторизації')
      })
  }, [isReady, initData])

  return { status, error, user, dbUserId }
}