import React from 'react'
import { useAppContext } from './context/AppContext'
import HomePage from './pages/HomePage'
import LandingPage from './pages/LandingPage'

function App() {
  const { isLoggedIn } = useAppContext()

  return (
    <div className="App">
      {true ? <HomePage /> : <LandingPage />}
    </div>
  )
}

export default App