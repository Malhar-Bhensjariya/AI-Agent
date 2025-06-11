import { useState } from 'react'
import { useAppContext } from '../context/AppContext'
import { sendMessage } from '../services/api'

export const useAgentResponse = () => {
  const { dispatch } = useAppContext()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const sendAgentMessage = async (message, filePath = null) => {
    setIsLoading(true)
    setError(null)

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
      dispatch({ type: 'ADD_MESSAGE', payload: agentMessage })

      // Show table view if response contains table data or if explicitly requested
      if (response.showTable || response.show_table || agentMessage.tableData) {
        dispatch({ type: 'SET_TABLE_VIEW', payload: true })
      }

      return response
    } catch (err) {
      const errorMessage = err.message || 'An error occurred while processing your request'
      setError(errorMessage)
      
      // Add error message to chat
      const errorChatMessage = {
        id: Date.now() + Math.random(),
        text: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        sender: 'agent',
        timestamp: new Date().toISOString(),
        error: true
      }
      
      dispatch({ type: 'ADD_MESSAGE', payload: errorChatMessage })
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
      
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
    setError(null)

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
      dispatch({ type: 'ADD_MESSAGE', payload: regeneratedMessage })

      // Show table view if needed
      if (response.showTable || response.show_table || regeneratedMessage.tableData) {
        dispatch({ type: 'SET_TABLE_VIEW', payload: true })
      }

      return response
    } catch (err) {
      const errorMessage = err.message || 'Failed to regenerate response'
      setError(errorMessage)
      
      const errorChatMessage = {
        id: Date.now() + Math.random(),
        text: `Sorry, I couldn't regenerate the response: ${errorMessage}. Please try again.`,
        sender: 'agent',
        timestamp: new Date().toISOString(),
        error: true
      }
      
      dispatch({ type: 'ADD_MESSAGE', payload: errorChatMessage })
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
      
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const clearError = () => {
    setError(null)
    dispatch({ type: 'CLEAR_ERROR' })
  }

  return {
    sendMessage: sendAgentMessage,
    regenerateResponse,
    clearError,
    isLoading,
    error
  }
}