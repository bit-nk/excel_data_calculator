import { Link } from 'react-router-dom'
import { ShieldAlert } from 'lucide-react'

export default function Forbidden() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-6">
      <div className="w-14 h-14 rounded-full bg-accent-soft flex items-center justify-center mb-4">
        <ShieldAlert size={26} className="text-accent" />
      </div>
      <h1 className="text-xl font-semibold text-ink-800">Access denied</h1>
      <p className="text-sm text-muted mt-2 max-w-md">
        Your role does not have permission to view this page. If you believe this is a mistake,
        contact your FinOps administrator.
      </p>
      <Link
        to="/"
        className="mt-6 px-4 py-2 rounded-lg bg-accent text-white text-sm font-medium hover:bg-accent-hover transition-colors"
      >
        Back to dashboard
      </Link>
    </div>
  )
}
