/**
 * Мінімальний парсер ISO 8601 Duration (напр. "P3D", "PT1H30M", "P1DT2H").
 * Бекенд віддає тривалість тренування саме в такому форматі.
 */
export function parseIsoDuration(iso) {
  if (!iso || typeof iso !== 'string') return null

  const match = iso.match(
    /^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?$/
  )
  if (!match) return null

  const [, years, months, days, hours, minutes, seconds] = match

  return {
    years: Number(years || 0),
    months: Number(months || 0),
    days: Number(days || 0),
    hours: Number(hours || 0),
    minutes: Number(minutes || 0),
    seconds: Number(seconds || 0),
  }
}

/**
 * Форматує ISO Duration у людський короткий рядок, напр. "3 дні", "1 год 30 хв".
 */
export function formatDuration(iso) {
  const d = parseIsoDuration(iso)
  if (!d) return '—'

  const parts = []
  if (d.years) parts.push(`${d.years} р.`)
  if (d.months) parts.push(`${d.months} міс.`)
  if (d.days) parts.push(`${d.days} дн.`)
  if (d.hours) parts.push(`${d.hours} год`)
  if (d.minutes) parts.push(`${d.minutes} хв`)
  if (d.seconds) parts.push(`${d.seconds} с`)

  return parts.length ? parts.join(' ') : '0 хв'
}
