import { useState } from 'react'
import { Download, RefreshCw, CheckCircle } from 'lucide-react'

interface BUSummary {
  bu: string
  code: string
  aws: number
  mongodb: number
  datadog: number
  confluent: number
  singlestore: number
  harness: number
  directTotal: number
  shared: number
  fee: number
  grandTotal: number
}

const mockData: BUSummary[] = [
  { bu: 'Global Equities', code: 'GEQ', aws: 312000, mongodb: 105000, datadog: 95000, confluent: 52500, singlestore: 21250, harness: 15000, directTotal: 600750, shared: 72090, fee: 120150, grandTotal: 792990 },
  { bu: 'Quantitative Strategies', code: 'QST', aws: 280000, mongodb: 94500, datadog: 85500, confluent: 47250, singlestore: 19125, harness: 13500, directTotal: 539875, shared: 64785, fee: 107975, grandTotal: 712635 },
  { bu: 'Multi-Strategy', code: 'MST', aws: 218000, mongodb: 73500, datadog: 66500, confluent: 36750, singlestore: 14875, harness: 10500, directTotal: 420125, shared: 50415, fee: 84025, grandTotal: 554565 },
  { bu: 'Technology', code: 'TCH', aws: 186000, mongodb: 63000, datadog: 57000, confluent: 31500, singlestore: 12750, harness: 9000, directTotal: 359250, shared: 43110, fee: 71850, grandTotal: 474210 },
  { bu: 'Platform Engineering', code: 'PLE', aws: 155000, mongodb: 52500, datadog: 47500, confluent: 26250, singlestore: 10625, harness: 7500, directTotal: 299375, shared: 35925, fee: 59875, grandTotal: 395175 },
  { bu: 'Risk Management', code: 'RSK', aws: 94000, mongodb: 31500, datadog: 28500, confluent: 15750, singlestore: 6375, harness: 4500, directTotal: 180625, shared: 21675, fee: 36125, grandTotal: 238425 },
]

const fmt = (n: number) => `$${(n / 1000).toFixed(0)}K`

