import { useMemo, useState } from 'react'
import { Check, Download, Send } from 'lucide-react'
import PageHeader from '../components/common/PageHeader'
import Card from '../components/common/Card'
import { useAuth } from '../hooks/useAuth'
import {
  downloadLedger,
  getChargebackReports,
  markLedgerSent,
} from '../services/api'
import {
  CURRENT_PERIOD,
  PORTFOLIO_MANAGERS,
  formatCurrency,
} from '../data/mock'

type Format = 'csv' | 'json' | 'xml'

const FORMATS: Format[] = ['csv', 'json', 'xml']

// SoW §4.3 contracts the accounting ledger output in CSV/ledger-file form.
// CSV is the canonical export the backend produces; JSON/XML remain as
// preview-only alternate renderings of the same journal.
function buildCsvPreview(): string {
  const header = 'Date,GL_Account,Cost_Center,Description,Debit,Credit,PM_Name,Team,Cost_Code'
  const rows = PORTFOLIO_MANAGERS.flatMap((pm) => [
    `2026-02-28,6100-CLOUD,${pm.costCode},Direct Cloud Costs - ${pm.team},${pm.directCost.toFixed(2)},,${pm.name},${pm.team},${pm.costCode}`,
    `2026-02-28,6200-SHARED,${pm.costCode},Shared Cost Allocation - ${pm.team},${pm.sharedAlloc.toFixed(2)},,${pm.name},${pm.team},${pm.costCode}`,
    `2026-02-28,6300-FNDTN,${pm.costCode},Foundational Mgmt Fee (20%) - ${pm.team},${pm.foundationalFee.toFixed(2)},,${pm.name},${pm.team},${pm.costCode}`,
  ])
  return [header, ...rows].join('\n')
}

function buildJsonPreview(): string {
  const lines = PORTFOLIO_MANAGERS.flatMap((pm) => [
    {
      date: '2026-02-28',
      gl_account: '6100-CLOUD',
      cost_center: pm.costCode,
      description: `Direct Cloud Costs - ${pm.team}`,
      debit: pm.directCost.toFixed(2),
      pm_name: pm.name,
      team: pm.team,
      cost_code: pm.costCode,
    },
    {
      date: '2026-02-28',
      gl_account: '6200-SHARED',
      cost_center: pm.costCode,
      description: `Shared Cost Allocation - ${pm.team}`,
      debit: pm.sharedAlloc.toFixed(2),
      pm_name: pm.name,
      team: pm.team,
      cost_code: pm.costCode,
    },
    {
      date: '2026-02-28',
      gl_account: '6300-FNDTN',
      cost_center: pm.costCode,
      description: `Foundational Mgmt Fee (20%) - ${pm.team}`,
      debit: pm.foundationalFee.toFixed(2),
      pm_name: pm.name,
      team: pm.team,
      cost_code: pm.costCode,
    },
  ])
  return JSON.stringify({ period: '2026-02', entries: lines }, null, 2)
}

function buildXmlPreview(): string {
  const entries = PORTFOLIO_MANAGERS.flatMap((pm) => [
    `  <entry date="2026-02-28" gl="6100-CLOUD" cc="${pm.costCode}" debit="${pm.directCost.toFixed(2)}" pm="${pm.name}"/>`,
    `  <entry date="2026-02-28" gl="6200-SHARED" cc="${pm.costCode}" debit="${pm.sharedAlloc.toFixed(2)}" pm="${pm.name}"/>`,
    `  <entry date="2026-02-28" gl="6300-FNDTN" cc="${pm.costCode}" debit="${pm.foundationalFee.toFixed(2)}" pm="${pm.name}"/>`,
  ])
  return ['<?xml version="1.0" encoding="UTF-8"?>', '<ledger period="2026-02">', ...entries, '</ledger>'].join('\n')
}

