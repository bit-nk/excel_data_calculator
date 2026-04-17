import { Doughnut } from 'react-chartjs-2'
import '../../lib/chart-setup'
import { PLATFORMS, formatCurrency } from '../../data/mock'

export default function PlatformDonut() {
  return (
    <Doughnut
      data={{
        labels: PLATFORMS.map((p) => p.name),
        datasets: [
          {
            data: PLATFORMS.map((p) => p.spend),
            backgroundColor: PLATFORMS.map((p) => p.color),
            borderWidth: 0,
            spacing: 3,
            borderRadius: 4,
          },
        ],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0B0B15',
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: (ctx) => {
                const total = (ctx.dataset.data as number[]).reduce((a, b) => a + b, 0)
                const pct = total > 0 ? ((Number(ctx.parsed) / total) * 100).toFixed(1) : '0'
                return ` ${formatCurrency(Number(ctx.parsed))} (${pct}%)`
              },
            },
          },
        },
      }}
    />
  )
}
