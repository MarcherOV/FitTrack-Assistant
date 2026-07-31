import { apiClient, setToken } from './client'

/**
 * Авторизує користувача через Telegram initData.
 * Відправляє initData на бекенд, отримує JWT і зберігає його.
 *
 * @param {string} initData - сирий рядок window.Telegram.WebApp.initData
 * @returns {Promise<{access_token: string, token_type: string}>}
 */
export async function authWithTelegram(initData) {
  const { data } = await apiClient.post('/api/v1/auth/telegram', {
    initData,
  })

  if (data?.access_token) {
    setToken(data.access_token)
    if (data.user_id) {
      localStorage.setItem('db_user_id', data.user_id.toString())
    }
  }

  return data
}
