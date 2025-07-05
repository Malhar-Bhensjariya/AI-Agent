import React from 'react'
import { useAppContext } from '../../context/AppContext'
import { Plus, MessageCircle, LogOut, BarChart3 } from 'lucide-react'

const Sidebar = () => {
  const { chats, currentChat, createNewChat, setCurrentChat, setMessages, user, logout } = useAppContext()

  const selectChat = (chat) => {
    setCurrentChat(chat)
    // Load messages for this chat
    setMessages([]) // Replace with actual message loading
  }

  return (
    <div className="group w-16 hover:w-64 bg-slate-900 text-white flex flex-col h-full transition-all duration-300 ease-in-out flex-shrink-0 border-r border-slate-700">
      {/* Header with Logo */}
      <div className="p-4 border-b border-slate-700">
        <div className="flex items-center justify-center group-hover:justify-start">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <div className="ml-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300 overflow-hidden">
            <div className="text-sm font-semibold text-white whitespace-nowrap">Data Analysis</div>
            <div className="text-xs text-slate-400 whitespace-nowrap">Chat Assistant</div>
          </div>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-4 border-b border-slate-700">
        <button
          onClick={createNewChat}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 px-3 rounded-lg transition-colors duration-200 flex items-center"
          title="New Chat"
        >
          <div className="flex items-center justify-center w-full group-hover:justify-start group-hover:w-auto">
            <Plus className="w-4 h-4 flex-shrink-0" />
          </div>
          <span className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 font-medium whitespace-nowrap overflow-hidden">
            New Chat
          </span>
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-4">
        <h3 className="text-xs font-medium text-slate-400 mb-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300 uppercase tracking-wide overflow-hidden">
          Recent Chats
        </h3>
        <div className="space-y-1">
          {chats.map((chat) => (
            <button
              key={chat.id}
              onClick={() => selectChat(chat)}
              className={`w-full text-left p-2.5 rounded-lg transition-colors duration-200 flex items-center ${
                currentChat?.id === chat.id 
                  ? 'bg-slate-800 text-white border border-slate-600' 
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
              title={chat.title}
            >
              <div className="flex items-center justify-center flex-shrink-0">
                <MessageCircle className="w-4 h-4 text-slate-400" />
              </div>
              <div className="ml-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300 min-w-0 flex-1 overflow-hidden">
                <div className="text-sm font-medium truncate">{chat.title}</div>
                <div className="text-xs text-slate-500 mt-0.5">
                  {new Date(chat.createdAt).toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric'
                  })}
                </div>
              </div>
            </button>
          ))}
          {chats.length === 0 && (
            <div className="text-slate-500 text-sm text-center py-8 opacity-0 group-hover:opacity-100 transition-opacity duration-300 overflow-hidden">
              <MessageCircle className="w-6 h-6 mx-auto mb-2 text-slate-600" />
              <p className="text-xs">No conversations yet</p>
            </div>
          )}
        </div>
      </div>

      {/* User Profile Section */}
      <div className="p-4 border-t border-slate-700">
        <div className="flex items-center mb-3">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-sm font-medium text-white">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
          <div className="ml-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300 min-w-0 flex-1 overflow-hidden">
            <div className="text-sm font-medium text-white truncate">
              {user?.name || 'User'}
            </div>
            <div className="text-xs text-slate-400 truncate">
              {user?.email || 'user@example.com'}
            </div>
          </div>
        </div>
        
        <button
          onClick={logout}
          className="w-full text-left text-sm text-slate-400 hover:text-white transition-colors duration-200 flex items-center p-2 rounded-lg hover:bg-slate-800"
          title="Sign Out"
        >
          <LogOut className="w-4 h-4 flex-shrink-0" />
          <span className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 font-medium whitespace-nowrap overflow-hidden">
            Sign Out
          </span>
        </button>
      </div>
    </div>
  )
}

export default Sidebar