import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import ProtectedRoute from './components/common/ProtectedRoute'
import Overview from './pages/Overview'
import CostAnalysis from './pages/CostAnalysis'
import Reports from './pages/Reports'
import ChargebackPage from './pages/ChargebackPage'
import Login from './pages/Login'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Layout />}>
          <Route index element={<Overview />} />
          <Route path="cost-analysis" element={<CostAnalysis />} />
          <Route path="reports" element={<Reports />} />
          <Route path="chargeback" element={<ChargebackPage />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
