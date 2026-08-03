import { differenceInCalendarDays, parseISO, startOfWeek, format } from 'date-fns'

/**
 * Дістає вагу з об'єкта підходу, підтримуючи кілька можливих назв поля
 * (бекенди часто називають це по-різному).
 */
export function getSetWeight(set) {
  const raw =
    set?.weight ?? set?.weight_kg ?? set?.kg ?? set?.load ?? set?.value ?? 0
  return Number(raw) || 0
}

/**
 * Дістає кількість повторень з об'єкта підходу, підтримуючи кілька можливих назв поля.
 */
export function getSetReps(set) {
  const raw =
    set?.reps ??
    set?.repeats ??
    set?.rep_count ??
    set?.repetitions ??
    set?.count ??
    set?.reps_count ??
    0
  return Number(raw) || 0
}

/**
 * Розрахунок орієнтовного одноповторного максимуму (1ПМ) за формулою Еплі.
 * @param {number} weight
 * @param {number} reps
 */
export function estimateOneRepMax(weight, reps) {
  if (!weight) return 0
  if (!reps || reps === 1) return weight
  return weight * (1 + reps / 30)
}

/**
 * Тоннаж (volume) одного підходу: вага * повторення.
 */
export function setVolume(set) {
  const weight = getSetWeight(set)
  const reps = getSetReps(set)
  return weight * reps
}

/**
 * Найважчий/найкращий підхід у списку сетів за розрахунковим 1ПМ.
 */
export function bestSet(sets) {
  if (!sets?.length) return null
  return sets.reduce((best, s) => {
    const weight = getSetWeight(s)
    const reps = getSetReps(s)
    const oneRm = estimateOneRepMax(weight, reps)
    if (!best || oneRm > best.oneRm) {
      return { ...s, weight, reps, oneRm }
    }
    return best
  }, null)
}

/**
 * Загальний тоннаж тренування (сума по всіх вправах і сетах).
 */
export function trainingVolume(training) {
  return (training.exercises || []).reduce((sum, ex) => {
    return sum + (ex.sets || []).reduce((s, set) => s + setVolume(set), 0)
  }, 0)
}

/**
 * Будує мапу exerciseName -> [{date, oneRm, weight, reps, volume}]
 * відсортовану за зростанням дати, для побудови графіків прогресу сили.
 */
export function buildExerciseHistory(trainings) {
  const map = new Map()

  for (const training of trainings || []) {
    const date = training.date
    for (const ex of training.exercises || []) {
      const name = ex.exercise?.name || 'Невідома вправа'
      const muscleGroup = ex.exercise?.muscle_group || ex.exercise?.category || null
      const best = bestSet(ex.sets)
      if (!best) continue

      const entry = {
        date,
        weight: Number(best.weight) || 0,
        reps: Number(best.reps) || 0,
        oneRm: Math.round(best.oneRm * 10) / 10,
        volume: (ex.sets || []).reduce((s, set) => s + setVolume(set), 0),
        muscleGroup,
      }

      if (!map.has(name)) map.set(name, [])
      map.get(name).push(entry)
    }
  }

  for (const list of map.values()) {
    list.sort((a, b) => parseISO(a.date).getTime() - parseISO(b.date).getTime())
  }

  return map
}

/**
 * Персональні рекорди по кожній вправі: макс. вага та макс. тоннаж за сесію.
 */
export function buildPersonalRecords(exerciseHistoryMap) {
  const records = []

  for (const [name, history] of exerciseHistoryMap.entries()) {
    if (!history.length) continue

    const maxWeightEntry = history.reduce((a, b) => (b.weight > a.weight ? b : a))
    const maxVolumeEntry = history.reduce((a, b) => (b.volume > a.volume ? b : a))
    const maxOneRmEntry = history.reduce((a, b) => (b.oneRm > a.oneRm ? b : a))

    const lastEntry = history[history.length - 1]
    const isRecentPR =
      lastEntry.date === maxWeightEntry.date || lastEntry.date === maxOneRmEntry.date

    records.push({
      name,
      maxWeight: maxWeightEntry,
      maxVolume: maxVolumeEntry,
      maxOneRm: maxOneRmEntry,
      isRecentPR,
      sessionsCount: history.length,
    })
  }

  return records.sort((a, b) => b.sessionsCount - a.sessionsCount)
}

/**
 * Тижневий тоннаж по всіх тренуваннях: [{weekLabel, volume, sessions}]
 */
export function buildWeeklyVolume(trainings) {
  const weeks = new Map()

  for (const training of trainings || []) {
    const weekStart = startOfWeek(parseISO(training.date), { weekStartsOn: 1 })
    const key = format(weekStart, 'yyyy-MM-dd')
    const volume = trainingVolume(training)

    if (!weeks.has(key)) {
      weeks.set(key, { weekStart, volume: 0, sessions: 0 })
    }
    const w = weeks.get(key)
    w.volume += volume
    w.sessions += 1
  }

  return Array.from(weeks.values())
    .sort((a, b) => a.weekStart.getTime() - b.weekStart.getTime())
    .map((w) => ({
      label: format(w.weekStart, 'dd.MM'),
      volume: Math.round(w.volume),
      sessions: w.sessions,
    }))
}

/**
 * Розподіл кількості підходів по категоріях вправ (напр. "Груди", "Спина", "Ноги").
 *
 * @param {Array} trainings
 * @param {Map<number, string>} categoriesMap - мапа category_id -> назва категорії,
 *   отримана з GET /categories/. Якщо не передано або ID не знайдено — групуємо
 *   за назвою вправи як fallback.
 */
export function buildMuscleGroupDistribution(trainings, categoriesMap = new Map()) {
  const counts = new Map()

  for (const training of trainings || []) {
    for (const ex of training.exercises || []) {
      const categoryId = ex.exercise?.category_id
      const categoryName = categoryId != null ? categoriesMap.get(categoryId) : null
      const group = categoryName || ex.exercise?.name || 'Інше'
      const setsCount = ex.sets?.length || 0
      counts.set(group, (counts.get(group) || 0) + setsCount)
    }
  }

  return Array.from(counts.entries())
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
}

/**
 * Поточна серія тренувань поспіль (у календарних днях, з допуском 1 пропущеного дня
 * не рахується — рахуємо просто унікальні дні тренувань, що йдуть підряд від сьогодні/вчора).
 */
export function calculateStreak(trainings) {
  if (!trainings?.length) return 0

  const uniqueDates = Array.from(
    new Set(trainings.map((t) => format(parseISO(t.date), 'yyyy-MM-dd')))
  )
    .map((d) => parseISO(d))
    .sort((a, b) => b.getTime() - a.getTime())

  if (!uniqueDates.length) return 0

  const today = new Date()
  const diffFromToday = differenceInCalendarDays(today, uniqueDates[0])
  if (diffFromToday > 1) return 0

  let streak = 1
  for (let i = 1; i < uniqueDates.length; i++) {
    const diff = differenceInCalendarDays(uniqueDates[i - 1], uniqueDates[i])
    if (diff === 1) {
      streak += 1
    } else if (diff === 0) {
      continue
    } else {
      break
    }
  }

  return streak
}

export function buildActivityMap(trainings) {
  const map = new Map()
  for (const t of trainings || []) {
    const key = format(parseISO(t.date), 'yyyy-MM-dd')
    map.set(key, (map.get(key) || 0) + 1)
  }
  return map
}
