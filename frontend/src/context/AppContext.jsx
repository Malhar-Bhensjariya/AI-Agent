import React, { createContext, useContext, useState, useReducer } from 'react'

const AppContext = createContext()

const initialState = {
  // Current session state
  messages: [],
  currentFile: null, // Currently uploaded file info
  
  // UI state
  isTableViewVisible: false,
  loading: false,
  error: null,
  
  // Future chat history (when Node.js backend is added)
  currentChat: null,
  chats: [],
  
  // Authentication (future)
  user: null
}

function appReducer(state, action) {
  switch (action.type) {
    // Message management
    case 'ADD_MESSAGE':
      return { 
        ...state, 
        messages: [...state.messages, action.payload],
        error: null // Clear any previous errors when adding message
      }
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload }
    case 'CLEAR_MESSAGES':
      return { ...state, messages: [] }
    
    // File management
    case 'SET_CURRENT_FILE':
      return { ...state, currentFile: action.payload }
    case 'CLEAR_CURRENT_FILE':
      return { ...state, currentFile: null }
    
    // UI state
    case 'TOGGLE_TABLE_VIEW':
      return { ...state, isTableViewVisible: !state.isTableViewVisible }
    case 'SET_TABLE_VIEW':
      return { ...state, isTableViewVisible: action.payload }
    case 'SET_LOADING':
      return { ...state, loading: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    case 'CLEAR_ERROR':
      return { ...state, error: null }
    
    // Future chat history features
    case 'SET_CURRENT_CHAT':
      return { ...state, currentChat: action.payload }
    case 'ADD_CHAT':
      return { ...state, chats: [...state.chats, action.payload] }
    case 'UPDATE_CHAT':
      return { 
        ...state, 
        chats: state.chats.map(chat => 
          chat.id === action.payload.id ? { ...chat, ...action.payload.updates } : chat
        )
      }
    case 'DELETE_CHAT':
      return { 
        ...state, 
        chats: state.chats.filter(chat => chat.id !== action.payload),
        currentChat: state.currentChat?.id === action.payload ? null : state.currentChat
      }
    
    // Authentication (future)
    case 'SET_USER':
      return { ...state, user: action.payload }
    
    default:
      return state
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState)
  const [isLoggedIn, setIsLoggedIn] = useState(true)  //For now true so we can develop easily without authentication

  // Authentication functions (future)
  const login = (userData) => {
    setIsLoggedIn(true)
    dispatch({ type: 'SET_USER', payload: userData })
  }

  const logout = () => {
    setIsLoggedIn(false)
    dispatch({ type: 'SET_USER', payload: null })
    // Clear session data on logout
    dispatch({ type: 'CLEAR_MESSAGES' })
    dispatch({ type: 'CLEAR_CURRENT_FILE' })
  }

  // Current session management
  const addMessage = (message) => {
    const messageWithId = {
      id: Date.now() + Math.random(), // Ensure unique ID
      timestamp: new Date().toISOString(),
      ...message
    }
    dispatch({ type: 'ADD_MESSAGE', payload: messageWithId })
  }

  const clearSession = () => {
    dispatch({ type: 'CLEAR_MESSAGES' })
    dispatch({ type: 'CLEAR_CURRENT_FILE' })
    dispatch({ type: 'CLEAR_ERROR' })
  }

  const setCurrentFile = (fileInfo) => {
    dispatch({ type: 'SET_CURRENT_FILE', payload: fileInfo })
  }

  // Future chat history functions
  const createNewChat = () => {
    const newChat = {
      id: Date.now(),
      title: 'New Chat',
      createdAt: new Date().toISOString()
    }
    dispatch({ type: 'ADD_CHAT', payload: newChat })
    dispatch({ type: 'SET_CURRENT_CHAT', payload: newChat })
    dispatch({ type: 'SET_MESSAGES', payload: [] })
  }

  const updateChatTitle = (chatId, title) => {
    dispatch({ 
      type: 'UPDATE_CHAT', 
      payload: { id: chatId, updates: { title } }
    })
  }

  // Error and loading helpers
  const setLoading = (loading) => {
    dispatch({ type: 'SET_LOADING', payload: loading })
  }

  const setError = (error) => {
    dispatch({ type: 'SET_ERROR', payload: error })
  }

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  const value = {
    // State
    ...state,
    isLoggedIn,
    
    // Authentication (future)
    login,
    logout,
    
    // Current session management
    addMessage,
    clearSession,
    setCurrentFile,
    
    // Future chat history
    createNewChat,
    updateChatTitle,
    
    // UI helpers
    setLoading,
    setError,
    clearError,
    
    // Raw dispatch for complex operations
    dispatch
  }

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  )
}

export function useAppContext() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider')
  }
  return context
}