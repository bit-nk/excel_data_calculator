import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import type { Permission, UserRole } from '../../types'

interface Props {
  roles?: UserRole[]
  permission?: Permission
}

export default function ProtectedRoute({ roles, permission }: Props = {}) {
  const { user, loading, hasRole, hasPermission } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-muted text-sm">
        Loading…
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (roles && roles.length > 0 && !hasRole(...roles)) {
    return <Navigate to="/forbidden" replace />
  }

  if (permission && !hasPermission(permission)) {
    return <Navigate to="/forbidden" replace />
  }

  return <Outlet />
}
