const FLASK_URL = import.meta.env.VITE_FLASK_API || 'http://localhost:5000'
import Papa from 'papaparse'

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.error || error.message || `HTTP error! status: ${response.status}`)
  }
  return response.json()
}

// Helper function to get auth headers (for future Node.js backend)
const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken')
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` })
  }
}

// Enhanced cleanDataForJSON function with better NaN/invalid value handling
export const cleanDataForJSON = (data) => {
  if (data === null || data === undefined) {
    return null
  }
  
  if (Array.isArray(data)) {
    return data.map(cleanDataForJSON)
  }
  
  if (data && typeof data === 'object') {
    // Handle Date objects
    if (data instanceof Date) {
      return data.toISOString()
    }
    
    const cleaned = {}
    for (const [key, value] of Object.entries(data)) {
      cleaned[key] = cleanDataForJSON(value)
    }
    return cleaned
  }
  
  // Handle numbers (including NaN and Infinity) - THIS IS THE KEY FIX
  if (typeof data === 'number') {
    if (isNaN(data) || !isFinite(data)) {
      return null  // Convert NaN/Infinity to null
    }
    return data
  }
  
  // Handle strings that might contain "NaN" or other invalid values
  if (typeof data === 'string') {
    const trimmed = data.trim()
    if (trimmed === 'NaN' || trimmed === 'Infinity' || trimmed === '-Infinity' || 
        trimmed === 'undefined' || trimmed === '') {
      return null
    }
    return data
  }
  
  return data
}

// Alternative: More aggressive cleaning function for problematic datasets
export const deepCleanDataForJSON = (data) => {
  // Convert to JSON string and back to handle edge cases
  try {
    const jsonString = JSON.stringify(data, (key, value) => {
      // Handle NaN, Infinity, undefined
      if (typeof value === 'number' && (isNaN(value) || !isFinite(value))) {
        return null
      }
      // Handle string representations of invalid numbers
      if (typeof value === 'string') {
        const trimmed = value.trim()
        if (trimmed === 'NaN' || trimmed === 'Infinity' || trimmed === '-Infinity' || 
            trimmed === 'undefined' || trimmed === '') {
          return null
        }
      }
      return value
    })
    
    return JSON.parse(jsonString)
  } catch (error) {
    console.warn('Failed to clean data, using fallback:', error)
    return cleanDataForJSON(data)
  }
}


// =============================================================================
// CURRENT FLASK APIs - Core Chat Functionality
// =============================================================================

// Upload file for chat analysis
export const uploadFile = async (file, onProgress) => {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    const formData = new FormData()
    formData.append('file', file)
    
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const progress = (event.loaded / event.total) * 100
        if (onProgress) onProgress(progress)
      }
    })

    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        try {
          const response = JSON.parse(xhr.responseText)
          resolve(response)
        } catch (e) {
          reject(new Error('Invalid response format'))
        }
      } else {
        try {
          const errorResponse = JSON.parse(xhr.responseText)
          reject(new Error(errorResponse.error || `Upload failed with status: ${xhr.status}`))
        } catch (e) {
          reject(new Error(`Upload failed with status: ${xhr.status}`))
        }
      }
    })

    xhr.addEventListener('error', () => {
      reject(new Error('Upload failed - network error'))
    })

    xhr.open('POST', `${FLASK_URL}/upload`)
    xhr.send(formData)
  })
}

// Send message in chat (main chat functionality)
// Send message with file data directly
export const sendMessage = async (message, fileData = null) => {
  try {
    const payload = {
      message,
      file_path: fileData?.file_path || null
    }
    
    // CRITICAL: Clean the payload before JSON.stringify
    const cleanedPayload = cleanDataForJSON(payload)
    
    console.log('Sending message:', cleanedPayload)
    
    // Test JSON serialization before sending
    const testSerialization = JSON.stringify(cleanedPayload)
    console.log('JSON serialization test passed')
    
    const response = await fetch(`${FLASK_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: testSerialization
    })

    return handleResponse(response)
  } catch (error) {
    console.error('Error in sendMessage:', error)
    if (error.message && error.message.includes('Unexpected token')) {
      throw new Error('Data contains invalid values (NaN/Infinity). Please clean your data first.')
    }
    throw error
  }
}

export const validateDataForJSON = (data, path = 'root') => {
  const issues = []
  
  const checkValue = (value, currentPath) => {
    if (typeof value === 'number') {
      if (isNaN(value)) {
        issues.push(`NaN found at ${currentPath}`)
      } else if (!isFinite(value)) {
        issues.push(`Infinity found at ${currentPath}`)
      }
    } else if (typeof value === 'string') {
      if (value === 'NaN' || value === 'Infinity' || value === '-Infinity') {
        issues.push(`Invalid string "${value}" found at ${currentPath}`)
      }
    } else if (Array.isArray(value)) {
      value.forEach((item, index) => {
        checkValue(item, `${currentPath}[${index}]`)
      })
    } else if (value && typeof value === 'object') {
      Object.entries(value).forEach(([key, val]) => {
        checkValue(val, `${currentPath}.${key}`)
      })
    }
  }
  
  checkValue(data, path)
  return issues
}

