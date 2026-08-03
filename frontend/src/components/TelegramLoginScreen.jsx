import { Dumbbell } from 'lucide-react'
import TelegramLoginWidget from './TelegramLoginWidget'

export default function TelegramLoginScreen({ onAuth }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-tg-bg text-tg-text px-6 text-center">
      <span className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-brand-lime/10 text-brand-lime">
        <Dumbbell size={26} strokeWidth={2.25} />
      </span>

      <div>
        <p className="text-tg-text font-semibold text-lg">Fitness Tracker</p>
        <p className="text-tg-hint text-sm max-w-xs mt-1">
          Ви відкрили сторінку в звичайному браузері. Увійдіть через Telegram, щоб побачити свою
          статистику.
        </p>
      </div>

      <div className="mt-2">
        <TelegramLoginWidget onAuth={onAuth} />
      </div>

      <p className="text-tg-hint text-[11px] max-w-xs">
        Або відкрийте бота напряму в Telegram і запустіть Mini App звідти.
      </p>
    </div>
  )
}