export default function Ledger() {
  const [format, setFormat] = useState<Format>('csv')
  const [busy, setBusy] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const { hasPermission } = useAuth()

  const preview = useMemo(() => {
    if (format === 'csv') return buildCsvPreview()
    if (format === 'json') return buildJsonPreview()
    return buildXmlPreview()
  }, [format])

  const totals = useMemo(() => {
    const totalDebits = PORTFOLIO_MANAGERS.reduce(
      (s, pm) => s + pm.directCost + pm.sharedAlloc + pm.foundationalFee,
      0,
    )
    return {
      lineCount: PORTFOLIO_MANAGERS.length * 3,
      totalDebits,
    }
  }, [])

  const canExport = hasPermission('export_ledger')

  const handleDownload = async () => {
    setBusy('download')
    setMessage(null)
    try {
      if (canExport) {
        // Try the real backend: pull the most recent report for the period
        const res = await getChargebackReports('2026-02')
        const id = res.data[0]?.id
        if (id) {
          await downloadLedger(id, 'csv')
          setMessage(`Ledger for report #${id} downloaded.`)
          return
        }
      }
      // Fallback: download the client-side preview
      const blob = new Blob([preview], { type: mimeFor(format) })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `ledger_2026-02.${format}`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
      setMessage(`Preview ledger (${format.toUpperCase()}) downloaded.`)
    } catch (err) {
      setMessage((err as Error).message)
    } finally {
      setBusy(null)
    }
  }

  const handleSend = async () => {
    setBusy('send')
    setMessage(null)
    try {
      const res = await getChargebackReports('2026-02')
      const id = res.data[0]?.id
      if (!id) {
        setMessage('No approved report found for 2026-02.')
        return
      }
      await markLedgerSent(id)
      setMessage(`Report #${id} marked sent to Accounting.`)
    } catch (err) {
      setMessage((err as Error).message)
    } finally {
      setBusy(null)
    }
  }

  return (
    <div>
      <PageHeader
        title="Accounting Ledger Export"
        subtitle="Auto-generated ledger file ready for your accounting system"
      />

      {message && (
        <div className="mb-5 bg-info-soft text-info text-sm px-4 py-2.5 rounded-lg" role="status">
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-[2fr_1fr] gap-5">
        <Card
          title="Ledger File Preview"
          subtitle={`CSV format — ${CURRENT_PERIOD} billing cycle`}
          actions={
            <div className="flex items-center gap-0.5 bg-input rounded-lg p-0.5">
              {FORMATS.map((f) => (
                <button
                  key={f}
                  type="button"
                  onClick={() => setFormat(f)}
                  className={`px-4 py-[7px] rounded-md text-xs font-medium transition-all ${
                    format === f
                      ? 'bg-white text-ink-800 font-semibold shadow-card'
                      : 'text-muted hover:text-ink-800'
                  }`}
                >
                  {f.toUpperCase()}
                </button>
              ))}
            </div>
          }
        >
          <pre className="bg-[#1e1e2e] text-[#cdd6f4] font-mono text-xs leading-[1.7] rounded-card p-6 overflow-x-auto scrollbar-thin whitespace-pre">
            {formatPreviewHeader(preview, format)}
          </pre>
        </Card>

        <div className="space-y-5">
          <Card title="Export Summary">
            <div className="space-y-1">
              <SummaryRow label="Total Lines" value={totals.lineCount.toString()} />
              <SummaryRow label="Total Debits" value={formatCurrency(totals.totalDebits)} mono />
              <SummaryRow label="Format" value={`${format.toUpperCase()} / UTF-8`} />
              <SummaryRow label="Period" value={CURRENT_PERIOD} />
              <div className="flex items-center justify-between py-1.5 text-[13px]">
                <span className="text-muted">Status</span>
                <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-ok-soft text-ok text-[11px] font-semibold rounded-md">
                  <Check size={12} strokeWidth={2} />
                  Ready to Export
                </span>
              </div>
            </div>
          </Card>

          <div className="bg-surface rounded-card border border-line overflow-hidden">
            <div className="px-6 py-8 text-center">
              <div className="text-sm font-semibold text-ink-800 mb-1">Ready to Export</div>
              <div className="text-xs text-muted mb-5">
                Download the finalized ledger file for your accounting system
              </div>
              <button
                type="button"
                onClick={handleDownload}
                disabled={busy !== null}
                className="w-full inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-accent text-white text-[13px] font-semibold hover:bg-accent-hover hover:shadow-accent transition-all disabled:opacity-50"
              >
                <Download size={16} strokeWidth={1.8} />
                Download Ledger File
              </button>
              <button
                type="button"
                onClick={handleSend}
                disabled={busy !== null || !canExport}
                title={canExport ? undefined : 'Requires export_ledger permission'}
                className="w-full mt-3 inline-flex items-center justify-center gap-2 px-5 py-2 rounded-lg bg-transparent text-muted text-[13px] font-semibold hover:bg-input hover:text-ink-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send size={16} strokeWidth={1.8} />
                Send to Accounting
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function SummaryRow({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between py-1.5 text-[13px]">
      <span className="text-muted">{label}</span>
      <span className={`font-semibold text-ink-800 ${mono ? 'tabular-nums' : ''}`}>{value}</span>
    </div>
  )
}

function formatPreviewHeader(content: string, format: Format): string {
  // First line gets highlighted differently for CSV; leave JSON/XML as-is.
  if (format !== 'csv') return content
  const [header, ...rest] = content.split('\n')
  return [header, ...rest].join('\n')
}

function mimeFor(format: Format): string {
  if (format === 'csv') return 'text/csv'
  if (format === 'json') return 'application/json'
  return 'application/xml'
}