export default function ChargebackPage() {
  const [period, setPeriod] = useState('2026-03')

  const totals = mockData.reduce(
    (acc, row) => ({
      aws: acc.aws + row.aws,
      mongodb: acc.mongodb + row.mongodb,
      datadog: acc.datadog + row.datadog,
      confluent: acc.confluent + row.confluent,
      singlestore: acc.singlestore + row.singlestore,
      harness: acc.harness + row.harness,
      directTotal: acc.directTotal + row.directTotal,
      shared: acc.shared + row.shared,
      fee: acc.fee + row.fee,
      grandTotal: acc.grandTotal + row.grandTotal,
    }),
    { aws: 0, mongodb: 0, datadog: 0, confluent: 0, singlestore: 0, harness: 0, directTotal: 0, shared: 0, fee: 0, grandTotal: 0 }
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-driven-navy">Chargeback Report</h2>
          <p className="text-sm text-gray-500 mt-1">Department and team-wise cost allocation</p>
        </div>
        <div className="flex items-center gap-3">
          <input
            type="month"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="px-4 py-2 border border-driven-gray-300 rounded-lg text-sm"
          />
          <button className="flex items-center gap-2 px-4 py-2 bg-driven-navy text-white text-sm rounded-lg hover:opacity-90">
            <RefreshCw size={14} />
            Generate
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:opacity-90">
            <CheckCircle size={14} />
            Approve
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-driven-red text-white text-sm rounded-lg hover:opacity-90">
            <Download size={14} />
            Export
          </button>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-driven-gray-200">
          <div className="text-sm text-gray-500">Total Direct Costs</div>
          <div className="text-xl font-bold text-driven-navy mt-1">{fmt(totals.directTotal)}</div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-driven-gray-200">
          <div className="text-sm text-gray-500">Shared Cost Allocation</div>
          <div className="text-xl font-bold text-driven-navy mt-1">{fmt(totals.shared)}</div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-driven-gray-200">
          <div className="text-sm text-gray-500">Management Fee (20%)</div>
          <div className="text-xl font-bold text-driven-navy mt-1">{fmt(totals.fee)}</div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-driven-gray-200">
          <div className="text-sm text-gray-500">Grand Total</div>
          <div className="text-xl font-bold text-driven-red mt-1">{fmt(totals.grandTotal)}</div>
        </div>
      </div>

      {/* Chargeback table */}
      <div className="bg-white rounded-xl shadow-sm border border-driven-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-driven-navy text-white">
                <th className="text-left py-3 px-4 font-medium">Business Unit</th>
                <th className="text-right py-3 px-4 font-medium">AWS</th>
                <th className="text-right py-3 px-4 font-medium">MongoDB</th>
                <th className="text-right py-3 px-4 font-medium">Datadog</th>
                <th className="text-right py-3 px-4 font-medium">Confluent</th>
                <th className="text-right py-3 px-4 font-medium">SingleStore</th>
                <th className="text-right py-3 px-4 font-medium">Harness</th>
                <th className="text-right py-3 px-4 font-medium bg-blue-900">Direct Total</th>
                <th className="text-right py-3 px-4 font-medium bg-blue-900">Shared</th>
                <th className="text-right py-3 px-4 font-medium bg-blue-900">Mgmt Fee</th>
                <th className="text-right py-3 px-4 font-medium bg-red-900">Grand Total</th>
              </tr>
            </thead>
            <tbody>
              {mockData.map((row, i) => (
                <tr key={row.code} className={i % 2 === 0 ? 'bg-white' : 'bg-driven-gray-50'}>
                  <td className="py-3 px-4 font-medium">
                    <div>{row.bu}</div>
                    <div className="text-xs text-gray-400">{row.code}</div>
                  </td>
                  <td className="text-right py-3 px-4">{fmt(row.aws)}</td>
                  <td className="text-right py-3 px-4">{fmt(row.mongodb)}</td>
                  <td className="text-right py-3 px-4">{fmt(row.datadog)}</td>
                  <td className="text-right py-3 px-4">{fmt(row.confluent)}</td>
                  <td className="text-right py-3 px-4">{fmt(row.singlestore)}</td>
                  <td className="text-right py-3 px-4">{fmt(row.harness)}</td>
                  <td className="text-right py-3 px-4 font-semibold bg-blue-50">{fmt(row.directTotal)}</td>
                  <td className="text-right py-3 px-4 bg-blue-50">{fmt(row.shared)}</td>
                  <td className="text-right py-3 px-4 bg-blue-50">{fmt(row.fee)}</td>
                  <td className="text-right py-3 px-4 font-bold text-driven-red bg-red-50">{fmt(row.grandTotal)}</td>
                </tr>
              ))}
              {/* Totals row */}
              <tr className="bg-driven-navy text-white font-semibold">
                <td className="py-3 px-4">TOTAL</td>
                <td className="text-right py-3 px-4">{fmt(totals.aws)}</td>
                <td className="text-right py-3 px-4">{fmt(totals.mongodb)}</td>
                <td className="text-right py-3 px-4">{fmt(totals.datadog)}</td>
                <td className="text-right py-3 px-4">{fmt(totals.confluent)}</td>
                <td className="text-right py-3 px-4">{fmt(totals.singlestore)}</td>
                <td className="text-right py-3 px-4">{fmt(totals.harness)}</td>
                <td className="text-right py-3 px-4">{fmt(totals.directTotal)}</td>
                <td className="text-right py-3 px-4">{fmt(totals.shared)}</td>
                <td className="text-right py-3 px-4">{fmt(totals.fee)}</td>
                <td className="text-right py-3 px-4 text-red-300">{fmt(totals.grandTotal)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
