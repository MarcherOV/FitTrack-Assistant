import { apiClient } from './client'

/**
 * @returns {Promise<Array<{id: number, name: string}>>}
 */
export async function fetchCategories() {
  const { data } = await apiClient.get('/categories/')
  return data
}
