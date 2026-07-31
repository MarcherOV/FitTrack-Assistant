import { useEffect, useState } from 'react'
import Header from './components/Header'
import WeightChart from './components/WeightChart'
import TrainingsList from './components/TrainingsList'
import MeasurementsRadar from './components/MeasurementsRadar'
import { LoadingScreen, ErrorScreen } from './components/StatusScreen'
import { useAuth } from './hooks/useAuth'
import { fetchTrainings } from './api/trainings'
import { fetchMeasurements } from './api/measurements'

export default function App() {
  const { status: authStatus, error: authError, user, dbUserId } = useAuth()

  const [dataStatus, setDataStatus] = useState('idle') // idle | loading | success | error
  const [dataError, setDataError] = useState(null)
  const [trainings, setTrainings] = useState([])
  const [measurements, setMeasurements] = useState([])

  const userId = user?.id

  async function loadDashboardData() {
    if (!dbUserId) {
      setDataStatus('error')
      setDataError('Не вдалося визначити внутрішній ID користувача в базі даних.')
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
        err?.response?.data?.detail || err.message || 'Не вдалося завантажити дані дашборду'
      )
    }
  }

  useEffect(() => {
    if (authStatus === 'success') {
      loadDashboardData()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authStatus, dbUserId])

  if (authStatus === 'loading') {
    return <LoadingScreen label="Авторизація через Telegram…" />
  }

  if (authStatus === 'error') {
    return <ErrorScreen message={authError} />
  }

  if (dataStatus === 'loading' || dataStatus === 'idle') {
    return <LoadingScreen label="Завантажуємо ваш прогрес…" />
  }

  if (dataStatus === 'error') {
    return <ErrorScreen message={dataError} onRetry={loadDashboardData} />
  }

  return (
    <div className="min-h-screen bg-tg-bg pb-8">
      <Header user={user} />

      <main className="px-4 flex flex-col gap-4 mt-2">
        <WeightChart measurements={measurements} />
        <MeasurementsRadar measurements={measurements} />
        <TrainingsList trainings={trainings} />
      </main>
    </div>
  )
}
