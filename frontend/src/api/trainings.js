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

/**
 * Підвантажує ВСІ тренування користувача (проходить усі сторінки).
 * Потрібно для графіків прогресу сили, теплокарти активності, тижневого тоннажу тощо,
 * де недостатньо останніх 5 записів.
 *
 * Зупиняється, коли бекенд повертає порожню/неповну сторінку, або після maxPages
 * запобіжника, щоб не заблокувати додаток при дуже великій історії.
 *
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
