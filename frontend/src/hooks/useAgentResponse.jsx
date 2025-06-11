import { useState } from 'react'
import { useAppContext } from '../context/AppContext'
import { sendMessage } from '../services/api'

export const useAgentResponse = () => {
  const { addMessage, setTableView, setError, clearError } = useAppContext()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setLocalError] = useState(null)

  const sendAgentMessage = async (message, filePath = null) => {
    setIsLoading(true)
    setLocalError(null)

    try {
      // Call the updated API service
      const response = await sendMessage(message, filePath)

      // Create agent response message
      const agentMessage = {
        id: Date.now() + Math.random(), // Ensure unique ID
        text: response.response || response.text || response.message,
        sender: 'agent',
        timestamp: new Date().toISOString(),
        chartData: response.chartData || response.chart_data || null,
        tableData: response.tableData || response.table_data || null,
        analysis: response.analysis || null
      }

      // Add agent response to messages
      addMessage(agentMessage)

      // Show table view if response contains table data or if explicitly requested
      if (response.showTable || response.show_table || agentMessage.tableData) {
        setTableView(true)
      }

      return response
    } catch (err) {
      const errorMessage = err.message || 'An error occurred while processing your request'
      setLocalError(errorMessage)
      setError(errorMessage)
      
      // Add error message to chat
      const errorChatMessage = {
        id: Date.now() + Math.random(),
        text: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        sender: 'agent',
        timestamp: new Date().toISOString(),
        error: true
      }
      
      addMessage(errorChatMessage)
      
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
      // Call API again with the same message
      const response = await sendMessage(originalMessage, filePath)

      // Create new agent response message
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

      // Add regenerated response to messages
      addMessage(regeneratedMessage)

      // Show table view if needed
      if (response.showTable || response.show_table || regeneratedMessage.tableData) {
        setTableView(true)
      }

      return response
    } catch (err) {
      const errorMessage = err.message || 'Failed to regenerate response'
      setLocalError(errorMessage)
      setError(errorMessage)
      
      const errorChatMessage = {
        id: Date.now() + Math.random(),
        text: `Sorry, I couldn't regenerate the response: ${errorMessage}. Please try again.`,
        sender: 'agent',
        timestamp: new Date().toISOString(),
        error: true
      }
      
      addMessage(errorChatMessage)
      
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