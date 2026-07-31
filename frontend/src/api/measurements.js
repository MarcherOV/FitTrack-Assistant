import { apiClient } from './client'

/**
 * Отримати сторінку замірів тіла користувача.
 * @param {number|string} userId
 * @param {{page?: number, pageSize?: number}} options
 */
export async function fetchMeasurements(userId, { page = 1, pageSize = 5 } = {}) {
  const { data } = await apiClient.get(`/body-info/users/${userId}/measurements`, {
    params: { page, page_size: pageSize },
  })
  return data // { items: [...] }
}
