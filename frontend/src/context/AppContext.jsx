import React, { createContext, useContext, useState, useCallback } from 'react'

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
  const [tableView, setTableView] = useState(false) // Add this missing state

  // Enhanced message functions
  const addMessage = useCallback((message) => {
    const messageWithId = {
      id: Date.now() + Math.random(),
      timestamp: new Date().toISOString(),
      ...message
    }
    setMessages(prev => [...prev, messageWithId])
    setError(null)
  }, [])

  const updateMessage = useCallback((id, updates) => {
    setMessages(prev => prev.map(msg => 
      msg.id === id ? { ...msg, ...updates } : msg
    ))
  }, [])

  const deleteMessage = useCallback((id) => {
    setMessages(prev => prev.filter(msg => msg.id !== id))
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  // File management functions - simplified and focused
  const setCurrentFile = useCallback((fileData) => {
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
      file_path: fileData.file_path || fileData.filePath || fileData.path || null,
      
      // Parsing info
      parsedAt: new Date().toISOString(),
      rowCount: (fileData.data || fileData.tableData || []).length,
      
      // Add analysis tracking
      lastAnalysis: null,
      analysisHistory: [],

      // Add a unique update ID to force re-renders
      updateId: Date.now() + Math.random()
    }

    console.log('Structured file data:', structuredFile)
    setActiveFile(structuredFile)
  }, [])

  const updateFileData = useCallback((newData, newHeaders = null) => {
    console.log('Updating file data:', newData, 'with headers:', newHeaders)
    
    setActiveFile(prevFile => {
      if (!prevFile) {
        console.warn('No active file to update')
        return prevFile
      }

      const updatedFile = {
        ...prevFile,
        tableData: newData,
        headers: newHeaders || prevFile.headers,
        rowCount: newData ? newData.length : 0,
        updatedAt: new Date().toISOString(),
        // Force re-render with new update ID
        updateId: Date.now() + Math.random()
      }

      console.log('Updated file data:', updatedFile)
      return updatedFile
    })
  }, [])

  // Add analysis tracking
  const addAnalysisToFile = useCallback((analysisType, analysisResult) => {
    if (!activeFile) return

    const analysis = {
      type: analysisType,
      result: analysisResult,
      timestamp: new Date().toISOString()
    }

    setActiveFile(prev => ({
      ...prev,
      lastAnalysis: analysis,
      analysisHistory: [...(prev.analysisHistory || []), analysis],
      updateId: Date.now() + Math.random() // Force re-render
    }))
  }, [activeFile])

  const clearCurrentFile = useCallback(() => {
    console.log('Clearing active file')
    setActiveFile(null)
    setTableView(false) // Also hide table view when clearing file
  }, [])

  // Get current table data - these are memoized with activeFile as dependency
  const getCurrentTableData = useCallback(() => {
    return activeFile?.tableData || []
  }, [activeFile?.tableData, activeFile?.updateId])

  const getCurrentHeaders = useCallback(() => {
    return activeFile?.headers || []
  }, [activeFile?.headers, activeFile?.updateId])

  // File info getters
  const hasActiveFile = useCallback(() => {
    return activeFile !== null && Array.isArray(activeFile?.tableData) && activeFile.tableData.length > 0
  }, [activeFile?.tableData, activeFile?.updateId])

  const getActiveFileName = useCallback(() => {
    return activeFile?.filename || 'No file loaded'
  }, [activeFile?.filename, activeFile?.updateId])

  const getActiveFileInfo = useCallback(() => {
    if (!activeFile) return null
    
    return {
      filename: activeFile.filename,
      size: activeFile.size,
      rowCount: activeFile.rowCount,
      headers: activeFile.headers,
      parsedAt: activeFile.parsedAt,
      updatedAt: activeFile.updatedAt,
      lastAnalysis: activeFile.lastAnalysis,
      analysisCount: activeFile.analysisHistory?.length || 0,
      updateId: activeFile.updateId
    }
  }, [activeFile])

  // Enhanced UI functions
  const clearError = useCallback(() => setError(null), [])

  // Enhanced chart functions
  const updateChartData = useCallback((data) => setChartData(data), [])

  // Enhanced chat functions
  const createNewChat = useCallback(() => {
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
  }, [clearMessages])

  const updateChat = useCallback((id, updates) => {
    setChats(prev => prev.map(chat => 
      chat.id === id ? { ...chat, ...updates } : chat
    ))
  }, [])

  const updateChatTitle = useCallback((chatId, title) => {
    updateChat(chatId, { title, updatedAt: new Date().toISOString() })
  }, [updateChat])

  const deleteChat = useCallback((id) => {
    setChats(prev => prev.filter(chat => chat.id !== id))
    if (currentChat?.id === id) setCurrentChat(null)
  }, [currentChat])

  // Session management
  const clearSession = useCallback(() => {
    clearMessages()
    clearError()
    setTableView(false)
  }, [clearMessages, clearError])

  const clearAll = useCallback(() => {
    clearSession()
    setChartData(null)
    setAnalysis(null)
    // Keep active file - it should persist
  }, [clearSession])

  // Auth functions
  const login = useCallback((userData) => setUser(userData), [])
  
  const logout = useCallback(() => {
    setUser(null)
    clearAll()
    clearCurrentFile() // Clear file on logout
  }, [clearAll, clearCurrentFile])

  // Context value - memoize stable references
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
    tableView,
    
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
    addAnalysisToFile,
    
    // UI
    setLoading,
    setError,
    clearError,
    updateChartData,
    setAnalysis,
    setTableView,
    
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