// Parse CSV/Excel file locally
// Updated parseFileLocally function with better data cleaning
export const parseFileLocally = async (file) => {
  return new Promise((resolve, reject) => {
    if (!file) {
      reject(new Error('No file provided'))
      return
    }

    const fileExtension = file.name.split('.').pop().toLowerCase()
    
    if (fileExtension === 'csv') {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const csv = e.target.result
          const results = Papa.parse(csv, {
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
            transform: (value, field) => {
              // Handle empty values first
              if (value === "" || value === undefined || value === null) {
                return null
              }
              
              // Handle string representations of invalid numbers
              if (typeof value === 'string') {
                const trimmed = value.trim()
                if (trimmed === 'NaN' || trimmed === 'Infinity' || trimmed === '-Infinity' || 
                    trimmed === 'undefined' || trimmed === '') {
                  return null
                }
              }
              
              // Handle numeric values - CRITICAL FIX FOR YOUR DATA
              if (typeof value === 'number') {
                if (isNaN(value) || !isFinite(value)) {
                  return null
                }
              }
              
              return value
            }
          })
          
          // Additional cleaning pass - Double protection
          const cleanedData = results.data.map(row => {
            const cleanedRow = {}
            for (const [key, value] of Object.entries(row)) {
              cleanedRow[key] = cleanDataForJSON(value)
            }
            return cleanedRow
          }).filter(row => {
            // Remove completely empty rows
            return Object.values(row).some(val => val !== null && val !== undefined)
          })
          
          console.log(`Parsed ${results.data.length} rows, cleaned to ${cleanedData.length} rows`)
          
          resolve({
            data: cleanedData,
            headers: Object.keys(cleanedData[0] || {}),
            filename: file.name,
            size: file.size,
            type: file.type
          })
        } catch (error) {
          console.error('CSV parsing error:', error)
          reject(error)
        }
      }
      reader.onerror = () => reject(new Error('Failed to read file'))
      reader.readAsText(file)
    } else {
      reject(new Error('Only CSV files are supported for local parsing'))
    }
  })
}


// Health check
export const healthCheck = async () => {
  const response = await fetch(`${FLASK_URL}/health`)
  return handleResponse(response)
}

// Get file URL for download/preview
export const getFileUrl = (filename) => {
  return `${FLASK_URL}/files/${filename}`
}

// =============================================================================
// FUTURE NODE.JS APIs - Chat History & Authentication
// =============================================================================

// Authentication APIs (for future Node.js/SQL backend)
export const authAPI = {
  login: async (credentials) => {
    const response = await fetch(`${FLASK_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    })
    return handleResponse(response)
  },

  register: async (userData) => {
    const response = await fetch(`${FLASK_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    })
    return handleResponse(response)
  },

  logout: async () => {
    const response = await fetch(`${FLASK_URL}/auth/logout`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    return handleResponse(response)
  }
}

// Chat APIs (for future Node.js/SQL backend)
export const chatAPI = {
  getChats: async () => {
    const response = await fetch(`${FLASK_URL}/chats`, {
      headers: getAuthHeaders()
    })
    return handleResponse(response)
  },

  createChat: async (chatData) => {
    const response = await fetch(`${FLASK_URL}/chats`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(chatData)
    })
    return handleResponse(response)
  },

  getChat: async (chatId) => {
    const response = await fetch(`${FLASK_URL}/chats/${chatId}`, {
      headers: getAuthHeaders()
    })
    return handleResponse(response)
  },

  updateChat: async (chatId, updates) => {
    const response = await fetch(`${FLASK_URL}/chats/${chatId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates)
    })
    return handleResponse(response)
  },

  deleteChat: async (chatId) => {
    const response = await fetch(`${FLASK_URL}/chats/${chatId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    return handleResponse(response)
  }
}

// Message APIs (for future Node.js/SQL backend)
export const messageAPI = {
  getMessages: async (chatId) => {
    const response = await fetch(`${FLASK_URL}/chats/${chatId}/messages`, {
      headers: getAuthHeaders()
    })
    return handleResponse(response)
  },

  saveMessage: async (chatId, messageData) => {
    const response = await fetch(`${FLASK_URL}/chats/${chatId}/messages`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(messageData)
    })
    return handleResponse(response)
  }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

// Check if backend is healthy
export const isBackendHealthy = async () => {
  try {
    const result = await healthCheck()
    return result.status === 'healthy'
  } catch (error) {
    return false
  }
}

// Format file size for display
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// =============================================================================
// LEGACY COMPATIBILITY (deprecated - use sendMessage instead)
// =============================================================================

export const sendMessageToAgent = async (data) => {
  console.warn('sendMessageToAgent is deprecated, use sendMessage instead')
  return sendMessage(data.message, data.file_path || data.filePath)
}

// =============================================================================
// MAIN EXPORT
// =============================================================================

export default {
  // Core functionality (current)
  uploadFile,
  sendMessage,
  healthCheck,
  getFileUrl,
  isBackendHealthy,
  formatFileSize,
  cleanDataForJSON,
  
  // Future functionality
  authAPI,
  chatAPI,
  messageAPI,
  
  // Legacy (deprecated)
  sendMessageToAgent
}