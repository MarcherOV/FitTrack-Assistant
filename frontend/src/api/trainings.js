import { apiClient } from './client'

/**
 * @param {number|string} userId
 * @param {{page?: number, pageSize?: number}} options
 */
export async function fetchTrainings(userId, { page = 1, pageSize = 5 } = {}) {
  const { data } = await apiClient.get(`/users/${userId}/trainings/`, {
    params: { page, page_size: pageSize },
  })
  return data // { items: [...] }
}

/**
 * Loads ALL of the user's workouts (goes through all pages).
 * Required for strength progress charts, activity heatmaps, weekly volume, etc.,
 * where the last 5 entries are insufficient.
 *
 * Stops when the backend returns an empty/incomplete page, or after reaching the maxPages
 * limit to prevent the app from crashing when the history is very large.
 * @param {number|string} userId
 * @param {{pageSize?: number, maxPages?: number}} options
 */
export async function fetchAllTrainings(userId, { pageSize = 50, maxPages = 40 } = {}) {
  const all = []
  let page = 1

  while (page <= maxPages) {
    const res = await fetchTrainings(userId, { page, pageSize })
    const items = res?.items || []
    all.push(...items)

    if (items.length < pageSize) break
    page += 1
  }

  return all
}
