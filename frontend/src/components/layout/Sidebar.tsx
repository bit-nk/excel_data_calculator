import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  DollarSign,
  Wallet,
  Wrench,
  TrendingUp,
  FileText,
  AlertTriangle,
  Tag,
  LogOut,
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Overview' },
  { to: '/cost-analysis', icon: DollarSign, label: 'Cost Analysis' },
  { to: '/budget', icon: Wallet, label: 'Budget Tracking' },
  { to: '/optimization', icon: Wrench, label: 'Optimization' },
  { to: '/forecasting', icon: TrendingUp, label: 'Forecasting' },
  { to: '/reports', icon: FileText, label: 'Reports' },
  { to: '/anomalies', icon: AlertTriangle, label: 'Anomalies' },
  { to: '/tags', icon: Tag, label: 'Tag Management' },
]

export default function Sidebar() {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <aside className="w-60 bg-white border-r border-driven-gray-200 flex flex-col">
      {/* Logo */}
      <div className="p-5 border-b border-driven-gray-200">
        <div className="text-lg font-bold text-driven-navy">DRIVEN</div>
        <div className="text-xs font-semibold text-driven-red tracking-wider">UNIFIED FINOPS</div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-5 py-3 text-sm transition-colors ${
                isActive
                  ? 'text-driven-red border-l-3 border-driven-red bg-red-50 font-semibold'
                  : 'text-gray-600 hover:text-driven-navy hover:bg-driven-gray-100'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-driven-gray-200">
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 w-full px-4 py-2.5 rounded-lg bg-driven-red text-white text-sm font-medium hover:bg-red-700 transition-colors"
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </aside>
  )
}
