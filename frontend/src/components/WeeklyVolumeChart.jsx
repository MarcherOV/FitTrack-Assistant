import { useMemo } from 'react'
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { BarChart3 } from 'lucide-react'
import Card from './Card'
import { buildWeeklyVolume } from '../utils/calculations'

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload

  return (
    <div className="bg-tg-secondary-bg border border-white/10 rounded-lg px-3 py-2 shadow-lg">
      <p className="text-tg-hint text-[10px] mb-0.5">A week from {label}</p>
      <p className="text-tg-text text-sm font-bold">
        {point.volume.toLocaleString('uk-UA')} kg
      </p>
      <p className="text-tg-hint text-xs">{point.sessions} workouts</p>
    </div>
  )
}

export default function WeeklyVolumeChart({ trainings }) {
  const data = useMemo(() => buildWeeklyVolume(trainings).slice(-10), [trainings])

  return (
    <Card title="Weekly tonnage" icon={BarChart3}>
      {data.length === 0 ? (
        <p className="text-tg-hint text-sm py-6 text-center">
          No data available for weekly volume calculation.
        </p>
      ) : (
        <div className="h-44 -ml-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
              <XAxis
                dataKey="label"
                tick={{ fill: 'var(--tg-theme-hint-color, #8b93a1)', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis hide />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
              <Bar dataKey="volume" fill="#c6ff3d" radius={[4, 4, 0, 0]} maxBarSize={28} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  )
}
