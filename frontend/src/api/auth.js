import { apiClient, setToken } from './client'

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

/**
 * Authorizes the user using data from the Telegram Login Widget (for a regular browser,
 * not within the Telegram Mini App).
 *
 * IMPORTANT: On the backend, this must be a SEPARATE endpoint from /auth/telegram, because the data
 * from the Login Widget is signed differently than the Mini App’s initData:
 *   - initData:      HMAC-SHA256(secret_key = HMAC-SHA256(bot_token, “WebAppData”), data_check_string)
 *   - Login Widget:   HMAC-SHA256(secret_key = SHA256(bot_token), data_check_string)
 * Attempting to verify the widget data using the same code as for initData will always result in a false positive.
 *
 * @param {{id:number, first_name:string, last_name?:string, username?:string,
 *          photo_url?:string, auth_date:number, hash:string}} telegramUser
 */
export async function authWithTelegramWidget(telegramUser) {
  const { data } = await apiClient.post('/api/v1/auth/telegram-widget', telegramUser)

  if (data?.access_token) {
    setToken(data.access_token)
    if (data.user_id) {
      localStorage.setItem('db_user_id', data.user_id.toString())
    }
  }

  return data
}
