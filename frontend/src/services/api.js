const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.message || `HTTP error! status: ${response.status}`)
  }
  return response.json()
}

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken')
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` })
  }
}

// Authentication APIs
export const authAPI = {
  login: async (credentials) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    })
    return handleResponse(response)
  },

  register: async (userData) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    })
    return handleResponse(response)
  },

  logout: async () => {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    return handleResponse(response)
  }
}

// Chat APIs
export const chatAPI = {
  getChats: async () => {
    const response = await fetch(`${API_BASE_URL}/chats`, {
      headers: getAuthHeaders()
    })
    return handleResponse(response)
  },

  createChat: async (chatData) => {
    const response = await fetch(`${API_BASE_URL}/chats`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(chatData)
    })
    return handleResponse(response)
  },

  getChat: async (chatId) => {
    const response = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
      headers: getAuthHeaders()
    })
    return handleResponse(response)
  },

  updateChat: async (chatId, updates) => {
    const response = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates)
    })
    return handleResponse(response)
  },

  deleteChat: async (chatId) => {
    const response = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    return handleResponse(response)
  }
}

// Message APIs
export const messageAPI = {
  getMessages: async (chatId) => {
    const response = await fetch(`${API_BASE_URL}/chats/${chatId}/messages`, {
      headers: getAuthHeaders()
    })
    return handleResponse(response)
  },

  sendMessage: async (chatId, messageData) => {
    const response = await fetch(`${API_BASE_URL}/chats/${chatId}/messages`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(messageData)
    })
    return handleResponse(response)
  }
}

// File upload API
export const uploadFile = async (formData, onProgress) => {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    
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
        reject(new Error(`Upload failed with status: ${xhr.status}`))
      }
    })

    xhr.addEventListener('error', () => {
      reject(new Error('Upload failed'))
    })

    const token = localStorage.getItem('authToken')
    xhr.open('POST', `${API_BASE_URL}/upload`)
    if (token) {
      xhr.setRequestHeader('Authorization', `Bearer ${token}`)
    }
    
    xhr.send(formData)
  })
}

// Agent API
export const sendMessageToAgent = async (data) => {
  try {
    const response = await fetch(`${API_BASE_URL}/agent/chat`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    })
    return handleResponse(response)
  } catch (error) {
    // Mock response for development
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          text: `I received your message: "${data.message}". ${data.file ? `And I can see you uploaded a file: ${data.file.name}` : ''}`,
          chartData: Math.random() > 0.5 ? {
            title: 'Sample Chart',
            type: 'bar',
            description: 'This is a sample chart generated from your data'
          } : null,
          showTable: Math.random() > 0.7
        })
      }, 1000 + Math.random() * 2000)
    })
  }
}

// Data analysis APIs
export const dataAPI = {
  analyzeData: async (fileId, analysisType) => {
    const response = await fetch(`${API_BASE_URL}/data/analyze`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ fileId, analysisType })
    })
    return handleResponse(response)
  },

  generateChart: async (fileId, chartConfig) => {
    const response = await fetch(`${API_BASE_URL}/data/chart`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ fileId, chartConfig })
    })
    return handleResponse(response)
  },

  getTableData: async (fileId, page = 1, limit = 50) => {
    const response = await fetch(`${API_BASE_URL}/data/table?fileId=${fileId}&page=${page}&limit=${limit}`, {
      headers: getAuthHeaders()
    })
    return handleResponse(response)
  }
}

export default {
  authAPI,
  chatAPI,
  messageAPI,
  uploadFile,
  sendMessageToAgent,
  dataAPI
}