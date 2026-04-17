import { Bar } from 'react-chartjs-2'
import '../../lib/chart-setup'
import { PORTFOLIO_MANAGERS, formatCurrency } from '../../data/mock'

export default function ChargebackBars() {
  const labels = PORTFOLIO_MANAGERS.map((pm) => pm.name.split(' ').pop() ?? pm.name)

  return (
    <Bar
      data={{
        labels,
        datasets: [
          {
            label: 'Direct Costs',
            data: PORTFOLIO_MANAGERS.map((pm) => pm.directCost),
            backgroundColor: '#3B82F6',
            borderRadius: 4,
            barPercentage: 0.7,
          },
          {
            label: 'Shared Allocation',
            data: PORTFOLIO_MANAGERS.map((pm) => pm.sharedAlloc),
            backgroundColor: '#F59E0B',
            borderRadius: 4,
            barPercentage: 0.7,
          },
          {
            label: 'Foundational Fee (20%)',
            data: PORTFOLIO_MANAGERS.map((pm) => pm.foundationalFee),
            backgroundColor: '#7C3AED',
            borderRadius: 4,
            barPercentage: 0.7,
          },
        ],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 20,
              usePointStyle: true,
              pointStyle: 'rectRounded',
              font: { size: 11, weight: 500 },
            },
          },
          tooltip: {
            backgroundColor: '#0B0B15',
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y)}`,
            },
          },
        },
        scales: {
          x: {
            stacked: true,
            grid: { display: false },
            ticks: { color: '#9CA3AF', font: { size: 11, weight: 500 } },
          },
          y: {
            stacked: true,
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
