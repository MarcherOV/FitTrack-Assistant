import { Flame } from 'lucide-react'

function getGreeting() {
  const hour = new Date().getHours()
  if (hour < 5) return 'Good night'
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good day'
  return 'Good evening'
}

export default function Header({ user, streak = 0 }) {
  const firstName = user?.first_name || 'Athlete'
  const initial = firstName.charAt(0).toUpperCase()

  return (
    <header className="safe-area-top flex items-center justify-between px-4 pt-4 pb-2">
      <div>
        <p className="text-tg-hint text-xs font-medium">{getGreeting()},</p>
        <h1 className="text-tg-text text-xl font-bold leading-tight">{firstName} 👋</h1>
      </div>

      <div className="flex items-center gap-2">
        {streak > 0 && (
          <div className="flex items-center gap-1 bg-brand-coral/10 text-brand-coral px-2.5 py-1 rounded-full text-xs font-semibold">
            <Flame size={13} strokeWidth={2.5} />
            <span>{streak} {pluralizeDays(streak)}</span>
          </div>
        )}
        {user?.photo_url ? (
          <img
            src={user.photo_url}
            alt={firstName}
            className="w-9 h-9 rounded-full object-cover border border-white/10"
          />
        ) : (
          <div className="w-9 h-9 rounded-full bg-tg-button text-tg-button-text flex items-center justify-center font-bold">
            {initial}
          </div>
        )}
      </div>
    </header>
  )
}

function pluralizeDays(count) {
  const mod10 = count % 10
  const mod100 = count % 100
  if (mod100 >= 11 && mod100 <= 14) return 'days in a row'
  if (mod10 === 1) return 'day in a row'
  if (mod10 >= 2 && mod10 <= 4) return 'days in a row'
  return 'days in a row'
}
