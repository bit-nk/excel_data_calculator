import type { ReactNode } from 'react'
import { useAuth } from '../../hooks/useAuth'
import type { Permission, UserRole } from '../../types'

interface Props {
  roles?: UserRole[]
  permission?: Permission
  fallback?: ReactNode
  children: ReactNode
}

export default function Can({ roles, permission, fallback = null, children }: Props) {
  const { hasRole, hasPermission } = useAuth()

  if (roles && roles.length > 0 && !hasRole(...roles)) return <>{fallback}</>
  if (permission && !hasPermission(permission)) return <>{fallback}</>
  return <>{children}</>
}
