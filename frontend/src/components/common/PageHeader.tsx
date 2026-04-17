interface Props {
  title: string
  subtitle?: string
  actions?: React.ReactNode
}

export default function PageHeader({ title, subtitle, actions }: Props) {
  return (
    <div className="mb-7 flex items-start justify-between gap-4">
      <div>
        <h1 className="text-[24px] font-bold text-ink-800 tracking-[-0.3px] leading-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="text-sm text-muted mt-1 font-normal">{subtitle}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
    </div>
  )
}
