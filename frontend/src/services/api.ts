import axios, { AxiosError } from 'axios'
import type {
  User,
  ChargebackReport,
  ChargebackSummaryByBU,
  CostBreakdown,
  CostTrend,
  ConnectorHealth,
} from '../types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      // Use path-based redirect instead of window.location to stay in SPA
      if (window.location.pathname !== '/login') {
        window.location.pathname = '/login'
      }
    }
    // Sanitize error — only pass status and message, not full response
    const status = err.response?.status ?? 0
    const message = (err.response?.data as { detail?: string })?.detail ?? 'An error occurred'
    return Promise.reject(new Error(`[${status}] ${message}`))
  }
)

// --- Billing period validation ---
const BILLING_PERIOD_RE = /^\d{4}-(0[1-9]|1[0-2])$/

function validateBillingPeriod(period: string): string {
  if (!BILLING_PERIOD_RE.test(period)) {
    throw new Error('Invalid billing period format. Expected YYYY-MM.')
  }
  return period
}

// Auth
export const login = (email: string, password: string) =>
  api.post<{ access_token: string }>('/auth/login', {
    email: email.trim(),
    password,
  })

export const getMe = () => api.get<User>('/auth/me')

// Costs
export const getCostBreakdown = (billingPeriod: string) =>
  api.get<CostBreakdown[]>('/costs/breakdown-by-platform', {
    params: { billing_period: validateBillingPeriod(billingPeriod) },
  })

export const getCostTrend = (months = 6) =>
  api.get<CostTrend[]>('/costs/trend', { params: { months } })

// Chargeback
export const generateChargebackReport = (billingPeriod: string) =>
  api.post<ChargebackReport>('/chargeback/generate', {
    billing_period: validateBillingPeriod(billingPeriod),
  })

export const getChargebackReports = (billingPeriod?: string) =>
  api.get<ChargebackReport[]>('/chargeback/reports', {
    params: billingPeriod ? { billing_period: validateBillingPeriod(billingPeriod) } : {},
  })

export const getChargebackReport = (id: number) =>
  api.get<ChargebackReport>(`/chargeback/reports/${id}`)

export const approveReport = (id: number) =>
  api.post(`/chargeback/reports/${id}/approve`)

export const getChargebackSummary = (billingPeriod: string) =>
  api.get<ChargebackSummaryByBU[]>('/chargeback/summary', {
    params: { billing_period: validateBillingPeriod(billingPeriod) },
  })

// Connectors
export const getConnectorHealth = () =>
  api.get<ConnectorHealth>('/connectors/health')

export const triggerIngestion = (startDate: string, endDate: string, platforms?: string[]) =>
  api.post('/connectors/ingest', null, {
    params: { start_date: startDate, end_date: endDate, platforms },
  })

export default api
