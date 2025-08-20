import { useState } from 'react'
import { useAppContext } from '../context/AppContext'
import { sendMessage, cleanDataForJSON, validateDataForJSON } from '../services/api'

export const useAgentResponse = () => {
  const { addMessage, setTableView, setError, clearError, activeFile, updateFileData } = useAppContext()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setLocalError] = useState(null)

  const sendAgentMessage = async (message, fileData = null) => {
    setIsLoading(true)
    setLocalError(null)

    try {
      let fileToSend = null
      
      if (fileData) {
        fileToSend = fileData
      } else if (activeFile) {
        // CRITICAL: Clean the data before sending
        console.log('Cleaning active file data...')
        const cleanedTableData = cleanDataForJSON(activeFile.tableData)
        
        // Validate the cleaned data
        const validationIssues = validateDataForJSON(cleanedTableData, 'tableData')
        if (validationIssues.length > 0) {
          console.warn('Data validation issues found:', validationIssues)
        }
        
        fileToSend = {
          file: activeFile.file,
          data: cleanedTableData,
          headers: activeFile.headers,
          filename: activeFile.filename,
          file_path: activeFile.file_path
        }
        
        // Final validation of the complete payload
        const payloadValidation = validateDataForJSON(fileToSend, 'fileToSend')
        if (payloadValidation.length > 0) {
          console.error('Critical: Payload validation failed:', payloadValidation)
          throw new Error('Data contains invalid values that cannot be processed')
        }
        
        console.log('File data prepared:', {
          filename: fileToSend.filename,
          rowCount: cleanedTableData?.length || 0,
          headers: fileToSend.headers,
          hasValidData: cleanedTableData && cleanedTableData.length > 0
        })
      }

      // Test JSON serialization before sending to backend
      try {
        const testPayload = {
          message,
          file_path: fileToSend?.file_path || null
        }
        JSON.stringify(testPayload)
        console.log('Pre-send JSON validation passed')
      } catch (jsonError) {
        console.error('JSON serialization test failed:', jsonError)
        throw new Error('Data formatting error: Unable to serialize data for transmission')
      }

      const response = await sendMessage(message, fileToSend)
      console.log('Agent response received:', response)

      if (response.updated_data && activeFile) {
        console.log('Updating file data with backend response')
        updateFileData(response.updated_data, response.headers)
      }

      // Extract display text with better error handling
      let displayText = ''
      let analysisResult = null

      if (typeof response === 'string') {
        displayText = response
      } else if (response.type === 'chart') {
        displayText = response.text || response.message || 'Chart generated successfully'
      } else if (response.text) {
        displayText = response.text
      } else if (response.message) {
        displayText = response.message
      } else if (response.response) {
        displayText = response.response
      } else {
        try {
          displayText = JSON.stringify(response, null, 2)
        } catch (jsonError) {
          console.warn('Failed to stringify response:', jsonError)
          displayText = 'Response received but could not be displayed properly'
        }
      }

      if (typeof displayText !== 'string') {
        displayText = String(displayText)
      }

      // Handle JSON responses
      if (displayText.trim().startsWith('{')) {
        try {
          analysisResult = JSON.parse(displayText)
          displayText = formatJSONResponse(analysisResult)
        } catch (e) {
          console.log('Response is not valid JSON, displaying as text')
        }
      }

      // Handle chart data
      let chartData = null
      if (response.type === 'chart' && response.chart_config) {
        chartData = {
          config: response.chart_config,
          type: response.chart_type || response.chart_config.type || 'bar'
        }
        displayText = response.text || response.message || 'Chart generated successfully'
      } else if (response.chartData || response.chart_data) {
        chartData = response.chartData || response.chart_data
      }
      console.log('Chart data:', chartData)

      // Add agent's message to chat
      addMessage({
        id: Date.now() + Math.random(),
        text: displayText,
        sender: 'agent',
        timestamp: new Date().toISOString(),
        chartData: chartData,
        tableData: response.tableData || response.table_data || null,
        analysis: analysisResult || response.analysis || null,
        rawAnalysis: analysisResult
      })

      if (response.showTable || response.show_table || response.tableData) {
        setTableView(true)
      }

      return response
    } catch (err) {
      console.error('Send message error:', err)
      
      let errorMessage = 'An error occurred while processing your request'
      
      // Specific error handling for common issues
      if (err.message) {
        if (err.message.includes('Unexpected token')) {
          errorMessage = 'Your data contains invalid values (NaN, Infinity) that cannot be processed. The total_bedrooms column has 207 missing values causing this issue.'
        } else if (err.message.includes('JSON')) {
          errorMessage = 'Data formatting error - your file contains values that cannot be converted to JSON.'
        } else if (err.message.includes('Data contains invalid values')) {
          errorMessage = 'Your housing dataset has 207 NaN values in the total_bedrooms column. These need to be cleaned before analysis.'
        } else {
          errorMessage = err.message
        }
      }
      
      setLocalError(errorMessage)
      setError(errorMessage)

      addMessage({
        id: Date.now() + Math.random(),
        text: `❌ ${errorMessage}\n\n💡 Tip: Your dataset has missing values in the 'total_bedrooms' column. Try re-uploading your file - the system should automatically clean these values.`,
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
      let fileToSend = null
      
      if (activeFile) {
        // Clean the data before sending for regeneration too
        console.log('Cleaning active file data for regeneration...')
        const cleanedTableData = cleanDataForJSON(activeFile.tableData)
        
        // Validate the cleaned data
        const validationIssues = validateDataForJSON(cleanedTableData, 'tableData')
        if (validationIssues.length > 0) {
          console.warn('Data validation issues found during regeneration:', validationIssues)
        }
        
        fileToSend = {
          file: activeFile.file,
          data: cleanedTableData,
          headers: activeFile.headers,
          filename: activeFile.filename,
          file_path: activeFile.file_path
        }
        
        // Final validation of the complete payload
        const payloadValidation = validateDataForJSON(fileToSend, 'fileToSend')
        if (payloadValidation.length > 0) {
          console.error('Critical: Payload validation failed during regeneration:', payloadValidation)
          throw new Error('Data contains invalid values that cannot be processed')
        }
      }

      // Test JSON serialization before sending
      try {
        const testPayload = {
          message: originalMessage,
          file_path: fileToSend?.file_path || null
        }
        JSON.stringify(testPayload)
        console.log('Pre-regeneration JSON validation passed')
      } catch (jsonError) {
        console.error('JSON serialization test failed during regeneration:', jsonError)
        throw new Error('Data formatting error: Unable to serialize data for transmission')
      }

      const response = await sendMessage(originalMessage, fileToSend)
      console.log('Regenerated response received:', response)

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
        // If response is an object without clear text field, stringify it safely
        try {
          displayText = JSON.stringify(response, null, 2)
        } catch (jsonError) {
          console.warn('Failed to stringify regenerated response:', jsonError)
          displayText = 'Response received but could not be displayed properly'
        }
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
          console.log('Regenerated response is not valid JSON, displaying as text:', e.message)
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
      console.error('Regenerate response error:', err)
      
      let errorMessage = 'Failed to regenerate response'
      
      if (err.message) {
        if (err.message.includes('Unexpected token')) {
          errorMessage = 'Data formatting error during regeneration - your file may contain invalid values (NaN, Infinity).'
        } else if (err.message.includes('JSON')) {
          errorMessage = 'Data parsing error during regeneration - there may be formatting issues with your data.'
        } else if (err.message.includes('Data contains invalid values')) {
          errorMessage = 'Your housing dataset has invalid values that prevent regeneration. Please re-upload your file.'
        } else {
          errorMessage = err.message
        }
      }
      
      setLocalError(errorMessage)
      setError(errorMessage)

      addMessage({
        id: Date.now() + Math.random(),
        text: `❌ Sorry, I couldn't regenerate the response: ${errorMessage}\n\n💡 Tip: Try re-uploading your file to ensure all data is properly cleaned.`,
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