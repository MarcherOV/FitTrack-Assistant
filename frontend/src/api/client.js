import axios from 'axios'

export const BASE_URL = 'http://127.0.0.1:8000'

const TOKEN_STORAGE_KEY = 'fitness_jwt_token'

// --- Робота з токеном ---
// Примітка: у звичайному вебі варто зберігати в httpOnly cookie,
// але для Telegram Mini App localStorage/пам'ять сесії — прийнятний варіант.
export function getToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY)
}

// --- Axios instance ---
export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
})

// Interceptor: автоматично додає Authorization: Bearer <token> до кожного запиту,
// окрім самого ендпоінта авторизації (йому токен ще не потрібен).
apiClient.interceptors.request.use((config) => {
  const isAuthEndpoint = config.url?.includes('/auth/telegram')
  const token = getToken()

  if (token && !isAuthEndpoint) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

// Interceptor відповіді: якщо бекенд повернув 401 — токен протух/невалідний,
// чистимо його, щоб додаток міг спробувати переавторизуватись.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearToken()
    }
    return Promise.reject(error)
  }
)
