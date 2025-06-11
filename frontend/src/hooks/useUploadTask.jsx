import { useState } from 'react'
import { uploadFile as uploadFileAPI, formatFileSize } from '../services/api'
import { useAppContext } from '../context/AppContext'

export const useUploadTask = () => {
  const { dispatch } = useAppContext()
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState(null)

  const uploadFile = async (file) => {
    if (!file) {
      throw new Error('No file provided')
    }

    // Validate file type
    const allowedTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/json',
      'text/plain',
      'application/pdf',
      'text/tab-separated-values'
    ]

    if (!allowedTypes.includes(file.type) && !validateFileExtension(file.name)) {
      throw new Error('Unsupported file type. Please upload CSV, Excel, JSON, PDF, or text files.')
    }

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      throw new Error('File size too large. Please upload files smaller than 10MB.')
    }

    setIsUploading(true)
    setError(null)
    setUploadProgress(0)

    try {
      // Upload file using the API service
      const response = await uploadFileAPI(file, (progress) => {
        setUploadProgress(Math.round(progress))
      })

      // Create file info object
      const fileInfo = {
        id: response.file_id || response.fileId || Date.now(),
        name: file.name,
        type: file.type,
        size: file.size,
        path: response.file_path || response.filePath,
        uploadedAt: new Date().toISOString(),
        status: 'uploaded',
        preview: response.preview || null,
        summary: response.summary || null
      }

      // Update context with current file
      dispatch({ type: 'SET_CURRENT_FILE', payload: fileInfo })

      // Clear any previous errors
      dispatch({ type: 'CLEAR_ERROR' })

      return fileInfo
    } catch (err) {
      const errorMessage = err.message || 'Upload failed'
      setError(errorMessage)
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
      throw err
    } finally {
      setIsUploading(false)
      // Reset progress after a short delay
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }

  const validateFileExtension = (fileName) => {
    const allowedExtensions = ['.csv', '.xlsx', '.xls', '.json', '.txt', '.pdf', '.tsv']
    const fileExtension = fileName.toLowerCase().substring(fileName.lastIndexOf('.'))
    return allowedExtensions.includes(fileExtension)
  }

  const validateFileType = (file) => {
    // Check both MIME type and file extension
    const allowedTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/json',
      'text/plain',
      'application/pdf',
      'text/tab-separated-values'
    ]
    
    return allowedTypes.includes(file.type) || validateFileExtension(file.name)
  }

  const removeFile = () => {
    dispatch({ type: 'CLEAR_CURRENT_FILE' })
    setError(null)
    setUploadProgress(0)
  }

  const getFilePreview = (file) => {
    // Generate preview information for the file
    return {
      name: file.name,
      size: formatFileSize(file.size),
      type: file.type,
      lastModified: new Date(file.lastModified).toLocaleDateString()
    }
  }

  const clearError = () => {
    setError(null)
    dispatch({ type: 'CLEAR_ERROR' })
  }

  return {
    uploadFile,
    validateFileType,
    validateFileExtension,
    removeFile,
    getFilePreview,
    clearError,
    formatFileSize,
    isUploading,
    uploadProgress,
    error
  }
}