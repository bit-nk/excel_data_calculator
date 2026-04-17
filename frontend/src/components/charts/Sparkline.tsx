import { Line } from 'react-chartjs-2'
import '../../lib/chart-setup'

interface Props {
  data: number[]
  color: string
  labels?: string[]
}

export default function Sparkline({ data, color, labels }: Props) {
  return (
    <Line
      data={{
        labels: labels ?? data.map((_, i) => String(i)),
        datasets: [
          {
            data,
            borderColor: color,
            backgroundColor: color + '22',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
          },
        ],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        scales: { x: { display: false }, y: { display: false } },
      }}
    />
  )
}
