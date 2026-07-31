import { apiClient } from './client'

/**
 * Отримати сторінку тренувань користувача.
 * @param {number|string} userId
 * @param {{page?: number, pageSize?: number}} options
 */
export async function fetchTrainings(userId, { page = 1, pageSize = 5 } = {}) {
  const { data } = await apiClient.get(`/users/${userId}/trainings/`, {
    params: { page, page_size: pageSize },
  })
  return data // { items: [...] }
}
