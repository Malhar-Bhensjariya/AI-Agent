import { useState } from 'react'
import { useAppContext } from '../context/AppContext'
import { sendMessageToAgent } from '../services/api'

export const useAgentResponse = () => {
  const { dispatch } = useAppContext()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const sendMessage = async (message, file = null) => {
    setIsLoading(true)
    setError(null)

    try {
      // Call API to send message to agent
      const response = await sendMessageToAgent({
        message,
        file: file ? {
          name: file.name,
          type: file.type,
          data: file.data
        } : null
      })

      // Create agent response message
      const agentMessage = {
        id: Date.now() + 1,
        text: response.text,
        sender: 'agent',
        timestamp: new Date().toISOString(),
        chartData: response.chartData || null
      }

      // Add agent response to messages
      dispatch({ type: 'ADD_MESSAGE', payload: agentMessage })

      // Show table view if requested
      if (response.showTable) {
        dispatch({ type: 'SET_TABLE_VIEW', payload: true })
      }

      return response
    } catch (err) {
      setError(err.message)
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'agent',
        timestamp: new Date().toISOString(),
        error: true
      }
      
      dispatch({ type: 'ADD_MESSAGE', payload: errorMessage })
      
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const regenerateResponse = async (messageId) => {
    // Implementation for regenerating a specific response
    setIsLoading(true)
    try {
      // Find the original user message and regenerate response
      // This would involve calling the API again with the same parameters
      console.log('Regenerating response for message:', messageId)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return {
    sendMessage,
    regenerateResponse,
    isLoading,
    error
  }
}