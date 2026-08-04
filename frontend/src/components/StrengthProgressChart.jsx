import { useMemo, useState } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { TrendingUp } from 'lucide-react'
import { format, parseISO } from 'date-fns'
import Card from './Card'
import { buildExerciseHistory } from '../utils/calculations'

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload

  return (
    <div className="bg-tg-secondary-bg border border-white/10 rounded-lg px-3 py-2 shadow-lg">
      <p className="text-tg-hint text-[10px] mb-1">{point.fullDate}</p>
      <p className="text-tg-text text-sm font-bold">~{point.oneRm} kg · 1RM</p>
      <p className="text-tg-hint text-xs">
        {point.weight} kg × {point.reps} reps
      </p>
    </div>
  )
}

export default function StrengthProgressChart({ trainings }) {
  const historyMap = useMemo(() => buildExerciseHistory(trainings), [trainings])

  const exerciseNames = useMemo(
    () =>
      Array.from(historyMap.entries())
        .filter(([, list]) => list.length >= 2)
        .sort((a, b) => b[1].length - a[1].length)
        .map(([name]) => name),
    [historyMap]
  )

  const [selected, setSelected] = useState(null)
  const activeExercise = selected && exerciseNames.includes(selected) ? selected : exerciseNames[0]

  const chartData = useMemo(() => {
    if (!activeExercise) return []
    return historyMap.get(activeExercise).map((e) => ({
      date: format(parseISO(e.date), 'dd.MM'),
      fullDate: format(parseISO(e.date), 'dd MMMM yyyy'),
      oneRm: e.oneRm,
      weight: e.weight,
      reps: e.reps,
    }))
  }, [activeExercise, historyMap])

  return (
    <Card title="The Progress of Strength" icon={TrendingUp}>
      {exerciseNames.length === 0 ? (
        <p className="text-tg-hint text-sm py-6 text-center">
          Not enough data available for strength progress chart. At least 2 training sessions with the same exercise are required.
        </p>
      ) : (
        <>
          <div className="flex gap-1.5 overflow-x-auto pb-3 -mx-1 px-1 no-scrollbar">
            {exerciseNames.map((name) => (
              <button
                key={name}
                onClick={() => setSelected(name)}
                className={`shrink-0 text-xs font-semibold px-3 py-1.5 rounded-full border transition-colors ${
                  name === activeExercise
                    ? 'bg-brand-lime text-tg-bg border-brand-lime'
                    : 'bg-transparent text-tg-hint border-white/10'
                }`}
              >
                {name}
              </button>
            ))}
          </div>

          <p className="text-tg-hint text-[11px] mb-2">
            Estimated one-rep maximum (1RM), calculated using the Epley formula
          </p>

          <div className="h-48 -ml-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(139, 147, 161, 0.1)" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fill: 'var(--tg-theme-hint-color, #8b93a1)', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis hide domain={['dataMin - 5', 'dataMax + 5']} />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="oneRm"
                  stroke="#7c5cff"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#7c5cff', strokeWidth: 0 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </Card>
  )
}
