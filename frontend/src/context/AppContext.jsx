import React, { createContext, useContext, useState, useReducer } from 'react'

const AppContext = createContext()

const initialState = {
  currentChat: null,
  chats: [],
  messages: [],
  isTableViewVisible: false,
  user: null,
  loading: false,
  error: null
}

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_CURRENT_CHAT':
      return { ...state, currentChat: action.payload }
    case 'ADD_CHAT':
      return { ...state, chats: [...state.chats, action.payload] }
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload }
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] }
    case 'TOGGLE_TABLE_VIEW':
      return { ...state, isTableViewVisible: !state.isTableViewVisible }
    case 'SET_TABLE_VIEW':
      return { ...state, isTableViewVisible: action.payload }
    case 'SET_USER':
      return { ...state, user: action.payload }
    case 'SET_LOADING':
      return { ...state, loading: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    default:
      return state
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  const login = (userData) => {
    setIsLoggedIn(true)
    dispatch({ type: 'SET_USER', payload: userData })
  }

  const logout = () => {
    setIsLoggedIn(false)
    dispatch({ type: 'SET_USER', payload: null })
  }

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

  const value = {
    ...state,
    isLoggedIn,
    login,
    logout,
    createNewChat,
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