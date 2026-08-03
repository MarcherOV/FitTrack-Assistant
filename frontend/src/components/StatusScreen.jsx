import { Loader2, AlertTriangle } from 'lucide-react'

export function LoadingScreen({ label = 'Loading…' }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-3 bg-tg-bg text-tg-text px-6">
      <Loader2 className="animate-spin text-brand-lime" size={32} />
      <p className="text-tg-hint text-sm">{label}</p>
    </div>
  )
}

export function ErrorScreen({ message, onRetry }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-3 bg-tg-bg text-tg-text px-6 text-center">
      <AlertTriangle className="text-brand-coral" size={32} />
      <p className="text-tg-text font-semibold">Something went wrong</p>
      <p className="text-tg-hint text-sm max-w-xs">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 bg-tg-button text-tg-button-text text-sm font-semibold px-4 py-2 rounded-full"
        >
          Try Again
        </button>
      )}
    </div>
  )
}
