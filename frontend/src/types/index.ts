export type Platform = 'aws' | 'mongodb' | 'datadog' | 'confluent' | 'singlestore' | 'harness'
export type CloudFilter = 'all' | 'aws' | 'azure'
export type UserRole = 'admin' | 'finance' | 'portfolio_manager' | 'viewer'

export interface User {
  id: number
  email: string
  full_name: string
  role_name: UserRole
  business_unit_id: number | null
  is_active: boolean
}

export interface ChargebackReport {
  id: number
  billing_period: string
  status: string
  total_direct_cost: number
  total_shared_cost: number
  total_management_fee: number
  total_cost: number
  generated_at: string
  approved_at: string | null
  line_items: ChargebackLineItem[]
}

export interface ChargebackLineItem {
  id: number
  business_unit_name: string
  business_unit_code: string
  portfolio_manager_name: string | null
  platform: Platform
  category: string
  cost_code: string | null
  service_name: string | null
  direct_cost: number
  shared_cost_allocation: number
  management_fee: number
  total_cost: number
}

export interface ChargebackSummaryByBU {
  business_unit_name: string
  business_unit_code: string
  aws_cost: number
  mongodb_cost: number
  datadog_cost: number
  confluent_cost: number
  singlestore_cost: number
  harness_cost: number
  total_direct: number
  shared_allocation: number
  management_fee: number
  grand_total: number
}

export interface CostBreakdown {
  platform: Platform
  total_cost: number
  percentage: number
}

export interface CostTrend {
  period: string
  total_cost: number
  by_platform: Record<string, number>
}

export interface ConnectorHealth {
  [platform: string]: {
    is_healthy: boolean
    message: string
  }
}
