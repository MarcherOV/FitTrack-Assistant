import { useMemo } from 'react'
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { TrendingDown, TrendingUp, Scale } from 'lucide-react'
import { format, parseISO } from 'date-fns'
import Card from './Card'

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload

  return (
    <div className="bg-tg-secondary-bg border border-white/10 rounded-lg px-3 py-2 shadow-lg">
      <p className="text-tg-hint text-[10px] mb-0.5">{point.fullDate}</p>
      <p className="text-tg-text text-sm font-bold">{point.weight} кг</p>
    </div>
  )
}

export default function WeightChart({ measurements }) {
  const chartData = useMemo(() => {
    return (measurements || [])
      // ігноруємо записи без ваги, як зазначено в задачі
      .filter((m) => m.weight !== null && m.weight !== undefined)
      .map((m) => {
        const dateObj = parseISO(m.date)
        return {
          date: format(dateObj, 'dd.MM'),
          fullDate: format(dateObj, 'dd MMMM yyyy'),
          weight: m.weight,
          timestamp: dateObj.getTime(),
        }
      })
      .sort((a, b) => a.timestamp - b.timestamp)
  }, [measurements])

  const { latest, delta, trendUp } = useMemo(() => {
    if (chartData.length === 0) return { latest: null, delta: null, trendUp: null }
    const latestVal = chartData[chartData.length - 1].weight
    const firstVal = chartData[0].weight
    const d = latestVal - firstVal
    return { latest: latestVal, delta: d, trendUp: d >= 0 }
  }, [chartData])

  return (
    <Card title="Прогрес ваги" icon={Scale}>
      {chartData.length === 0 ? (
        <p className="text-tg-hint text-sm py-6 text-center">
          Ще немає замірів ваги для побудови графіка.
        </p>
      ) : (
        <>
          <div className="flex items-end justify-between mb-2">
            <div>
              <span className="text-2xl font-bold text-tg-text">{latest}</span>
              <span className="text-tg-hint text-sm ml-1">кг</span>
            </div>
            {delta !== null && (
              <div
                className={`flex items-center gap-1 text-xs font-semibold ${
                  trendUp ? 'text-brand-coral' : 'text-brand-lime'
                }`}
              >
                {trendUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                {Math.abs(delta).toFixed(1)} кг
              </div>
            )}
          </div>

          <div className="h-40 -ml-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
                <XAxis
                  dataKey="date"
                  tick={{ fill: 'var(--tg-theme-hint-color, #8b93a1)', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis hide domain={['dataMin - 2', 'dataMax + 2']} />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="weight"
                  stroke="#c6ff3d"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#c6ff3d', strokeWidth: 0 }}
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
