import { useLocation } from 'react-router-dom'
import { Calendar, LogOut } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { CURRENT_PERIOD, initials } from '../../data/mock'

const TITLES: Record<string, string> = {
  '/': 'Executive Overview',
  '/platforms': 'Platform Breakdown',
  '/chargeback': 'PM Chargeback',
  '/invoice': 'Invoice Preview',
  '/ledger': 'Accounting Ledger',
}

export default function TopBar() {
  const { pathname } = useLocation()
  const { user, logout } = useAuth()

  const title = TITLES[pathname] ?? 'FinOps Dashboard'
  const avatar = user ? initials(user.full_name) : 'BS'

  return (
    <header className="sticky top-0 z-20 h-16 bg-surface border-b border-line flex items-center justify-between px-8">
      <div className="flex items-center gap-4">
        <span className="text-[15px] font-semibold text-ink-800">{title}</span>
      </div>

      <div className="flex items-center gap-4">
        <div className="inline-flex items-center gap-1.5 px-3 py-[5px] bg-ok-soft text-ok text-xs font-semibold rounded-full">
          <span className="w-1.5 h-1.5 rounded-full bg-current" />
          Live
        </div>

        <button
          type="button"
          className="flex items-center gap-2 px-[14px] py-[7px] bg-input rounded-lg text-[13px] font-medium text-ink-800 hover:bg-[#E5E6EA] transition-colors"
        >
          <Calendar size={16} className="text-muted" strokeWidth={1.8} />
          {CURRENT_PERIOD}
        </button>

        <button
          type="button"
          onClick={logout}
          title={user?.full_name ?? 'Sign out'}
          className="w-[34px] h-[34px] rounded-full bg-gradient-to-br from-accent to-[#06B6D4] flex items-center justify-center text-white text-[13px] font-bold hover:shadow-accent transition-shadow relative group"
        >
          {avatar}
          <LogOut
            size={14}
            className="absolute inset-0 m-auto opacity-0 group-hover:opacity-100 transition-opacity bg-ink-900 rounded-full p-0.5"
          />
        </button>
      </div>
    </header>
  )
}
