import { Download } from 'lucide-react'
import PageHeader from '../components/common/PageHeader'
import Card from '../components/common/Card'
import ChargebackBars from '../components/charts/ChargebackBars'
import { PORTFOLIO_MANAGERS, formatCurrency, initials } from '../data/mock'

export default function ChargebackPage() {
  const maxTotal = Math.max(
    ...PORTFOLIO_MANAGERS.map((pm) => pm.directCost + pm.sharedAlloc + pm.foundationalFee),
  )

  return (
    <div>
      <PageHeader
        title="Portfolio Manager Chargeback"
        subtitle="Cost allocation by PM — Direct costs, shared allocation, and 20% foundational fee"
      />

      <div className="mb-6">
        <Card
          title="Chargeback Distribution"
          subtitle="Stacked cost breakdown per Portfolio Manager"
        >
          <div className="h-[320px] relative">
            <ChargebackBars />
          </div>
        </Card>
      </div>

      <Card
        title="Detailed Chargeback Table"
        subtitle="Per-PM itemized cost allocation"
        flush
        actions={
          <button
            type="button"
            className="inline-flex items-center gap-2 px-4 py-2 bg-input rounded-lg text-[13px] font-semibold text-ink-800 hover:bg-[#E0E1E5] transition-colors"
          >
            <Download size={16} strokeWidth={1.8} />
            Export CSV
          </button>
        }
      >
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-[#FAFBFC]">
                {[
                  'Portfolio Manager',
                  'Cost Code',
                  'Direct Costs',
                  'Shared Alloc.',
                  'Foundation Fee',
                  'Total',
                  'Distribution',
                ].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-3.5 text-left text-[11px] font-semibold uppercase tracking-[0.8px] text-muted border-b border-line"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {PORTFOLIO_MANAGERS.map((pm) => {
                const total = pm.directCost + pm.sharedAlloc + pm.foundationalFee
                const directPct = (pm.directCost / total) * 100
                const sharedPct = (pm.sharedAlloc / total) * 100
                const foundPct = (pm.foundationalFee / total) * 100
                const barWidth = (total / maxTotal) * 100
                return (
                  <tr key={pm.id} className="hover:bg-[#F9FAFB] transition-colors">
                    <td className="px-4 py-3.5 text-[13.5px] border-b border-[#F3F4F6]">
                      <div className="flex items-center gap-2.5">
                        <div
                          className="w-[30px] h-[30px] rounded-full flex items-center justify-center text-[11px] font-bold text-white shrink-0"
                          style={{ background: pm.color }}
                        >
                          {initials(pm.name)}
                        </div>
                        <div>
                          <div className="font-semibold text-ink-800">{pm.name}</div>
                          <div className="text-[11px] text-muted-soft font-normal">{pm.team}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3.5 text-[13.5px] border-b border-[#F3F4F6] tabular-nums text-ink-800">
                      {pm.costCode}
                    </td>
                    <td className="px-4 py-3.5 text-[13.5px] border-b border-[#F3F4F6] tabular-nums font-semibold text-ink-800">
                      {formatCurrency(pm.directCost)}
                    </td>
                    <td className="px-4 py-3.5 text-[13.5px] border-b border-[#F3F4F6] tabular-nums text-ink-800">
                      {formatCurrency(pm.sharedAlloc)}
                    </td>
                    <td className="px-4 py-3.5 text-[13.5px] border-b border-[#F3F4F6] tabular-nums text-ink-800">
                      {formatCurrency(pm.foundationalFee)}
                    </td>
                    <td className="px-4 py-3.5 text-[13.5px] border-b border-[#F3F4F6] tabular-nums font-bold text-ink-800">
                      {formatCurrency(total)}
                    </td>
                    <td className="px-4 py-3.5 border-b border-[#F3F4F6] w-[160px]">
                      <div
                        className="flex h-1.5 rounded-full overflow-hidden bg-[#F3F4F6]"
                        style={{ width: `${barWidth}%` }}
                      >
                        <div className="h-full bg-info" style={{ width: `${directPct}%` }} />
                        <div className="h-full bg-warn" style={{ width: `${sharedPct}%` }} />
                        <div className="h-full bg-accent" style={{ width: `${foundPct}%` }} />
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="pt-4 flex flex-wrap gap-4 text-xs text-muted">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-info" />
          Direct Costs
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-warn" />
          Shared Allocation
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-accent" />
          Foundational Fee (20%)
        </div>
      </div>
    </div>
  )
}
