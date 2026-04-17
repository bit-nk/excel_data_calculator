export interface Platform {
  id: 'aws' | 'datadog' | 'confluent' | 'mongodb' | 'singlestore'
  name: string
  type: string
  color: string
  spend: number
  prevSpend: number
  monthlyTrend: number[]
  topItems: { name: string; cost: number }[]
}

export interface PortfolioManager {
  id: string
  name: string
  team: string
  costCode: string
  color: string
  directCost: number
  sharedAlloc: number
  foundationalFee: number
}

export interface MonthlyTotal {
  month: string
  total: number
}

export interface ConnectionStatus {
  name: string
  status: 'Connected' | 'Degraded' | 'Down'
  lastSync: string
}

export const CURRENT_PERIOD = 'February 2026'
export const LAST_UPDATED = 'Mar 1, 2026 08:00 AM EST'
export const FOUNDATIONAL_FEE_RATE = 0.20

export const MONTHLY_TOTALS: MonthlyTotal[] = [
  { month: 'Sep 2025', total: 589420 },
  { month: 'Oct 2025', total: 601830 },
  { month: 'Nov 2025', total: 612450 },
  { month: 'Dec 2025', total: 598100 },
  { month: 'Jan 2026', total: 623740 },
  { month: 'Feb 2026', total: 631284 },
]

export const PLATFORMS: Platform[] = [
  {
    id: 'aws',
    name: 'Amazon Web Services',
    type: 'Cloud Infrastructure',
    color: '#FF9900',
    spend: 421680,
    prevSpend: 412300,
    monthlyTrend: [385000, 392000, 401000, 395000, 412300, 421680],
    topItems: [
      { name: 'EC2 Instances', cost: 189200 },
      { name: 'S3 Storage', cost: 67400 },
      { name: 'RDS Databases', cost: 82350 },
      { name: 'Lambda Functions', cost: 31200 },
      { name: 'Data Transfer', cost: 28400 },
      { name: 'Other Services', cost: 23130 },
    ],
  },
  {
    id: 'datadog',
    name: 'Datadog',
    type: 'Monitoring & Observability',
    color: '#632CA6',
    spend: 86420,
    prevSpend: 89100,
    monthlyTrend: [78000, 81000, 84500, 87200, 89100, 86420],
    topItems: [
      { name: 'Infrastructure Hosts', cost: 42800 },
      { name: 'APM & Tracing', cost: 21600 },
      { name: 'Log Management', cost: 14200 },
      { name: 'Synthetics', cost: 4820 },
      { name: 'Custom Metrics', cost: 3000 },
    ],
  },
  {
    id: 'confluent',
    name: 'Confluent',
    type: 'Event Streaming',
    color: '#1A73E8',
    spend: 62340,
    prevSpend: 58900,
    monthlyTrend: [52000, 54000, 56800, 55200, 58900, 62340],
    topItems: [
      { name: 'Dedicated Clusters', cost: 38400 },
      { name: 'Partition Hours', cost: 12800 },
      { name: 'Connectors', cost: 6200 },
      { name: 'Schema Registry', cost: 2800 },
      { name: 'ksqlDB', cost: 2140 },
    ],
  },
  {
    id: 'mongodb',
    name: 'MongoDB Atlas',
    type: 'Database Platform',
    color: '#00684A',
    spend: 38120,
    prevSpend: 40200,
    monthlyTrend: [32000, 34000, 35600, 37800, 40200, 38120],
    topItems: [
      { name: 'M50 Clusters', cost: 22400 },
      { name: 'M30 Clusters', cost: 8900 },
      { name: 'Data Transfer', cost: 3400 },
      { name: 'Backup Storage', cost: 2200 },
      { name: 'Atlas Search', cost: 1220 },
    ],
  },
  {
    id: 'singlestore',
    name: 'SingleStore',
    type: 'Distributed SQL',
    color: '#AA00FF',
    spend: 22724,
    prevSpend: 23240,
    monthlyTrend: [18000, 19500, 20200, 21400, 23240, 22724],
    topItems: [
      { name: 'Workspace Compute', cost: 14200 },
      { name: 'Storage', cost: 5800 },
      { name: 'Data Transfer', cost: 2724 },
    ],
  },
]

export const PORTFOLIO_MANAGERS: PortfolioManager[] = [
  { id: 'pm1', name: 'Michael Chen', team: 'Quant Alpha', costCode: 'QA-001', color: '#3B82F6', directCost: 89400, sharedAlloc: 18200, foundationalFee: 17880 },
  { id: 'pm2', name: 'Sarah Mitchell', team: 'Global Macro', costCode: 'GM-002', color: '#8B5CF6', directCost: 112600, sharedAlloc: 22900, foundationalFee: 22520 },
  { id: 'pm3', name: 'James Rodriguez', team: 'Systematic Trading', costCode: 'ST-003', color: '#10B981', directCost: 76800, sharedAlloc: 15600, foundationalFee: 15360 },
  { id: 'pm4', name: 'Emily Nakamura', team: 'Equity L/S', costCode: 'EQ-004', color: '#F59E0B', directCost: 95200, sharedAlloc: 19400, foundationalFee: 19040 },
  { id: 'pm5', name: 'David Park', team: 'Fixed Income', costCode: 'FI-005', color: '#EF4444', directCost: 54300, sharedAlloc: 11100, foundationalFee: 10860 },
  { id: 'pm6', name: 'Alexandra Volkov', team: 'Multi-Strategy', costCode: 'MS-006', color: '#06B6D4', directCost: 68900, sharedAlloc: 14000, foundationalFee: 13780 },
  { id: 'pm7', name: 'Robert Kim', team: 'Event Arbitrage', costCode: 'ED-007', color: '#EC4899', directCost: 42200, sharedAlloc: 8600, foundationalFee: 8440 },
  { id: 'pm8', name: 'Lisa Patel', team: 'Quant Research', costCode: 'QR-008', color: '#14B8A6', directCost: 68284, sharedAlloc: 13800, foundationalFee: 13657 },
]

export const CONNECTIONS: ConnectionStatus[] = [
  { name: 'AWS', status: 'Connected', lastSync: '2 min ago' },
  { name: 'Datadog', status: 'Connected', lastSync: '5 min ago' },
  { name: 'Confluent', status: 'Connected', lastSync: '12 min ago' },
  { name: 'MongoDB', status: 'Connected', lastSync: '8 min ago' },
  { name: 'SingleStore', status: 'Connected', lastSync: '15 min ago' },
  { name: 'Harness', status: 'Connected', lastSync: '3 min ago' },
]

export const SHARED_COSTS = {
  platformEngineering: 95200,
  unallocated: 28400,
  total: 123600,
}

export function formatCurrency(amount: number, compact = false): string {
  if (compact && Math.abs(amount) >= 1_000_000) {
    return '$' + (amount / 1_000_000).toFixed(1) + 'M'
  }
  if (compact && Math.abs(amount) >= 1_000) {
    return '$' + (amount / 1_000).toFixed(0) + 'K'
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatPercent(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return sign + value.toFixed(1) + '%'
}

export function calcChange(current: number, previous: number): number {
  return ((current - previous) / previous) * 100
}

export function initials(fullName: string): string {
  return fullName
    .split(' ')
    .map((n) => n[0])
    .join('')
}
