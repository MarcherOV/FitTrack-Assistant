import axios from 'axios'

// By default, this is an empty string (relative paths).
// This means that all requests go to the SAME origin as the page itself
// (localhost:5173 in normal development, or your ngrok domain when testing
// via the Telegram/Login Widget)—and the Vite dev proxy (see vite.config.js)
// redirects them to the backend running at 127.0.0.1:8000.
//
// If for some reason you want to access the backend directly (without a proxy)—
// set VITE_API_BASE_URL in .env, e.g., VITE_API_BASE_URL=http://127.0.0.1:8000
export const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const TOKEN_STORAGE_KEY = 'fitness_jwt_token'

export function getToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY)
}

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
})

apiClient.interceptors.request.use((config) => {
  const isAuthEndpoint = config.url?.includes('/auth/telegram')
  const token = getToken()

  if (token && !isAuthEndpoint) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearToken()
    }
    return Promise.reject(error)
  }
)
