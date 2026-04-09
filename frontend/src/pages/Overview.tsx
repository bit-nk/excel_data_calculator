import { DollarSign, TrendingUp, AlertTriangle, Server } from 'lucide-react'

const stats = [
  { label: 'Total Monthly Spend', value: '$2.4M', change: '+12%', icon: DollarSign, color: 'bg-blue-100 text-blue-600' },
  { label: 'Chargeback Coverage', value: '94.2%', change: '+3.1%', icon: TrendingUp, color: 'bg-green-100 text-green-600' },
  { label: 'Cost Anomalies', value: '7', change: '-2', icon: AlertTriangle, color: 'bg-yellow-100 text-yellow-600' },
  { label: 'Active Platforms', value: '6/6', change: 'Healthy', icon: Server, color: 'bg-purple-100 text-purple-600' },
]

const platformSpend = [
  { name: 'AWS', spend: '$1,245,000', pct: 52, color: 'bg-orange-500' },
  { name: 'MongoDB Atlas', spend: '$420,000', pct: 18, color: 'bg-green-500' },
  { name: 'Datadog', spend: '$380,000', pct: 16, color: 'bg-purple-500' },
  { name: 'Confluent', spend: '$210,000', pct: 9, color: 'bg-blue-500' },
  { name: 'SingleStore', spend: '$85,000', pct: 3, color: 'bg-cyan-500' },
  { name: 'Harness', spend: '$60,000', pct: 2, color: 'bg-gray-500' },
]

export default function Overview() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-driven-navy">Dashboard Overview</h2>

      {/* Stat Cards */}
      <div className="grid grid-cols-4 gap-4">
        {stats.map(({ label, value, change, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-xl p-5 shadow-sm border border-driven-gray-200">
            <div className="flex items-center justify-between mb-3">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
                <Icon size={20} />
              </div>
              <span className="text-xs font-medium text-green-600">{change}</span>
            </div>
            <div className="text-2xl font-bold text-driven-navy">{value}</div>
            <div className="text-sm text-gray-500 mt-1">{label}</div>
          </div>
        ))}
      </div>

      {/* Platform Spend Breakdown */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-driven-gray-200">
        <h3 className="text-lg font-semibold text-driven-navy mb-4">Spend by Platform</h3>
        <div className="space-y-3">
          {platformSpend.map(({ name, spend, pct, color }) => (
            <div key={name} className="flex items-center gap-4">
              <div className="w-28 text-sm font-medium text-gray-700">{name}</div>
              <div className="flex-1 bg-driven-gray-100 rounded-full h-3">
                <div className={`${color} h-3 rounded-full`} style={{ width: `${pct}%` }} />
              </div>
              <div className="w-24 text-right text-sm font-semibold text-driven-navy">{spend}</div>
              <div className="w-12 text-right text-xs text-gray-500">{pct}%</div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-driven-gray-200">
          <h3 className="text-lg font-semibold text-driven-navy mb-4">Recent Chargeback Reports</h3>
          <div className="space-y-3">
            {['2026-03', '2026-02', '2026-01'].map((period) => (
              <div key={period} className="flex items-center justify-between py-2 border-b border-driven-gray-100">
                <span className="text-sm font-medium">{period}</span>
                <span className="px-2.5 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium">
                  Approved
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-driven-gray-200">
          <h3 className="text-lg font-semibold text-driven-navy mb-4">Connector Status</h3>
          <div className="space-y-3">
            {['AWS', 'MongoDB', 'Datadog', 'Confluent', 'SingleStore', 'Harness'].map((name) => (
              <div key={name} className="flex items-center justify-between py-2 border-b border-driven-gray-100">
                <span className="text-sm font-medium">{name}</span>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-xs text-gray-500">Connected</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
