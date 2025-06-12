import { useState } from 'react'
import { uploadFile as uploadFileAPI, parseFileLocally } from '../services/api'
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

    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      throw new Error('File size too large. Please upload files smaller than 10MB.')
    }

    setIsUploading(true)
    setLocalError(null)
    setUploadProgress(0)

    try {
      // Parse file locally first
      const parsedData = await parseFileLocally(file)

      // Upload to backend for processing
      const response = await uploadFileAPI(file, (progress) => {
        setUploadProgress(Math.round(progress))
      })

      const fileInfo = {
        id: response.file_id || response.fileId || Date.now(),
        filename: file.name,
        type: file.type,
        size: file.size,
        path: response.file_path || response.filePath,
        file_path: response.file_path || response.filePath,
        uploadedAt: new Date().toISOString(),
        status: 'uploaded',
        // Use locally parsed data
        data: parsedData.data,
        tableData: parsedData.data,
        headers: parsedData.headers,
        file: file // Store original file
      }

      console.log('Processed file info:', fileInfo)

      // Ensure preview data is properly stored in context
      const finalFileInfo = {
        ...fileInfo,
        preview: fileInfo.preview || fileInfo.tableData || null
      }

      setCurrentFile(fileInfo)
      clearError()

      return fileInfo
    } catch (err) {
      const errorMessage = err.message || 'Upload failed'
      setLocalError(errorMessage)
      setError(errorMessage)
      throw err
    } finally {
      setIsUploading(false)
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }

  const validateFileExtension = (fileName) => {
    const allowedExtensions = ['.csv', '.xlsx', '.xls', '.json', '.txt', '.pdf', '.tsv']
    const ext = fileName.toLowerCase().substring(fileName.lastIndexOf('.'))
    return allowedExtensions.includes(ext)
  }

  const validateFileType = (file) => {
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