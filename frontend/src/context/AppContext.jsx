import React, { createContext, useContext, useState } from 'react'

// Create context
const AppContext = createContext()

// Context provider component
export const AppProvider = ({ children }) => {
  // Core state using useState hooks
  const [messages, setMessages] = useState([])
  const [currentFile, setCurrentFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [tableData, setTableData] = useState(null)
  const [chartData, setChartData] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [currentChat, setCurrentChat] = useState(null)
  const [chats, setChats] = useState([])
  const [user, setUser] = useState(null)

  // Enhanced message functions
  const addMessage = (message) => {
    const messageWithId = {
      id: Date.now() + Math.random(),
      timestamp: new Date().toISOString(),
      ...message
    }
    setMessages(prev => [...prev, messageWithId])
    setError(null)
  }

  const updateMessage = (id, updates) => {
    setMessages(prev => prev.map(msg => 
      msg.id === id ? { ...msg, ...updates } : msg
    ))
  }

  const deleteMessage = (id) => {
    setMessages(prev => prev.filter(msg => msg.id !== id))
  }

  const clearMessages = () => {
    setMessages([])
    setError(null)
  }

  // Enhanced file functions
  const setActiveFile = (file) => {
    setCurrentFile(file)
    // When a new file is set, update table data if available
    if (file && file.tableData) {
      setTableData(file.tableData)
    } else if (file && file.preview) {
      // If file has preview data, use that for table
      setTableData(file.preview)
    } else {
      // Clear table data if no file data available
      setTableData(null)
    }
  }

  const clearCurrentFile = () => {
    setCurrentFile(null)
    setTableData(null)
  }

  // Enhanced UI functions
  const clearError = () => setError(null)

  // Enhanced data functions - always update table data for active file
  const updateTableData = (data) => {
    setTableData(data)
    // Also update the current file's table data if available
    if (currentFile) {
      setCurrentFile(prev => ({
        ...prev,
        tableData: data
      }))
    }
  }

  const updateChartData = (data) => setChartData(data)

  // Enhanced chat functions
  const createNewChat = () => {
    const newChat = {
      id: Date.now() + Math.random(),
      title: 'New Chat',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    setChats(prev => [...prev, newChat])
    setCurrentChat(newChat)
    clearMessages()
    return newChat
  }

  const updateChat = (id, updates) => {
    setChats(prev => prev.map(chat => 
      chat.id === id ? { ...chat, ...updates } : chat
    ))
  }

  const updateChatTitle = (chatId, title) => {
    updateChat(chatId, { title, updatedAt: new Date().toISOString() })
  }

  const deleteChat = (id) => {
    setChats(prev => prev.filter(chat => chat.id !== id))
    if (currentChat?.id === id) setCurrentChat(null)
  }

  // Session management
  const clearSession = () => {
    clearMessages()
    clearError()
  }

  const clearAll = () => {
    clearSession()
    setChartData(null)
    setAnalysis(null)
    // Don't clear current file and table data - keep them persistent
  }

  // Auth functions
  const login = (userData) => setUser(userData)
  
  const logout = () => {
    setUser(null)
    clearAll()
    clearCurrentFile() // Only clear file on logout
  }

  // Context value
  const contextValue = {
    // State
    messages,
    currentChat,
    currentFile,
    loading,
    error,
    tableData,
    chartData,
    analysis,
    chats,
    user,
    
    // Functions
    addMessage,
    updateMessage,
    deleteMessage,
    setMessages,
    clearMessages,
    setCurrentFile: setActiveFile, // Use the enhanced version
    clearCurrentFile,
    setLoading,
    setError,
    clearError,
    updateTableData,
    updateChartData,
    setAnalysis,
    setCurrentChat,
    createNewChat,
    updateChat,
    updateChatTitle,
    deleteChat,
    clearSession,
    clearAll,
    login,
    logout,
    setUser
  }

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  )
}

// Custom hook to use the context
export const useAppContext = () => {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider')
  }
  return context
}

// Action types export for backward compatibility (if needed)
export const ActionTypes = {
  ADD_MESSAGE: 'ADD_MESSAGE',
  UPDATE_MESSAGE: 'UPDATE_MESSAGE',
  DELETE_MESSAGE: 'DELETE_MESSAGE',
  SET_MESSAGES: 'SET_MESSAGES',
  CLEAR_MESSAGES: 'CLEAR_MESSAGES',
  SET_CURRENT_FILE: 'SET_CURRENT_FILE',
  CLEAR_CURRENT_FILE: 'CLEAR_CURRENT_FILE',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_TABLE_DATA: 'SET_TABLE_DATA',
  SET_CHART_DATA: 'SET_CHART_DATA',
  SET_ANALYSIS: 'SET_ANALYSIS',
  SET_CURRENT_CHAT: 'SET_CURRENT_CHAT',
  ADD_CHAT: 'ADD_CHAT',
  UPDATE_CHAT: 'UPDATE_CHAT',
  DELETE_CHAT: 'DELETE_CHAT',
  SET_USER: 'SET_USER'
}

export default AppContext