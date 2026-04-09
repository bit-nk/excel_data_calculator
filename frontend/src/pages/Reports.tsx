import { AlertTriangle, Cpu, Tag, Cloud, Receipt, Leaf, Download } from 'lucide-react'

const reports = [
  {
    title: 'Anomaly Detection Report',
    description: 'Unusual spending patterns and cost spikes with root cause analysis.',
    icon: AlertTriangle,
    iconBg: 'bg-yellow-100',
    iconColor: 'text-yellow-600',
  },
  {
    title: 'Reserved Instance Analysis',
    description: 'RI coverage, utilization, and recommendations for commitment optimization.',
    icon: Cpu,
    iconBg: 'bg-red-100',
    iconColor: 'text-driven-red',
  },
  {
    title: 'Tag Compliance Report',
    description: 'Resource tagging compliance status and untagged resource identification.',
    icon: Tag,
    iconBg: 'bg-pink-100',
    iconColor: 'text-pink-600',
  },
  {
    title: 'Multi-Cloud Comparison',
    description: 'Side-by-side comparison of AWS vs Azure costs, performance, and efficiency.',
    icon: Cloud,
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
  },
  {
    title: 'Chargeback Report',
    description: 'Department and team-wise cost allocation for internal billing and accountability.',
    icon: Receipt,
    iconBg: 'bg-amber-100',
    iconColor: 'text-amber-600',
  },
  {
    title: 'Sustainability Report',
    description: 'Carbon footprint analysis and environmental impact of cloud infrastructure.',
    icon: Leaf,
    iconBg: 'bg-emerald-100',
    iconColor: 'text-emerald-600',
  },
]

export default function Reports() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-driven-navy">FinOps Reports</h2>
        <p className="text-sm text-gray-500 mt-1">Download comprehensive PDF reports</p>
      </div>

      <div className="grid grid-cols-3 gap-5">
        {reports.map(({ title, description, icon: Icon, iconBg, iconColor }) => (
          <div
            key={title}
            className="bg-white rounded-xl p-6 shadow-sm border border-driven-gray-200 flex flex-col"
          >
            <div className={`w-12 h-12 rounded-xl ${iconBg} flex items-center justify-center mb-4`}>
              <Icon size={24} className={iconColor} />
            </div>
            <h3 className="text-lg font-semibold text-driven-navy mb-2">{title}</h3>
            <p className="text-sm text-gray-500 flex-1 mb-4">{description}</p>
            <button className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg bg-gradient-to-r from-driven-red to-driven-orange text-white text-sm font-medium hover:opacity-90 transition-opacity">
              <Download size={16} />
              Download PDF
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
