import { Navigate, Route, Routes } from 'react-router-dom'
import { DashboardPage } from './pages/DashboardPage.jsx'
import { SetupPage } from './pages/SetupPage.jsx'
import { hasSession } from './lib/session.js'

function RootRedirect() {
  return <Navigate to={hasSession() ? '/dashboard' : '/setup'} replace />
}

function RequireSession({ children }) {
  if (!hasSession()) {
    return <Navigate to="/setup" replace />
  }
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<RootRedirect />} />
      <Route path="/setup" element={<SetupPage />} />
      <Route
        path="/dashboard"
        element={
          <RequireSession>
            <DashboardPage />
          </RequireSession>
        }
      />
      <Route path="*" element={<RootRedirect />} />
    </Routes>
  )
}
