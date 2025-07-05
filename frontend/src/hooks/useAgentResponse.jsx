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
      const fileToSend = fileData || (activeFile ? {
        file: activeFile.file,
        data: activeFile.tableData,
        headers: activeFile.headers,
        filename: activeFile.filename,
        file_path: activeFile.file_path
      } : null)

      const response = await sendMessage(message, fileToSend)
      console.log('Agent response:', response);

      if (response.updated_data && activeFile) {
        console.log('Updating file data with backend response:', response.updated_data)
        console.log('Backend headers:', response.headers)
        updateFileData(response.updated_data, response.headers)
      }

      // Extract the display text properly
      let displayText = ''
      let analysisResult = null

      // Handle different response formats
      if (typeof response === 'string') {
        displayText = response
      } else if (response.type === 'chart') {
        // For chart responses, use the message field
        displayText = response.text || response.message || 'Chart generated successfully'
      } else if (response.text) {
        displayText = response.text
      } else if (response.message) {
        displayText = response.message
      } else if (response.response) {
        displayText = response.response
      } else {
        // If response is an object without clear text field, stringify it
        displayText = JSON.stringify(response, null, 2)
      }

      // Ensure displayText is always a string
      if (typeof displayText !== 'string') {
        displayText = String(displayText)
      }

      // Check if the display text is JSON from data analyzer
      if (displayText.trim().startsWith('{')) {
        try {
          analysisResult = JSON.parse(displayText)
          // Format the JSON for better display
          displayText = formatJSONResponse(analysisResult)
        } catch (e) {
          console.log('Response is not valid JSON, displaying as text')
        }
      }

      // Handle chart data from backend
      let chartData = null
      if (response.type === 'chart' && response.chart_config) {
        chartData = {
          config: response.chart_config,
          type: response.chart_type || response.chart_config.type || 'bar'
        }
        // For chart responses, use the message as display text
        displayText = response.text || response.message || 'Chart generated successfully'
        console.log('Chart data prepared:', chartData)
      } else if (response.chartData || response.chart_data) {
        chartData = response.chartData || response.chart_data
        console.log('Legacy chart data format:', chartData)
      }

      // Add agent's message to chat
      addMessage({
        id: Date.now() + Math.random(),
        text: displayText, // This is now guaranteed to be a string
        sender: 'agent',
        timestamp: new Date().toISOString(),
        chartData: chartData,
        tableData: response.tableData || response.table_data || null,
        analysis: analysisResult || response.analysis || null,
        rawAnalysis: analysisResult // Store raw JSON for potential future use
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

  // Format JSON response for better display
  const formatJSONResponse = (jsonData) => {
    if (!jsonData || typeof jsonData !== 'object') {
      return String(jsonData)
    }

    // Handle error responses
    if (jsonData.error) {
      return `❌ Error: ${jsonData.error}`
    }

    const formatted = []
    
    Object.entries(jsonData).forEach(([key, value]) => {
      formatted.push(formatKeyValue(key, value))
    })
    
    return formatted.join('\n\n')
  }

  const formatKeyValue = (key, value) => {
    const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    
    if (value === null || value === undefined) {
      return `${formattedKey}: N/A`
    }
    
    if (typeof value === 'boolean') {
      return `${formattedKey}: ${value ? '✅ Yes' : '❌ No'}`
    }
    
    if (typeof value === 'number') {
      return `${formattedKey}: ${value.toLocaleString()}`
    }
    
    if (typeof value === 'object' && value !== null) {
      if (Array.isArray(value)) {
        return `${formattedKey}:\n${value.map(item => `• ${item}`).join('\n')}`
      } else {
        const subItems = Object.entries(value).map(([k, v]) => `• ${k}: ${v}`).join('\n')
        return `${formattedKey}:\n${subItems}`
      }
    } else {
      return `${formattedKey}: ${value}`
    }
  }

  const regenerateResponse = async (originalMessage, filePath = null) => {
    if (!originalMessage) {
      throw new Error('No original message provided for regeneration')
    }

    setIsLoading(true)
    setLocalError(null)

    try {
      const fileToSend = activeFile ? {
        file: activeFile.file,
        data: activeFile.tableData,
        headers: activeFile.headers,
        filename: activeFile.filename,
        file_path: activeFile.file_path
      } : null

      const response = await sendMessage(originalMessage, fileToSend)

      // Extract the display text properly for regenerated responses
      let displayText = ''
      let analysisResult = null

      // Handle different response formats
      if (typeof response === 'string') {
        displayText = response
      } else if (response.type === 'chart') {
        // For chart responses, use the message field
        displayText = response.text || response.message || 'Chart generated successfully'
      } else if (response.text) {
        displayText = response.text
      } else if (response.message) {
        displayText = response.message
      } else if (response.response) {
        displayText = response.response
      } else {
        // If response is an object without clear text field, stringify it
        displayText = JSON.stringify(response, null, 2)
      }

      // Ensure displayText is always a string
      if (typeof displayText !== 'string') {
        displayText = String(displayText)
      }

      // Check if the display text is JSON from data analyzer
      if (displayText.trim().startsWith('{')) {
        try {
          analysisResult = JSON.parse(displayText)
          displayText = formatJSONResponse(analysisResult)
        } catch (e) {
          console.log('Regenerated response is not valid JSON, displaying as text')
        }
      }

      // Handle chart data from backend for regenerated responses
      let chartData = null
      if (response.type === 'chart' && response.chart_config) {
        chartData = {
          config: response.chart_config,
          type: response.chart_type || response.chart_config.type || 'bar'
        }
        // For chart responses, use the message as display text
        displayText = response.text || response.message || 'Chart generated successfully'
        console.log('Regenerated chart data prepared:', chartData)
      } else if (response.chartData || response.chart_data) {
        chartData = response.chartData || response.chart_data
        console.log('Regenerated legacy chart data format:', chartData)
      }

      const regeneratedMessage = {
        id: Date.now() + Math.random(),
        text: displayText, // This is now guaranteed to be a string
        sender: 'agent',
        timestamp: new Date().toISOString(),
        chartData: chartData,
        tableData: response.tableData || response.table_data || null,
        analysis: analysisResult || response.analysis || null,
        rawAnalysis: analysisResult,
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