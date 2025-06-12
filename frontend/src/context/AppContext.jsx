import React, { createContext, useContext, useState } from 'react'

// Create context
const AppContext = createContext()

// Context provider component
export const AppProvider = ({ children }) => {
  // Core state using useState hooks
  const [messages, setMessages] = useState([])
  const [activeFile, setActiveFile] = useState(null) // Renamed for clarity
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
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

  // File management functions - simplified and focused
  const setCurrentFile = (fileData) => {
    console.log('Setting active file:', fileData)
    
    if (!fileData) {
      setActiveFile(null)
      return
    }

    // Structure the file data consistently
    const structuredFile = {
      // File metadata
      filename: fileData.filename || fileData.name || 'Unknown',
      size: fileData.size || 0,
      type: fileData.type || 'text/csv',
      
      // Table data - this is what TableView will use
      tableData: fileData.data || fileData.tableData || [],
      headers: fileData.headers || (fileData.data && fileData.data.length > 0 ? Object.keys(fileData.data[0]) : []),
      
      // Original file object for backend operations
      originalFile: fileData.file || fileData.originalFile || null,
      file_path: fileData.file_path || fileData.filePath || fileData.path || null, // Add fileData.path
      // Parsing info
      parsedAt: new Date().toISOString(),
      rowCount: (fileData.data || fileData.tableData || []).length
    }

    console.log('Structured file data:', structuredFile)
    setActiveFile(structuredFile)
  }

  const updateFileData = (newData, newHeaders = null) => {
    if (!activeFile) {
      console.warn('No active file to update')
      return
    }

    console.log('Updating file data:', newData, 'with headers:', newHeaders)
    
    const updatedFile = {
      ...activeFile,
      tableData: newData,
      headers: newHeaders || activeFile.headers,
      rowCount: newData ? newData.length : 0,
      updatedAt: new Date().toISOString()
    }

    console.log('Updated file data:', updatedFile)
    setActiveFile(updatedFile)
  }

  const clearCurrentFile = () => {
    console.log('Clearing active file')
    setActiveFile(null)
  }

  // Get current table data - this is what components should use
  const getCurrentTableData = () => {
    return activeFile?.tableData || []
  }

  const getCurrentHeaders = () => {
    return activeFile?.headers || []
  }

  // File info getters
  const hasActiveFile = () => {
    return activeFile !== null && Array.isArray(activeFile.tableData) && activeFile.tableData.length > 0
  }

  const getActiveFileName = () => {
    return activeFile?.filename || 'No file loaded'
  }

  const getActiveFileInfo = () => {
    if (!activeFile) return null
    
    return {
      filename: activeFile.filename,
      size: activeFile.size,
      rowCount: activeFile.rowCount,
      headers: activeFile.headers,
      parsedAt: activeFile.parsedAt,
      updatedAt: activeFile.updatedAt
    }
  }

  // Enhanced UI functions
  const clearError = () => setError(null)

  // Enhanced chart functions
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
    // Keep active file - it should persist
  }

  // Auth functions
  const login = (userData) => setUser(userData)
  
  const logout = () => {
    setUser(null)
    clearAll()
    clearCurrentFile() // Clear file on logout
  }

  // Context value
  const contextValue = {
    // State
    messages,
    currentChat,
    currentFile: activeFile, // For backward compatibility
    activeFile, // New clear name
    loading,
    error,
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
    
    // File management
    setCurrentFile,
    updateFileData,
    clearCurrentFile,
    getCurrentTableData,
    getCurrentHeaders,
    hasActiveFile,
    getActiveFileName,
    getActiveFileInfo,
    
    // UI
    setLoading,
    setError,
    clearError,
    updateChartData,
    setAnalysis,
    
    // Chat management
    setCurrentChat,
    createNewChat,
    updateChat,
    updateChatTitle,
    deleteChat,
    clearSession,
    clearAll,
    
    // Auth
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

export default AppContext