import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAppContext } from './context/AppContext'
import HomePage from './pages/HomePage'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isLoggedIn } = useAppContext()
  return isLoggedIn ? children : <Navigate to="/login" replace />
}

// Public Route component (redirects to home if already logged in)
const PublicRoute = ({ children }) => {
  const { isLoggedIn } = useAppContext()
  return isLoggedIn ? <Navigate to="/" replace /> : children
}

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          } />
          <Route path="/register" element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          } />
          <Route path="/" element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App