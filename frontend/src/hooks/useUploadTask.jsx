import { useState } from 'react'
import { uploadFile as uploadFileAPI } from '../services/api'
import { useAppContext } from '../context/AppContext'

export const useUploadTask = () => {
  const { setCurrentFile, setError, clearError, updateTableData } = useAppContext()
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setLocalError] = useState(null)

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
    setLocalError(null)
    setUploadProgress(0)

    try {
      // Upload file using the API service
      const response = await uploadFileAPI(file, (progress) => {
        setUploadProgress(Math.round(progress))
      })

      // Create file info object with enhanced data handling
      const fileInfo = {
        id: response.file_id || response.fileId || Date.now(),
        name: file.name,
        type: file.type,
        size: file.size,
        path: response.file_path || response.filePath,
        uploadedAt: new Date().toISOString(),
        status: 'uploaded',
        preview: response.preview || null,
        summary: response.summary || null,
        tableData: response.table_data || response.tableData || response.preview || null
      }

      // Update context with current file (this will automatically update table data)
      setCurrentFile(fileInfo)

      // If we have table data from the upload response, update it
      if (fileInfo.tableData) {
        updateTableData(fileInfo.tableData)
      }

      // Clear any previous errors
      clearError()

      return fileInfo
    } catch (err) {
      const errorMessage = err.message || 'Upload failed'
      setLocalError(errorMessage)
      setError(errorMessage)
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
    setCurrentFile(null)
    setLocalError(null)
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

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const clearUploadError = () => {
    setLocalError(null)
    clearError()
  }

  return {
    uploadFile,
    validateFileType,
    validateFileExtension,
    removeFile,
    getFilePreview,
    clearError: clearUploadError,
    formatFileSize,
    isUploading,
    uploadProgress,
    error
  }
}