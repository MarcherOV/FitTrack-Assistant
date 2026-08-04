import { useEffect, useMemo, useState } from 'react'
import Header from './components/Header'
import WeightChart from './components/WeightChart'
import TrainingsList from './components/TrainingsList'
import MeasurementsRadar from './components/MeasurementsRadar'
import ProgressSummary from './components/ProgressSummary'
import StrengthProgressChart from './components/StrengthProgressChart'
import PersonalRecords from './components/PersonalRecords'
import TrainingHeatmap from './components/TrainingHeatmap'
import WeeklyVolumeChart from './components/WeeklyVolumeChart'
import MuscleGroupChart from './components/MuscleGroupChart'
import { LoadingScreen, ErrorScreen } from './components/StatusScreen'
import TelegramLoginScreen from './components/TelegramLoginScreen'
import { useAuth } from './hooks/useAuth'
import { fetchTrainings, fetchAllTrainings } from './api/trainings'
import { fetchMeasurements, fetchAllMeasurements } from './api/measurements'
import { fetchCategories } from './api/categories'
import { buildExerciseHistory, buildPersonalRecords, calculateStreak } from './utils/calculations'

export default function App() {
  const { status: authStatus, error: authError, user, dbUserId, loginWithWidget } = useAuth()

  const [dataStatus, setDataStatus] = useState('idle') // idle | loading | success | error
  const [dataError, setDataError] = useState(null)

  const [trainings, setTrainings] = useState([])
  const [measurements, setMeasurements] = useState([])

  const [allTrainings, setAllTrainings] = useState([])
  const [allMeasurements, setAllMeasurements] = useState([])
  const [historyStatus, setHistoryStatus] = useState('idle') // idle | loading | success | error

  const [categoriesMap, setCategoriesMap] = useState(new Map())

  async function loadDashboardData() {
    if (!dbUserId) {
      setDataStatus('error')
      setDataError('The users internal ID could not be found in the database.')
      return
    }

    setDataStatus('loading')
    setDataError(null)

    try {
      const [trainingsRes, measurementsRes] = await Promise.all([
        fetchTrainings(dbUserId, { page: 1, pageSize: 5 }),
        fetchMeasurements(dbUserId, { page: 1, pageSize: 5 }),
      ])

      setTrainings(trainingsRes?.items || [])
      setMeasurements(measurementsRes?.items || [])
      setDataStatus('success')
    } catch (err) {
      setDataStatus('error')
      setDataError(
        err?.response?.data?.detail || err.message || 'Unable to load dashboard data'
      )
    }
  }

  async function loadHistoryData() {
    if (!dbUserId) return

    setHistoryStatus('loading')
    try {
      const [trainingsHistory, measurementsHistory] = await Promise.all([
        fetchAllTrainings(dbUserId, { pageSize: 50 }),
        fetchAllMeasurements(dbUserId, { pageSize: 50 }),
      ])
      setAllTrainings(trainingsHistory)
      setAllMeasurements(measurementsHistory)
      setHistoryStatus('success')
    } catch (err) {
      setHistoryStatus('error')
    }
  }

  async function loadCategories() {
    try {
      const categories = await fetchCategories()
      setCategoriesMap(new Map((categories || []).map((c) => [c.id, c.name])))
    } catch (err) {
    }
  }

  useEffect(() => {
    if (authStatus === 'success') {
      loadDashboardData()
      loadHistoryData()
      loadCategories()
    }
  }, [authStatus, dbUserId])

  const personalRecords = useMemo(() => {
    const historyMap = buildExerciseHistory(allTrainings)
    return buildPersonalRecords(historyMap)
  }, [allTrainings])

  const streak = useMemo(() => calculateStreak(allTrainings.length ? allTrainings : trainings), [
    allTrainings,
    trainings,
  ])

  if (authStatus === 'loading') {
    return <LoadingScreen label="Authorization via Telegram…" />
  }

  if (authStatus === 'widget-required') {
    return <TelegramLoginScreen onAuth={loginWithWidget} />
  }

  if (authStatus === 'error') {
    return <ErrorScreen message={authError} />
  }

  if (dataStatus === 'loading' || dataStatus === 'idle') {
    return <LoadingScreen label="Loading your progress…" />
  }

  if (dataStatus === 'error') {
    return <ErrorScreen message={dataError} onRetry={loadDashboardData} />
  }

  const trainingsForCharts = allTrainings.length ? allTrainings : trainings
  const measurementsForCharts = allMeasurements.length ? allMeasurements : measurements

  return (
    <div className="min-h-screen bg-tg-bg pb-8">
      <Header user={user} streak={streak} />

      <main className="px-4 flex flex-col gap-4 mt-2">
        <ProgressSummary trainings={trainingsForCharts} personalRecords={personalRecords} />

        <WeightChart measurements={measurementsForCharts} />
        <MeasurementsRadar measurements={measurementsForCharts} />

        <StrengthProgressChart trainings={trainingsForCharts} />
        <PersonalRecords trainings={trainingsForCharts} />

        <TrainingHeatmap trainings={trainingsForCharts} />
        <WeeklyVolumeChart trainings={trainingsForCharts} />
        <MuscleGroupChart trainings={trainingsForCharts} categoriesMap={categoriesMap} />

        <TrainingsList trainings={trainings} />

        {historyStatus === 'loading' && (
          <p className="text-tg-hint text-[11px] text-center -mt-2">
            Loading full history for progress charts…
          </p>
        )}
      </main>
    </div>
  )
}
