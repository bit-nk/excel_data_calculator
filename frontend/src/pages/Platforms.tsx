import PageHeader from '../components/common/PageHeader'
import Sparkline from '../components/charts/Sparkline'
import {
  CURRENT_PERIOD,
  MONTHLY_TOTALS,
  PLATFORMS,
  calcChange,
  formatCurrency,
  formatPercent,
} from '../data/mock'

export default function Platforms() {
  const monthLabels = MONTHLY_TOTALS.map((m) => m.month)

  return (
    <div>
      <PageHeader
        title="Platform Breakdown"
        subtitle={`Detailed spend analysis per billing source — ${CURRENT_PERIOD}`}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {PLATFORMS.map((p) => {
          const change = calcChange(p.spend, p.prevSpend)
          const isUp = change >= 0
          const initial = p.name.charAt(0)

          return (
            <div
              key={p.id}
              className="relative bg-surface rounded-card border border-line p-6 overflow-hidden transition-all hover:-translate-y-0.5 hover:shadow-lift"
            >
              <span
                className="absolute left-0 top-0 bottom-0 w-1"
                style={{ background: p.color }}
              />
              <div
                className="w-[42px] h-[42px] rounded-[10px] flex items-center justify-center text-white text-lg font-extrabold mb-4"
                style={{ background: p.color }}
              >
                {initial}
              </div>
              <div className="text-[15px] font-semibold text-ink-800 mb-1">{p.name}</div>
              <div className="text-xs text-muted-soft mb-4">{p.type}</div>
              <div className="text-[26px] font-extrabold text-ink-800 tracking-[-0.5px] mb-1.5 tabular-nums">
                {formatCurrency(p.spend)}
              </div>
              <div className="flex items-center gap-3 text-xs text-muted">
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md font-semibold ${
                    isUp ? 'bg-danger-soft text-danger' : 'bg-ok-soft text-ok'
                  }`}
                >
                  {isUp ? (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="w-3 h-3">
                      <path d="M7 17L17 7M17 7H7M17 7V17" />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="w-3 h-3">
                      <path d="M7 7L17 17M17 17H7M17 17V7" />
                    </svg>
                  )}
                  {formatPercent(change)}
                </span>
                <span>vs. prev month</span>
              </div>

              <div className="h-[60px] mt-4">
                <Sparkline data={p.monthlyTrend} color={p.color} labels={monthLabels} />
              </div>

              <div className="h-px bg-line my-5" />

              <div className="text-[11px] font-semibold uppercase tracking-[0.5px] text-muted mb-2">
                Top Cost Drivers
              </div>
              <div className="space-y-1">
                {p.topItems.slice(0, 4).map((item) => (
                  <div key={item.name} className="flex items-center justify-between text-[13px] py-1">
                    <span className="text-muted">{item.name}</span>
                    <span className="font-semibold tabular-nums text-ink-800">
                      {formatCurrency(item.cost)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
