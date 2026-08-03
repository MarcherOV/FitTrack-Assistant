import { useMemo } from 'react'
import { CalendarDays } from 'lucide-react'
import { addDays, format, startOfWeek, subWeeks } from 'date-fns'
import Card from './Card'
import { buildActivityMap } from '../utils/calculations'

const WEEKS_TO_SHOW = 14 // ~3 months
const CELL_SIZE = 14 // px
const CELL_GAP = 4 // px
const COLUMN_STEP = CELL_SIZE + CELL_GAP

function levelForCount(count) {
  if (count <= 0) return 0
  if (count === 1) return 1
  if (count === 2) return 2
  return 3
}

// level 0 has a visible border, because fill opacity alone isn't enough —
// on a light theme it blends into the card background
const LEVEL_STYLES = [
  'bg-tg-hint/10 border border-tg-hint/25',
  'bg-brand-lime/40 border border-brand-lime/40',
  'bg-brand-lime/70 border border-brand-lime/70',
  'bg-brand-lime border border-brand-lime',
]

const WEEKDAY_LABELS = ['Mon', '', 'Wed', '', 'Fri', '', '']

export default function TrainingHeatmap({ trainings }) {
  const { weeks, monthLabels } = useMemo(() => {
    const activityMap = buildActivityMap(trainings)
    const today = new Date()
    const currentWeekStart = startOfWeek(today, { weekStartsOn: 1 })
    const firstWeekStart = subWeeks(currentWeekStart, WEEKS_TO_SHOW - 1)

    const weeksData = []
    const labels = []
    let lastMonth = null

    for (let w = 0; w < WEEKS_TO_SHOW; w++) {
      const weekStart = addDays(firstWeekStart, w * 7)
      const days = []
      for (let d = 0; d < 7; d++) {
        const date = addDays(weekStart, d)
        const key = format(date, 'yyyy-MM-dd')
        const count = activityMap.get(key) || 0
        days.push({ date, count, level: levelForCount(count) })
      }
      weeksData.push(days)

      const month = format(weekStart, 'LLL')
      if (month !== lastMonth) {
        labels.push({ index: w, label: month })
        lastMonth = month
      }
    }

    return { weeks: weeksData, monthLabels: labels }
  }, [trainings])

  const totalSessions = (trainings || []).length

  return (
    <Card
      title="Activity"
      icon={CalendarDays}
      action={<span className="text-tg-hint text-[11px]">{totalSessions} workouts</span>}
    >
      <div className="overflow-x-auto no-scrollbar -mx-1 px-1">
        <div className="inline-flex flex-col gap-2 min-w-full">
          {/* Month labels — columns line up exactly with the week columns below */}
          <div className="flex" style={{ paddingLeft: 28 }}>
            {weeks.map((_, wi) => {
              const label = monthLabels.find((m) => m.index === wi)
              return (
                <div key={wi} style={{ width: COLUMN_STEP }} className="shrink-0">
                  {label && (
                    <span className="text-tg-hint text-[10px] font-medium">
                      {label.label}
                    </span>
                  )}
                </div>
              )
            })}
          </div>

          <div className="flex gap-1">
            <div
              className="flex flex-col justify-between shrink-0"
              style={{ width: 22, height: CELL_SIZE * 7 + CELL_GAP * 6 }}
            >
              {WEEKDAY_LABELS.map((d, i) => (
                <span
                  key={i}
                  className="text-tg-hint text-[10px] font-medium leading-none"
                  style={{ height: CELL_SIZE }}
                >
                  {d}
                </span>
              ))}
            </div>

            <div className="flex" style={{ gap: CELL_GAP }}>
              {weeks.map((week, wi) => (
                <div key={wi} className="flex flex-col" style={{ gap: CELL_GAP }}>
                  {week.map((day, di) => (
                    <div
                      key={di}
                      title={`${format(day.date, 'MM/dd/yyyy')}: ${day.count} workout(s)`}
                      className={`rounded-[3px] ${LEVEL_STYLES[day.level]}`}
                      style={{ width: CELL_SIZE, height: CELL_SIZE }}
                    />
                  ))}
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-1.5 justify-end pt-0.5">
            <span className="text-tg-hint text-[10px]">less</span>
            {LEVEL_STYLES.map((c, i) => (
              <div
                key={i}
                className={`rounded-[3px] ${c}`}
                style={{ width: CELL_SIZE, height: CELL_SIZE }}
              />
            ))}
            <span className="text-tg-hint text-[10px]">more</span>
          </div>
        </div>
      </div>
    </Card>
  )
}
