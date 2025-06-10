import { useState } from 'react'
import { uploadFile as uploadFileAPI } from '../services/api'

export const useUploadTask = () => {
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
      'text/plain'
    ]

    if (!allowedTypes.includes(file.type)) {
      throw new Error('Unsupported file type. Please upload CSV, Excel, JSON, or text files.')
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
      // Create FormData for file upload
      const formData = new FormData()
      formData.append('file', file)

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + 10
        })
      }, 100)

      // Upload file
      const response = await uploadFileAPI(formData, (progress) => {
        setUploadProgress(progress)
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      // Return file info with upload response
      return {
        id: response.fileId,
        name: file.name,
        type: file.type,
        size: file.size,
        data: response.data,
        uploadedAt: new Date().toISOString()
      }
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setIsUploading(false)
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }

  const validateFileType = (file) => {
    const allowedExtensions = ['.csv', '.xlsx', '.xls', '.json', '.txt']
    const fileName = file.name.toLowerCase()
    return allowedExtensions.some(ext => fileName.endsWith(ext))
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return {
    uploadFile,
    validateFileType,
    formatFileSize,
    isUploading,
    uploadProgress,
    error
  }
}