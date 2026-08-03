import { useMemo } from 'react'
import { Trophy } from 'lucide-react'
import { format, parseISO } from 'date-fns'
import Card from './Card'
import { buildExerciseHistory, buildPersonalRecords } from '../utils/calculations'

export default function PersonalRecords({ trainings }) {
  const records = useMemo(() => {
    const historyMap = buildExerciseHistory(trainings)
    return buildPersonalRecords(historyMap).slice(0, 6)
  }, [trainings])

  return (
    <Card title="Personal Records" icon={Trophy}>
      {records.length === 0 ? (
        <p className="text-tg-hint text-sm py-6 text-center">
          Not enough data available for personal records. Keep training! 💪
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-2.5">
          {records.map((r) => (
            <div
              key={r.name}
              className="bg-tg-bg/50 border border-white/5 rounded-xl p-3 flex flex-col gap-1 relative"
            >
              {r.isRecentPR && (
                <span className="absolute top-2 right-2 text-[10px] bg-brand-coral/15 text-brand-coral px-1.5 py-0.5 rounded-full font-semibold">
                  new 🔥
                </span>
              )}
              <span className="text-tg-text text-xs font-semibold truncate pr-8">{r.name}</span>
              <span className="text-tg-text text-lg font-bold leading-tight">
                {r.maxWeight.weight} <span className="text-xs font-medium text-tg-hint">kg</span>
              </span>
              <span className="text-tg-hint text-[10px]">
                {r.maxWeight.reps} reps · {format(parseISO(r.maxWeight.date), 'dd.MM.yyyy')}
              </span>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
