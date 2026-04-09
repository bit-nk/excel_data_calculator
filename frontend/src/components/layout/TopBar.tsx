import { useState } from 'react'
import { Cloud, User } from 'lucide-react'
import type { CloudFilter } from '../../types'

const cloudOptions: { value: CloudFilter; label: string }[] = [
  { value: 'all', label: 'All Clouds' },
  { value: 'aws', label: 'AWS' },
  { value: 'azure', label: 'Azure' },
]

export default function TopBar() {
  const [activeCloud, setActiveCloud] = useState<CloudFilter>('all')

  return (
    <header className="h-16 bg-white border-b border-driven-gray-200 flex items-center justify-between px-6">
      {/* Left: page context */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-driven-navy rounded flex items-center justify-center">
          <span className="text-white text-xs font-bold">D</span>
        </div>
        <div>
          <h1 className="text-lg font-semibold text-driven-navy">FinOps Reports</h1>
          <p className="text-xs text-gray-400">Download comprehensive PDF reports</p>
        </div>
      </div>

      {/* Right: cloud filter + user */}
      <div className="flex items-center gap-4">
        <div className="flex bg-driven-gray-100 rounded-full p-1">
          {cloudOptions.map(({ value, label }) => (
            <button
              key={value}
              onClick={() => setActiveCloud(value)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                activeCloud === value
                  ? 'bg-driven-red text-white'
                  : 'text-gray-600 hover:text-driven-navy'
              }`}
            >
              {value === 'all' && <Cloud size={14} className="inline mr-1" />}
              {label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 bg-driven-gray-100 rounded-full">
          <User size={16} className="text-driven-red" />
          <span className="text-sm font-medium">Admin</span>
        </div>
      </div>
    </header>
  )
}
