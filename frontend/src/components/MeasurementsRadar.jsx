import { useMemo } from 'react'
import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import { Ruler } from 'lucide-react'
import { format, parseISO } from 'date-fns'
import Card from './Card'

const LABELS = {
  chest: 'Chest',
  biceps: 'Biceps',
  waist: 'Waist',
  hips: 'Hips',
  thigh: 'Thigh',
  calf: 'Calf',
  shoulders: 'Shoulders',
  neck: 'Neck',
}

function labelFor(key) {
  return LABELS[key] || key.charAt(0).toUpperCase() + key.slice(1)
}

const CustomRenderLabel = ({ x, y, value }) => {
  return (
    <g transform={`translate(${x},${y})`}>
      <rect
        x="-14"
        y="-8"
        width="28"
        height="16"
        rx="4"
        fill="var(--tg-theme-bg-color, #ffffff)"
        fillOpacity="0.85"
      />
      <text
        x="0"
        y="3"
        fill="#7c5cff"
        fontSize="11"
        fontWeight="bold"
        textAnchor="middle"
      >
        {value}
      </text>
    </g>
  )
}

export default function MeasurementsRadar({ measurements }) {
  const latestWithMeasurements = useMemo(() => {
    const withEnoughData = (measurements || []).filter((m) => {
      if (!m.measurements) return false;
      const totalMetrics = m.measurements.reduce((acc, entry) => {
        return acc + Object.keys(entry.measurements || {}).length;
      }, 0);
      return totalMetrics >= 3;
    });

    if (!withEnoughData.length) return null;

    return [...withEnoughData].sort(
      (a, b) => parseISO(b.date).getTime() - parseISO(a.date).getTime()
    )[0]
  }, [measurements])

  const radarData = useMemo(() => {
    if (!latestWithMeasurements) return []

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
      title="Body Measurements"
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
          No detailed measurements (circumferences) available for chart construction.
        </p>
      ) : (
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData} outerRadius="65%">
              <PolarGrid stroke="rgba(139, 147, 161, 0.2)" />
              <PolarAngleAxis
                dataKey="metric"
                tick={{ fill: 'var(--tg-theme-hint-color, #8b93a1)', fontSize: 11 }}
              />
              <Tooltip
                formatter={(value) => [`${value} cm`, 'Body circumference']}
                contentStyle={{
                  backgroundColor: 'var(--tg-theme-bg-color, #ffffff)',
                  borderRadius: '8px',
                  border: 'none',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  color: 'var(--tg-theme-text-color, #000000)'
                }}
                itemStyle={{ color: '#7c5cff', fontWeight: 'bold' }}
              />
              <Radar
                name="Measurements"
                dataKey="value"
                stroke="#7c5cff"
                fill="#7c5cff"
                fillOpacity={0.35}
                strokeWidth={2}
                label={<CustomRenderLabel />}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  )
}
