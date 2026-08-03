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
import { TrendingDown, TrendingUp, Scale } from 'lucide-react'
import { format, parseISO, subDays } from 'date-fns'
import Card from './Card'

const RANGES = [
  { key: '30', label: '30 days', days: 30 },
  { key: '90', label: '90 days', days: 90 },
  { key: 'all', label: 'All', days: null },
]

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload

  return (
    <div className="bg-tg-secondary-bg border border-white/10 rounded-lg px-3 py-2 shadow-lg">
      <p className="text-tg-hint text-[10px] mb-0.5">{point.fullDate}</p>
      <p className="text-tg-text text-sm font-bold">{point.weight} kg</p>
      {point.waist != null && (
        <p className="text-brand-violet text-xs font-semibold">Waist: {point.waist} cm</p>
      )}
    </div>
  )
}

export default function WeightChart({ measurements }) {
  const [range, setRange] = useState('90')

  const chartData = useMemo(() => {
    const activeRange = RANGES.find((r) => r.key === range)
    const cutoff = activeRange?.days ? subDays(new Date(), activeRange.days) : null

    return (measurements || [])
      .filter((m) => m.weight !== null && m.weight !== undefined)
      .map((m) => {
        const dateObj = parseISO(m.date)
        const waistEntry = m.measurements?.find((e) =>
          Object.prototype.hasOwnProperty.call(e.measurements || {}, 'waist')
        )
        return {
          date: format(dateObj, 'dd.MM'),
          fullDate: format(dateObj, 'dd MMMM yyyy'),
          weight: m.weight,
          waist: waistEntry?.measurements?.waist ?? null,
          timestamp: dateObj.getTime(),
        }
      })
      .filter((d) => !cutoff || d.timestamp >= cutoff.getTime())
      .sort((a, b) => a.timestamp - b.timestamp)
  }, [measurements, range])

  const hasWaistData = chartData.some((d) => d.waist != null)

  const { latest, delta, trendUp } = useMemo(() => {
    if (chartData.length === 0) return { latest: null, delta: null, trendUp: null }
    const latestVal = chartData[chartData.length - 1].weight
    const firstVal = chartData[0].weight
    const d = latestVal - firstVal
    return { latest: latestVal, delta: d, trendUp: d >= 0 }
  }, [chartData])

  return (
    <Card
      title="Weight Progress"
      icon={Scale}
      action={
        <div className="flex bg-tg-bg/50 rounded-full p-0.5 gap-0.5">
          {RANGES.map((r) => (
            <button
              key={r.key}
              onClick={() => setRange(r.key)}
              className={`text-[10px] font-semibold px-2 py-1 rounded-full transition-colors ${
                range === r.key
                  ? 'bg-brand-lime text-tg-bg'
                  : 'text-tg-hint'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      }
    >
      {chartData.length === 0 ? (
        <p className="text-tg-hint text-sm py-6 text-center">
          No weight measurements available for chart construction.
        </p>
      ) : (
        <>
          <div className="flex items-end justify-between mb-2">
            <div>
              <span className="text-2xl font-bold text-tg-text">{latest}</span>
              <span className="text-tg-hint text-sm ml-1">kg</span>
            </div>
            {delta !== null && (
              <div
                className={`flex items-center gap-1 text-xs font-semibold ${
                  trendUp ? 'text-brand-coral' : 'text-brand-lime'
                }`}
              >
                {trendUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                {Math.abs(delta).toFixed(1)} kg over the period
              </div>
            )}
          </div>

          <div className="h-40 -ml-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(139, 147, 161, 0.1)" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fill: 'var(--tg-theme-hint-color, #8b93a1)', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis hide domain={['dataMin - 2', 'dataMax + 2']} yAxisId="weight" />
                {hasWaistData && (
                  <YAxis hide domain={['dataMin - 5', 'dataMax + 5']} yAxisId="waist" />
                )}
                <Tooltip content={<CustomTooltip />} />
                <Line
                  yAxisId="weight"
                  type="monotone"
                  dataKey="weight"
                  stroke="#c6ff3d"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#c6ff3d', strokeWidth: 0 }}
                  activeDot={{ r: 5 }}
                  connectNulls
                />
                {hasWaistData && (
                  <Line
                    yAxisId="waist"
                    type="monotone"
                    dataKey="waist"
                    stroke="#7c5cff"
                    strokeWidth={2}
                    strokeDasharray="4 3"
                    dot={{ r: 2.5, fill: '#7c5cff', strokeWidth: 0 }}
                    connectNulls
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
          {hasWaistData && (
            <div className="flex items-center gap-3 mt-1 justify-center">
              <span className="flex items-center gap-1 text-[10px] text-tg-hint">
                <span className="w-2 h-0.5 bg-brand-lime inline-block" /> Weight
              </span>
              <span className="flex items-center gap-1 text-[10px] text-tg-hint">
                <span className="w-2 h-0.5 bg-brand-violet inline-block" /> Waist
              </span>
            </div>
          )}
        </>
      )}
    </Card>
  )
}
