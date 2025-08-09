import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import { Layout } from './components/layout/Layout'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { BillingPage } from './pages/BillingPage'
import { UsagePage } from './pages/UsagePage'
import { PackagesPage } from './pages/PackagesPage'
import { SpeedTestPage } from './pages/SpeedTestPage'
import { ProfilePage } from './pages/ProfilePage'
import { LoadingSpinner } from './components/ui/LoadingSpinner'

function App() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/billing" element={<BillingPage />} />
        <Route path="/usage" element={<UsagePage />} />
        <Route path="/packages" element={<PackagesPage />} />
        <Route path="/speed-test" element={<SpeedTestPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/login" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  )
}

export default App