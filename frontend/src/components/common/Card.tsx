import type { ReactNode } from 'react'

interface CardProps {
  title?: ReactNode
  subtitle?: ReactNode
  actions?: ReactNode
  flush?: boolean
  className?: string
  children: ReactNode
}

export default function Card({
  title,
  subtitle,
  actions,
  flush = false,
  className = '',
  children,
}: CardProps) {
  const hasHeader = title || subtitle || actions
  return (
    <div
      className={`bg-surface rounded-card border border-line overflow-hidden transition-shadow hover:shadow-card-hover ${className}`}
    >
      {hasHeader && (
        <div className="px-6 py-5 border-b border-line flex items-center justify-between gap-4">
          <div>
            {title && <div className="text-[15px] font-semibold text-ink-800">{title}</div>}
            {subtitle && <div className="text-xs text-muted mt-0.5">{subtitle}</div>}
          </div>
          {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
        </div>
      )}
      <div className={flush ? 'p-0' : 'p-6'}>{children}</div>
    </div>
  )
}
