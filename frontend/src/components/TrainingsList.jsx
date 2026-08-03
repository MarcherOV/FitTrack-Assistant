import { Dumbbell, Clock } from 'lucide-react'
import { format, parseISO } from 'date-fns'
import { uk } from 'date-fns/locale'
import Card from './Card'
import { formatDuration } from '../utils/duration'

function TrainingItem({ training }) {
  const dateObj = parseISO(training.date)

  return (
    <div className="relative pl-6 pb-5 last:pb-0 border-l-2 border-white/10 last:border-transparent">
      <span className="absolute -left-[7px] top-0 w-3 h-3 rounded-full bg-brand-violet ring-4 ring-tg-section-bg" />

      <div className="flex items-center justify-between mb-1.5">
        <span className="text-tg-text text-sm font-semibold capitalize">
          {format(dateObj, 'd MMMM', { locale: uk })}
        </span>
        <span className="flex items-center gap-1 text-tg-hint text-xs">
          <Clock size={12} />
          {formatDuration(training.duration_time)}
        </span>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {training.exercises?.map((ex) => (
          <span
            key={ex.id}
            className="bg-tg-bg/60 border border-white/5 text-tg-text text-xs px-2.5 py-1 rounded-full"
          >
            {ex.exercise?.name || 'Exercise'}:{' '}
            <span className="text-tg-hint">
              {ex.sets?.length || 0} {pluralizeSets(ex.sets?.length || 0)}
            </span>
          </span>
        ))}
        {!training.exercises?.length && (
          <span className="text-tg-hint text-xs">There are no exercises in the recording</span>
        )}
      </div>
    </div>
  )
}

function pluralizeSets(count) {
  const mod10 = count % 10
  const mod100 = count % 100
  if (mod100 >= 11 && mod100 <= 14) return 'sets'
  if (mod10 === 1) return 'set'
  if (mod10 >= 2 && mod10 <= 4) return 'sets'
  return 'sets'
}

export default function TrainingsList({ trainings }) {
  return (
    <Card title="Recent Trainings" icon={Dumbbell}>
      {!trainings?.length ? (
        <p className="text-tg-hint text-sm py-6 text-center">
          No trainings yet. Time to get started! 💪
        </p>
      ) : (
        <div>
          {trainings.map((t) => (
            <TrainingItem key={t.id} training={t} />
          ))}
        </div>
      )}
    </Card>
  )
}
