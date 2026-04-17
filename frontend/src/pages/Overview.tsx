import { DollarSign, TrendingUp, Layers, Users, Check } from 'lucide-react'
import PageHeader from '../components/common/PageHeader'
import Card from '../components/common/Card'
import KpiCard from '../components/dashboard/KpiCard'
import SpendTrendChart from '../components/charts/SpendTrendChart'
import PlatformDonut from '../components/charts/PlatformDonut'
import {
  CONNECTIONS,
  CURRENT_PERIOD,
  MONTHLY_TOTALS,
  PLATFORMS,
  PORTFOLIO_MANAGERS,
  calcChange,
  formatCurrency,
  formatPercent,
} from '../data/mock'

export default function Overview() {
  const totalSpend = PLATFORMS.reduce((s, p) => s + p.spend, 0)
  const prevTotal = PLATFORMS.reduce((s, p) => s + p.prevSpend, 0)
  const change = calcChange(totalSpend, prevTotal)
  const prevMonth = MONTHLY_TOTALS[MONTHLY_TOTALS.length - 2]?.month ?? 'prev month'

  return (
    <div>
      <PageHeader
        title="Executive Overview"
        subtitle={`Cloud infrastructure spend summary for ${CURRENT_PERIOD}`}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 mb-7">
        <KpiCard
          label="Total Cloud Spend"
          icon={<DollarSign />}
          value={formatCurrency(totalSpend)}
          accentColor="#E33529"
          trend={{ direction: change >= 0 ? 'up' : 'down', label: formatPercent(change) }}
        />
        <KpiCard
          label="Month-over-Month"
          icon={<TrendingUp />}
          value={formatPercent(change)}
          accentColor="#10B981"
          trend={{ direction: change >= 0 ? 'up' : 'down', label: `vs. ${prevMonth}` }}
        />
        <KpiCard
          label="Active Platforms"
          icon={<Layers />}
          value={PLATFORMS.length.toString()}
          accentColor="#3B82F6"
          tag={{ variant: 'green', label: 'All Connected' }}
        />
        <KpiCard
          label="Portfolio Managers"
          icon={<Users />}
          value={PORTFOLIO_MANAGERS.length.toString()}
          accentColor="#8B5CF6"
          tag={{ variant: 'blue', label: 'Active Chargebacks' }}
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[2fr_1fr] gap-5 mb-7">
        <Card title="Spend Trend" subtitle="6-month rolling total cloud spend">
          <div className="h-[280px] relative">
            <SpendTrendChart />
          </div>
        </Card>

        <Card title="Spend by Platform" subtitle={`${CURRENT_PERIOD} distribution`}>
          <div className="h-[220px] relative">
            <PlatformDonut />
          </div>
          <div className="flex flex-wrap justify-center gap-4 mt-3">
            {PLATFORMS.map((p) => (
              <div key={p.id} className="flex items-center gap-1.5 text-xs text-muted">
                <span
                  className="w-2 h-2 rounded-full shrink-0"
                  style={{ background: p.color }}
                />
                {p.name.replace('Amazon Web Services', 'AWS').replace('MongoDB Atlas', 'MongoDB')}
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card
        title="Data Source Connections"
        subtitle="Real-time ingestion pipeline status"
        actions={
          <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-ok-soft text-ok text-[11px] font-semibold rounded-md">
            <Check size={12} strokeWidth={2} />
            All Healthy
          </span>
        }
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {CONNECTIONS.map((c) => (
            <div
              key={c.name}
              className="flex items-center gap-2.5 px-4 py-3 bg-[#FAFBFC] border border-line rounded-lg"
            >
              <span className="w-2 h-2 rounded-full bg-ok shrink-0" />
              <span className="text-[13px] font-medium text-ink-800">{c.name}</span>
              <span className="text-[11px] text-muted-soft ml-auto">{c.lastSync}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
