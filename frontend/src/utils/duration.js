
function parseIsoDuration(value) {
  if (typeof value !== 'string') return 0

  const match = value.match(
    /^P(?:(\d+(?:\.\d+)?)Y)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)W)?(?:(\d+(?:\.\d+)?)D)?(?:T(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?)?$/
  )
  if (!match) return 0

  const [, years, months, weeks, days, hours, minutes, seconds] = match.map((v) =>
    v ? parseFloat(v) : 0
  )

  return (
    years * 365 * 24 * 3600 +
    months * 30 * 24 * 3600 +
    weeks * 7 * 24 * 3600 +
    days * 24 * 3600 +
    hours * 3600 +
    minutes * 60 +
    seconds
  )
}

/**
 * @param {number|string} durationValue
 */
export function formatDuration(durationValue) {
  const seconds =
    typeof durationValue === 'string' ? parseIsoDuration(durationValue) : Number(durationValue) || 0

  if (!seconds || seconds <= 0) return '—'

  const totalMinutes = Math.round(seconds / 60)
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60

  if (hours > 0) {
    return minutes > 0 ? `${hours} hours ${minutes} mins` : `${hours} hours`
  }
  return `${minutes} mins`
}
