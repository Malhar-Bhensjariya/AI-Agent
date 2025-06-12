import { useState } from 'react'
import { useAppContext } from '../context/AppContext'
import { sendMessage } from '../services/api'

export const useAgentResponse = () => {
  const { addMessage, setTableView, setError, clearError, activeFile, updateFileData } = useAppContext()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setLocalError] = useState(null)

  const sendAgentMessage = async (message, fileData = null) => {
    setIsLoading(true)
    setLocalError(null)

    try {
      // Fix: Don't try to access file.path - just send the file object
      const fileToSend = fileData || (activeFile ? {
        file: activeFile.file,
        data: activeFile.tableData,
        headers: activeFile.headers,
        filename: activeFile.filename,
        file_path: activeFile.file_path
      } : null)

      // Pass the entire fileToSend object, not just the path
      const response = await sendMessage(message, fileToSend)
      console.log('Agent response:', response);

      if (response.updated_data && activeFile) {
        console.log('Updating file data with backend response:', response.updated_data)
        console.log('Backend headers:', response.headers)
        updateFileData(response.updated_data, response.headers)
      }

      // ✅ Add agent's message to chat
      addMessage({
        id: Date.now() + Math.random(),
        text: response.response || response.text || response.message,
        sender: 'agent',
        timestamp: new Date().toISOString(),
        chartData: response.chartData || response.chart_data || null,
        tableData: response.tableData || response.table_data || null,
        analysis: response.analysis || null
      })

      if (response.showTable || response.show_table || response.tableData) {
        setTableView(true)
      }

      return response
    } catch (err) {
      const errorMessage = err.message || 'An error occurred while processing your request'
      setLocalError(errorMessage)
      setError(errorMessage)

      addMessage({
        id: Date.now() + Math.random(),
        text: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        sender: 'agent',
        timestamp: new Date().toISOString(),
        error: true
      })

      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const regenerateResponse = async (originalMessage, filePath = null) => {
    if (!originalMessage) {
      throw new Error('No original message provided for regeneration')
    }

    setIsLoading(true)
    setLocalError(null)

    try {
      // Fix: Pass the active file instead of just filePath
      const fileToSend = activeFile ? {
        file: activeFile.file,
        data: activeFile.tableData,
        headers: activeFile.headers,
        filename: activeFile.filename,
        file_path: activeFile.file_path
      } : null

      const response = await sendMessage(originalMessage, fileToSend)

      const regeneratedMessage = {
        id: Date.now() + Math.random(),
        text: response.response || response.text || response.message,
        sender: 'agent',
        timestamp: new Date().toISOString(),
        chartData: response.chartData || response.chart_data || null,
        tableData: response.tableData || response.table_data || null,
        analysis: response.analysis || null,
        regenerated: true
      }

      addMessage(regeneratedMessage)

      if (response.showTable || response.show_table || regeneratedMessage.tableData) {
        setTableView(true)
      }

      return response
    } catch (err) {
      const errorMessage = err.message || 'Failed to regenerate response'
      setLocalError(errorMessage)
      setError(errorMessage)

      addMessage({
        id: Date.now() + Math.random(),
        text: `Sorry, I couldn't regenerate the response: ${errorMessage}. Please try again.`,
        sender: 'agent',
        timestamp: new Date().toISOString(),
        error: true
      })

      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const clearAgentError = () => {
    setLocalError(null)
    clearError()
  }

  return {
    sendMessage: sendAgentMessage,
    regenerateResponse,
    clearError: clearAgentError,
    isLoading,
    error
  }
}