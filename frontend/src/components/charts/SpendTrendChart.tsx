import { Line } from 'react-chartjs-2'
import '../../lib/chart-setup'
import { MONTHLY_TOTALS, formatCurrency } from '../../data/mock'

export default function SpendTrendChart() {
  return (
    <Line
      data={{
        labels: MONTHLY_TOTALS.map((m) => m.month),
        datasets: [
          {
            label: 'Total Cloud Spend',
            data: MONTHLY_TOTALS.map((m) => m.total),
            borderColor: '#7C3AED',
            backgroundColor: 'rgba(124,58,237,0.08)',
            borderWidth: 2.5,
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: '#7C3AED',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointHoverRadius: 6,
          },
        ],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0B0B15',
            padding: 12,
            cornerRadius: 8,
            titleFont: { size: 12 },
            bodyFont: { size: 13, weight: 600 },
            callbacks: { label: (ctx) => formatCurrency(ctx.parsed.y) },
          },
        },
        interaction: { intersect: false, mode: 'index' },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: '#9CA3AF', font: { size: 11, weight: 500 } },
          },
          y: {
            grid: { color: '#F3F4F6' },
            border: { display: false },
            ticks: {
              color: '#9CA3AF',
              font: { size: 11 },
              callback: (v) => formatCurrency(Number(v), true),
            },
          },
        },
      }}
    />
  )
}
