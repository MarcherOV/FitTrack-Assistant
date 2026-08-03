import { useMemo } from 'react'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { PieChart as PieIcon } from 'lucide-react'
import Card from './Card'
import { buildMuscleGroupDistribution } from '../utils/calculations'

const COLORS = ['#c6ff3d', '#7c5cff', '#ff6b6b', '#4dd0e1', '#ffb347', '#f06292', '#81c784']

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload

  return (
    <div className="bg-tg-secondary-bg border border-white/10 rounded-lg px-3 py-2 shadow-lg">
      <p className="text-tg-text text-sm font-bold">{point.name}</p>
      <p className="text-tg-hint text-xs">{point.value} sets</p>
    </div>
  )
}

export default function MuscleGroupChart({ trainings, categoriesMap }) {
  const data = useMemo(
    () => buildMuscleGroupDistribution(trainings, categoriesMap).slice(0, 7),
    [trainings, categoriesMap]
  )

  return (
    <Card title="Muscle Group Distribution" icon={PieIcon}>
      {data.length === 0 ? (
        <p className="text-tg-hint text-sm py-6 text-center">
          No data available for chart construction.
        </p>
      ) : (
        <div className="flex items-center gap-3">
          <div className="h-40 w-40 shrink-0">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  dataKey="value"
                  nameKey="name"
                  innerRadius="55%"
                  outerRadius="85%"
                  paddingAngle={2}
                  stroke="none"
                >
                  {data.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-col gap-1.5 min-w-0 flex-1">
            {data.map((d, i) => (
              <div key={d.name} className="flex items-center gap-1.5 min-w-0">
                <span
                  className="w-2 h-2 rounded-full shrink-0"
                  style={{ backgroundColor: COLORS[i % COLORS.length] }}
                />
                <span className="text-tg-text text-xs truncate flex-1">{d.name}</span>
                <span className="text-tg-hint text-xs shrink-0">{d.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  )
}
