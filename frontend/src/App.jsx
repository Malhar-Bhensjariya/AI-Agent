import { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { LandingPage } from './pages/LandingPage'
import { ChatPage } from './pages/ChatPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'

export default function App() {
  const [darkMode, setDarkMode] = useState(false)

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-50'}`}>
      <BrowserRouter>
        <nav className="p-4 border-b flex justify-between items-center bg-white dark:bg-gray-800">
          <h1 className="text-xl font-bold"></h1>
          <button 
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            {darkMode ? '🌙' : '🌞'}
          </button>
        </nav>

        <Routes>
          <Route path="/" element={<LandingPage darkMode={darkMode} />} />
          <Route path="/chat" element={<ChatPage darkMode={darkMode} />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  )
}