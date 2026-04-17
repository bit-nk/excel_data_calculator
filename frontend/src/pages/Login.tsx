import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import NkFinOpsLogo from '../components/brand/NkFinOpsLogo'
import { useAuth } from '../hooks/useAuth'

const DEMO_EMAIL = 'admin@nkfinops.local'
const DEMO_PASSWORD = 'demo-access-2026'

export default function Login() {
  const [email, setEmail] = useState(DEMO_EMAIL)
  const [password, setPassword] = useState(DEMO_PASSWORD)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email.trim(), password)
      navigate('/')
    } catch {
      setError('Unable to sign in. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-body px-4">
      <div className="w-full max-w-md">
        <div className="bg-surface rounded-card border border-line shadow-lift p-8">
          <div className="flex flex-col items-center mb-8">
            <div className="w-14 h-14 bg-ink-900 rounded-xl flex items-center justify-center mb-4">
              <NkFinOpsLogo size={18} />
            </div>
            <h1 className="text-xl font-bold text-ink-800 tracking-[-0.3px]">FinOps Engine</h1>
            <p className="text-xs text-muted mt-1 tracking-[1.5px] uppercase font-semibold">
              Cloud Cost Allocation
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            {error && (
              <div
                className="bg-danger-soft text-danger text-sm px-3 py-2.5 rounded-lg"
                role="alert"
              >
                {error}
              </div>
            )}
            <div>
              <label htmlFor="email" className="block text-[13px] font-semibold text-ink-800 mb-1.5">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2.5 bg-input border border-transparent rounded-lg text-sm text-ink-800 focus:outline-none focus:ring-2 focus:ring-accent focus:bg-white transition"
                autoComplete="email"
                maxLength={255}
                required
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-[13px] font-semibold text-ink-800 mb-1.5">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 bg-input border border-transparent rounded-lg text-sm text-ink-800 focus:outline-none focus:ring-2 focus:ring-accent focus:bg-white transition"
                autoComplete="current-password"
                maxLength={128}
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 bg-accent hover:bg-accent-hover text-white rounded-lg text-sm font-semibold shadow-accent hover:shadow-lift transition-all disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in…' : 'Sign In'}
            </button>

            <p className="text-[11px] text-muted-soft text-center mt-3">
              Demo mode — credentials pre-filled. Backend optional.
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
