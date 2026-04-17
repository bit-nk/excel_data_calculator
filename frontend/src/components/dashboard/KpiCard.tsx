import type { ReactNode } from 'react'

interface Props {
  label: string
  icon: ReactNode
  value: string
  accentColor: string
  trend?: {
    direction: 'up' | 'down'
    label: string
  }
  tag?: {
    variant: 'green' | 'blue' | 'amber'
    label: string
  }
}

const tagVariant: Record<'green' | 'blue' | 'amber', string> = {
  green: 'bg-ok-soft text-ok',
  blue: 'bg-info-soft text-info',
  amber: 'bg-warn-soft text-warn',
}

export default function KpiCard({ label, icon, value, accentColor, trend, tag }: Props) {
  return (
    <div
      className="group relative bg-surface rounded-card border border-line p-6 overflow-hidden transition-all hover:-translate-y-0.5 hover:shadow-lift"
    >
      <span
        className="absolute inset-x-0 top-0 h-[3px] opacity-0 transition-opacity group-hover:opacity-100"
        style={{ background: accentColor }}
      />
      <div className="flex items-center gap-2 text-[12px] font-semibold uppercase tracking-[0.8px] text-muted mb-2.5">
        <span className="opacity-50 [&>svg]:w-4 [&>svg]:h-4">{icon}</span>
        {label}
      </div>
      <div className="text-[30px] font-extrabold text-ink-800 tracking-[-1px] leading-none mb-2 tabular-nums">
        {value}
      </div>
      {trend && (
        <span
          className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-md ${
            trend.direction === 'up' ? 'bg-danger-soft text-danger' : 'bg-ok-soft text-ok'
          }`}
        >
          {trend.direction === 'up' ? (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="w-3 h-3">
              <path d="M7 17L17 7M17 7H7M17 7V17" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="w-3 h-3">
              <path d="M7 7L17 17M17 17H7M17 17V7" />
            </svg>
          )}
          {trend.label}
        </span>
      )}
      {tag && (
        <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1 rounded-md ${tagVariant[tag.variant]}`}>
          {tag.label}
        </span>
      )}
    </div>
  )
}
