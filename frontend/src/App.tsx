import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import ProtectedRoute from './components/common/ProtectedRoute'
import { AuthProvider } from './hooks/useAuth'
import Overview from './pages/Overview'
import Platforms from './pages/Platforms'
import ChargebackPage from './pages/ChargebackPage'
import Invoice from './pages/Invoice'
import Ledger from './pages/Ledger'
import Login from './pages/Login'
import Forbidden from './pages/Forbidden'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Layout />}>
            <Route index element={<Overview />} />
            <Route path="platforms" element={<Platforms />} />
            <Route path="invoice" element={<Invoice />} />
            <Route path="forbidden" element={<Forbidden />} />

            <Route element={<ProtectedRoute roles={['admin', 'finance', 'portfolio_manager']} />}>
              <Route path="chargeback" element={<ChargebackPage />} />
            </Route>

            <Route element={<ProtectedRoute permission="export_ledger" />}>
              <Route path="ledger" element={<Ledger />} />
            </Route>
          </Route>
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App
