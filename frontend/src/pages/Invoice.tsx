import { useState } from 'react'
import { Check, Download, Printer } from 'lucide-react'
import PageHeader from '../components/common/PageHeader'
import {
  CURRENT_PERIOD,
  LAST_UPDATED,
  PLATFORMS,
  PORTFOLIO_MANAGERS,
  formatCurrency,
  initials,
} from '../data/mock'

export default function InvoicePage() {
  const [selectedId, setSelectedId] = useState(PORTFOLIO_MANAGERS[1]?.id ?? PORTFOLIO_MANAGERS[0].id)
  const pm = PORTFOLIO_MANAGERS.find((p) => p.id === selectedId) ?? PORTFOLIO_MANAGERS[0]
  const total = pm.directCost + pm.sharedAlloc + pm.foundationalFee

  const totalPlatformSpend = PLATFORMS.reduce((s, p) => s + p.spend, 0)
  const platformLines = PLATFORMS.map((p) => ({
    name: p.name,
    amount: Math.round(pm.directCost * (p.spend / totalPlatformSpend)),
  }))

  return (
    <div>
      <PageHeader
        title="Invoice Preview"
        subtitle="Select a Portfolio Manager to view their itemized chargeback invoice"
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {PORTFOLIO_MANAGERS.map((p) => {
          const active = p.id === selectedId
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => setSelectedId(p.id)}
              className={`p-4 rounded-lg border-2 cursor-pointer text-center transition-all ${
                active ? 'border-accent bg-accent-soft' : 'border-line hover:border-accent hover:bg-accent-soft'
              }`}
            >
              <div
                className="w-9 h-9 mx-auto rounded-full flex items-center justify-center text-[13px] font-bold text-white"
                style={{ background: p.color }}
              >
                {initials(p.name)}
              </div>
              <div className="mt-2 text-[13px] font-semibold text-ink-800">{p.name}</div>
              <div className="text-[11px] text-muted">{p.team}</div>
            </button>
          )
        })}
      </div>

      <div className="bg-surface rounded-card border border-line max-w-[800px] mx-auto overflow-hidden">
        <div className="px-10 py-10 flex items-start justify-between border-b border-line">
          <div>
            <div className="text-[28px] font-extrabold text-ink-800 tracking-[-0.5px]">
              Chargeback Invoice
            </div>
            <div className="text-[13px] text-muted mt-1">{CURRENT_PERIOD} Billing Cycle</div>
          </div>
          <div className="inline-flex items-center gap-1 px-3.5 py-1.5 bg-ok-soft text-ok text-xs font-semibold rounded-full">
            <Check size={12} strokeWidth={2} />
            Finalized
          </div>
        </div>

        <div className="grid grid-cols-2 gap-8 px-10 py-8 border-b border-line">
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[1px] text-muted-soft mb-1">
              Billed To
            </div>
            <div className="text-sm font-medium text-ink-800">{pm.name}</div>
            <div className="text-xs text-muted">
              {pm.team} — {pm.costCode}
            </div>
          </div>
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[1px] text-muted-soft mb-1">
              Invoice Number
            </div>
            <div className="text-sm font-medium text-ink-800">INV-2026-02-{pm.costCode}</div>
            <div className="text-xs text-muted">Generated: Mar 1, 2026</div>
          </div>
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[1px] text-muted-soft mb-1">
              Billing Period
            </div>
            <div className="text-sm font-medium text-ink-800">Feb 1 — Feb 28, 2026</div>
          </div>
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[1px] text-muted-soft mb-1">
              Total Due
            </div>
            <div className="text-[20px] font-extrabold text-accent tabular-nums">
              {formatCurrency(total)}
            </div>
          </div>
        </div>

        <div className="px-10">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="text-left py-4 text-[11px] font-semibold uppercase tracking-[0.8px] text-muted border-b border-line">
                  Description
                </th>
                <th className="text-right py-4 text-[11px] font-semibold uppercase tracking-[0.8px] text-muted border-b border-line">
                  Amount
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colSpan={2}>
                  <div className="text-[12px] font-semibold text-accent pt-5 pb-1">
                    Direct Platform Costs
                  </div>
                </td>
              </tr>
              {platformLines.map((pl) => (
                <tr key={pl.name}>
                  <td className="py-3.5 text-sm border-b border-[#F3F4F6]">{pl.name}</td>
                  <td className="py-3.5 text-sm text-right font-semibold tabular-nums border-b border-[#F3F4F6]">
                    {formatCurrency(pl.amount)}
                  </td>
                </tr>
              ))}
              <tr>
                <td className="py-3.5 text-sm font-semibold border-b border-[#F3F4F6]">
                  Subtotal — Direct Costs
                </td>
                <td className="py-3.5 text-sm text-right font-bold tabular-nums border-b border-[#F3F4F6]">
                  {formatCurrency(pm.directCost)}
                </td>
              </tr>

              <tr>
                <td colSpan={2}>
                  <div className="text-[12px] font-semibold text-accent pt-5 pb-1">
                    Shared Cost Allocation
                  </div>
                </td>
              </tr>
              <tr>
                <td className="py-3.5 text-sm border-b border-[#F3F4F6]">
                  Platform Engineering (pro-rata)
                </td>
                <td className="py-3.5 text-sm text-right font-semibold tabular-nums border-b border-[#F3F4F6]">
                  {formatCurrency(Math.round(pm.sharedAlloc * 0.77))}
                </td>
              </tr>
              <tr>
                <td className="py-3.5 text-sm border-b border-[#F3F4F6]">
                  Unallocated Infrastructure
                </td>
                <td className="py-3.5 text-sm text-right font-semibold tabular-nums border-b border-[#F3F4F6]">
                  {formatCurrency(Math.round(pm.sharedAlloc * 0.23))}
                </td>
              </tr>
              <tr>
                <td className="py-3.5 text-sm font-semibold border-b border-[#F3F4F6]">
                  Subtotal — Shared Costs
                </td>
                <td className="py-3.5 text-sm text-right font-bold tabular-nums border-b border-[#F3F4F6]">
                  {formatCurrency(pm.sharedAlloc)}
                </td>
              </tr>

              <tr>
                <td colSpan={2}>
                  <div className="text-[12px] font-semibold text-accent pt-5 pb-1">
                    Foundational Management Fee
                  </div>
                </td>
              </tr>
              <tr>
                <td className="py-3.5 text-sm border-b border-[#F3F4F6]">
                  20% of Direct Costs ({formatCurrency(pm.directCost)} × 0.20)
                </td>
                <td className="py-3.5 text-sm text-right font-semibold tabular-nums border-b border-[#F3F4F6]">
                  {formatCurrency(pm.foundationalFee)}
                </td>
              </tr>

              <tr>
                <td className="pt-4 text-base font-bold border-t-2 border-ink-800">
                  TOTAL CHARGEBACK
                </td>
                <td className="pt-4 text-base text-right font-bold tabular-nums border-t-2 border-ink-800">
                  {formatCurrency(total)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between px-10 py-8 mt-4 bg-[#FAFBFC]">
          <div className="text-xs text-muted-soft">
            Auto-generated by NkFinOps Engine • {LAST_UPDATED}
          </div>
          <div className="flex gap-2">
            <button className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-input text-[13px] font-semibold text-ink-800 hover:bg-[#E0E1E5] transition-colors">
              <Printer size={16} strokeWidth={1.8} />
              Print
            </button>
            <button className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-accent text-white text-[13px] font-semibold hover:bg-accent-hover hover:shadow-accent transition-all">
              <Download size={16} strokeWidth={1.8} />
              Export PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
