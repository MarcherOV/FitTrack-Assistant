import { apiClient } from './client'

/**
 * @param {number|string} userId
 * @param {{page?: number, pageSize?: number}} options
 */
export async function fetchMeasurements(userId, { page = 1, pageSize = 5 } = {}) {
  const { data } = await apiClient.get(`/body-info/users/${userId}/measurements/`, {
    params: { page, page_size: pageSize },
  })
  return data // { items: [...] }
}

/**
 *
 * @param {number|string} userId
 * @param {{pageSize?: number, maxPages?: number}} options
 */
export async function fetchAllMeasurements(userId, { pageSize = 50, maxPages = 40 } = {}) {
  const all = []
  let page = 1

  while (page <= maxPages) {
    const res = await fetchMeasurements(userId, { page, pageSize })
    const items = res?.items || []
    all.push(...items)

    if (items.length < pageSize) break
    page += 1
  }

  return all
}
