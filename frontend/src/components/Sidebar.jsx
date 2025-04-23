// Sidebar.jsx
import { NavLink } from 'react-router-dom'

export function Sidebar({ darkMode }) {
  return (
    <div className={`w-64 h-full p-4 border-r ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
      <div className="mb-8">
        <h2 className="text-xl font-bold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
          DARA AI
        </h2>
        <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Research Analyst</p>
      </div>

      <nav className="space-y-2">
        <NavLink 
          to="/chat" 
          className={({ isActive }) => 
            `flex items-center p-3 rounded-lg transition-colors ${
              isActive 
                ? 'bg-blue-500 text-white' 
                : `${darkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-600'}`
            }`
          }
        >
          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          Chat History
        </NavLink>

        <NavLink
          to="/analysis"
          className={({ isActive }) =>
            `flex items-center p-3 rounded-lg transition-colors ${
              isActive
                ? 'bg-blue-500 text-white'
                : `${darkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-600'}`
            }`
          }
        >
          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Saved Reports
        </NavLink>

        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center p-3 rounded-lg transition-colors ${
              isActive
                ? 'bg-blue-500 text-white'
                : `${darkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-600'}`
            }`
          }
        >
          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Settings
        </NavLink>
      </nav>

      <div className={`mt-8 pt-8 border-t ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          <p>Storage used:</p>
          <div className="w-full bg-gray-200 rounded-full h-1 mt-2">
            <div className="bg-blue-500 h-1 rounded-full w-1/3"></div>
          </div>
        </div>
      </div>
    </div>
  )
}