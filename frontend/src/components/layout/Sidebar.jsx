import React from 'react'
import { useAppContext } from '../../context/AppContext'

const Sidebar = () => {
  const { chats, currentChat, createNewChat, dispatch, user, logout } = useAppContext()

  const selectChat = (chat) => {
    dispatch({ type: 'SET_CURRENT_CHAT', payload: chat })
    // Load messages for this chat
    dispatch({ type: 'SET_MESSAGES', payload: [] }) // Replace with actual message loading
  }

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col h-full">
      {/* New Chat Button */}
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={createNewChat}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition duration-200 flex items-center justify-center"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Chat
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-4">
        <h3 className="text-sm font-medium text-gray-400 mb-3">Previous Chats</h3>
        <div className="space-y-2">
          {chats.map((chat) => (
            <button
              key={chat.id}
              onClick={() => selectChat(chat)}
              className={`w-full text-left p-3 rounded-lg transition duration-200 ${
                currentChat?.id === chat.id 
                  ? 'bg-gray-700 text-white' 
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <div className="text-sm font-medium truncate">{chat.title}</div>
              <div className="text-xs text-gray-500 mt-1">
                {new Date(chat.createdAt).toLocaleDateString()}
              </div>
            </button>
          ))}
          {chats.length === 0 && (
            <div className="text-gray-500 text-sm text-center py-8">
              No previous chats
            </div>
          )}
        </div>
      </div>

      {/* User Profile Section */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <span className="text-sm font-medium">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-white truncate">
              {user?.name || 'User'}
            </div>
            <div className="text-xs text-gray-400 truncate">
              {user?.email || 'user@example.com'}
            </div>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full text-left text-sm text-gray-400 hover:text-white transition duration-200"
        >
          Sign Out
        </button>
      </div>
    </div>
  )
}

export default Sidebar