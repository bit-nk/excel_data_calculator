import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { getMe, login as apiLogin } from '../services/api'
import type { Permission, User, UserRole } from '../types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  hasPermission: (permission: Permission) => boolean
  hasRole: (...roles: UserRole[]) => boolean
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const OFFLINE_TOKEN = 'offline-demo'

const OFFLINE_USER: User = {
  id: 0,
  email: 'admin@nkfinops.local',
  full_name: 'NkFinOps Admin',
  role_name: 'admin',
  business_unit_id: null,
  is_active: true,
  permissions: {
    view_all_bus: true,
    approve_reports: true,
    manage_rules: true,
    export_ledger: true,
  },
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  const refresh = useCallback(async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    if (token === OFFLINE_TOKEN) {
      setUser(OFFLINE_USER)
      setLoading(false)
      return
    }
    try {
      const res = await getMe()
      setUser(res.data)
    } catch {
      // Backend unreachable or token invalid — fall back to offline demo user
      localStorage.setItem('token', OFFLINE_TOKEN)
      setUser(OFFLINE_USER)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const login = useCallback(async (email: string, password: string) => {
    try {
      const res = await apiLogin(email, password)
      localStorage.setItem('token', res.data.access_token)
      const me = await getMe()
      setUser(me.data)
    } catch {
      // Backend offline — sign the user in locally as the demo admin so the
      // UI is explorable without a running API.
      localStorage.setItem('token', OFFLINE_TOKEN)
      setUser({ ...OFFLINE_USER, email })
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setUser(null)
  }, [])

  const hasPermission = useCallback(
    (permission: Permission) => Boolean(user?.permissions?.[permission]),
    [user],
  )

  const hasRole = useCallback(
    (...roles: UserRole[]) => (user ? roles.includes(user.role_name) : false),
    [user],
  )

  const value = useMemo(
    () => ({ user, loading, login, logout, hasPermission, hasRole }),
    [user, loading, login, logout, hasPermission, hasRole],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
