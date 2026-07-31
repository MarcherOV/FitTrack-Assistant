import { useMemo } from 'react'
import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from 'recharts'
import { Ruler } from 'lucide-react'
import { format, parseISO } from 'date-fns'
import Card from './Card'

// Людські підписи для ключів замірів, що можуть прийти з бекенду
const LABELS = {
  chest: 'Груди',
  biceps: 'Біцепс',
  waist: 'Талія',
  hips: 'Стегна (обхват)',
  thigh: 'Стегно',
  calf: 'Гомілка',
  shoulders: 'Плечі',
  neck: 'Шия',
}

function labelFor(key) {
  return LABELS[key] || key.charAt(0).toUpperCase() + key.slice(1)
}

export default function MeasurementsRadar({ measurements }) {
  // Знаходимо останній (найсвіжіший) запис, у якого є хоч якісь заміри
  const latestWithMeasurements = useMemo(() => {
    const withData = (measurements || []).filter((m) => m.measurements?.length)
    if (!withData.length) return null

    return [...withData].sort(
      (a, b) => parseISO(b.date).getTime() - parseISO(a.date).getTime()
    )[0]
  }, [measurements])

  const radarData = useMemo(() => {
    if (!latestWithMeasurements) return []

    // measurements — масив об'єктів виду { measurements: { chest: 55, ... } }
    // Зливаємо всі вкладені виміри в один плаский набір показник -> значення
    const merged = latestWithMeasurements.measurements.reduce((acc, entry) => {
      return { ...acc, ...(entry.measurements || {}) }
    }, {})

    return Object.entries(merged).map(([key, value]) => ({
      metric: labelFor(key),
      value,
    }))
  }, [latestWithMeasurements])

  return (
    <Card
      title="Заміри тіла"
      icon={Ruler}
      action={
        latestWithMeasurements && (
          <span className="text-tg-hint text-[11px]">
            {format(parseISO(latestWithMeasurements.date), 'dd.MM.yyyy')}
          </span>
        )
      }
    >
      {radarData.length === 0 ? (
        <p className="text-tg-hint text-sm py-6 text-center">
          Немає детальних замірів (обхватів) для побудови діаграми.
        </p>
      ) : (
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData} outerRadius="75%">
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis
                dataKey="metric"
                tick={{ fill: 'var(--tg-theme-hint-color, #8b93a1)', fontSize: 11 }}
              />
              <Radar
                dataKey="value"
                stroke="#7c5cff"
                fill="#7c5cff"
                fillOpacity={0.35}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  )
}
