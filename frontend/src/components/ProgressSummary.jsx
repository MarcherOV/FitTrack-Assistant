import { useMemo } from 'react'
import { Dumbbell, Flame, TrendingUp, Trophy } from 'lucide-react'
import { parseISO, isWithinInterval, subDays } from 'date-fns'
import { calculateStreak, trainingVolume } from '../utils/calculations'

function StatBox({ icon: Icon, label, value, accent = 'text-brand-lime' }) {
  return (
    <div className="bg-tg-section-bg rounded-card p-3 border border-white/5 flex flex-col gap-1.5 min-w-0">
      <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full bg-white/5 ${accent}`}>
        <Icon size={14} strokeWidth={2.25} />
      </span>
      <span className="text-tg-text text-lg font-bold leading-tight truncate">{value}</span>
      <span className="text-tg-hint text-[11px] leading-tight">{label}</span>
    </div>
  )
}

export default function ProgressSummary({ trainings, personalRecords }) {
  const stats = useMemo(() => {
    const now = new Date()
    const monthAgo = subDays(now, 30)

    const trainingsThisMonth = (trainings || []).filter((t) =>
      isWithinInterval(parseISO(t.date), { start: monthAgo, end: now })
    )

    const totalVolumeThisMonth = trainingsThisMonth.reduce(
      (sum, t) => sum + trainingVolume(t),
      0
    )

    const avgVolume =
      trainingsThisMonth.length > 0
        ? Math.round(totalVolumeThisMonth / trainingsThisMonth.length)
        : 0

    const streak = calculateStreak(trainings)
    const prCount = (personalRecords || []).filter((r) => r.isRecentPR).length

    return {
      sessionsThisMonth: trainingsThisMonth.length,
      avgVolume,
      streak,
      prCount,
    }
  }, [trainings, personalRecords])

  return (
    <div className="grid grid-cols-4 gap-2">
      <StatBox
        icon={Dumbbell}
        label="Workouts per month"
        value={stats.sessionsThisMonth}
        accent="text-brand-violet"
      />
      <StatBox
        icon={TrendingUp}
        label="Avg. Volume, kg"
        value={stats.avgVolume.toLocaleString('uk-UA')}
        accent="text-brand-lime"
      />
      <StatBox
        icon={Flame}
        label="Streak, days"
        value={stats.streak}
        accent="text-brand-coral"
      />
      <StatBox
        icon={Trophy}
        label="New Records"
        value={stats.prCount}
        accent="text-yellow-400"
      />
    </div>
  )
}
