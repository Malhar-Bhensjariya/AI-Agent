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
  const payload = {
    message,
    file_path: fileData?.file_path || null
  }
  console.log('Sending message:', payload);
  const response = await fetch(`${FLASK_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })

  return handleResponse(response)
}

// Parse CSV/Excel file locally
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
            skipEmptyLines: true
          })
          
          resolve({
            data: results.data,
            headers: Object.keys(results.data[0] || {}),
            filename: file.name,
            size: file.size,
            type: file.type
          })
        } catch (error) {
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
  
  // Future functionality
  authAPI,
  chatAPI,
  messageAPI,
  
  // Legacy (deprecated)
  sendMessageToAgent
}