import { NavLink } from 'react-router-dom'
import { LayoutGrid, Layers, Users, FileText, BookOpen } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import NkFinOpsLogo from '../brand/NkFinOpsLogo'
import { useAuth } from '../../hooks/useAuth'
import type { Permission, UserRole } from '../../types'

interface NavItem {
  to: string
  icon: LucideIcon
  label: string
  roles?: UserRole[]
  permission?: Permission
}

interface NavSection {
  title: string
  items: NavItem[]
}

const SECTIONS: NavSection[] = [
  {
    title: 'Analytics',
    items: [
      { to: '/', icon: LayoutGrid, label: 'Executive Overview' },
      { to: '/platforms', icon: Layers, label: 'Platform Breakdown' },
      {
        to: '/chargeback',
        icon: Users,
        label: 'PM Chargeback',
        roles: ['admin', 'finance', 'portfolio_manager'],
      },
    ],
  },
  {
    title: 'Outputs',
    items: [
      { to: '/invoice', icon: FileText, label: 'Invoice Preview' },
      {
        to: '/ledger',
        icon: BookOpen,
        label: 'Accounting Ledger',
        permission: 'export_ledger',
      },
    ],
  },
]

export default function Sidebar() {
  const { hasRole, hasPermission } = useAuth()

  const visible = (item: NavItem) => {
    if (item.roles && !hasRole(...item.roles)) return false
    if (item.permission && !hasPermission(item.permission)) return false
    return true
  }

  return (
    <aside className="fixed top-0 left-0 w-[260px] h-screen bg-ink-900 flex flex-col z-40 text-white">
      <div className="px-7 py-6 border-b border-white/10">
        <NkFinOpsLogo />
        <div className="mt-1 text-[10px] font-medium uppercase tracking-[2.5px] text-white/40">
          FinOps Engine
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 overflow-y-auto scrollbar-thin">
        {SECTIONS.map((section) => {
          const items = section.items.filter(visible)
          if (items.length === 0) return null
          return (
            <div key={section.title}>
              <div className="text-[10px] font-semibold uppercase tracking-[1.5px] text-white/35 px-4 pt-6 pb-2">
                {section.title}
              </div>
              {items.map(({ to, icon: Icon, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) =>
                    [
                      'relative flex items-center gap-3 px-4 py-[11px] rounded-lg text-[13.5px] font-medium mb-0.5 transition-all',
                      isActive
                        ? 'bg-accent/15 text-accent'
                        : 'text-white/55 hover:bg-white/[0.06] hover:text-white/90',
                    ].join(' ')
                  }
                >
                  {({ isActive }) => (
                    <>
                      {isActive && (
                        <span className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-accent rounded-r" />
                      )}
                      <Icon size={18} strokeWidth={1.8} className={isActive ? 'opacity-100' : 'opacity-80'} />
                      <span>{label}</span>
                    </>
                  )}
                </NavLink>
              ))}
            </div>
          )
        })}
      </nav>

      <div className="px-5 py-4 border-t border-white/10">
        <div className="flex items-center gap-2 text-[12px] text-white/40">
          <span className="w-[7px] h-[7px] rounded-full bg-ok animate-pulseDot" />
          All systems connected
        </div>
      </div>
    </aside>
  )
}
