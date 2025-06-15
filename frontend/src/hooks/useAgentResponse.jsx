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
          displayText = formatAnalysisResult(analysisResult)
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

  // Format analysis results for better display
  const formatAnalysisResult = (result) => {
    if (!result || typeof result !== 'object') {
      return JSON.stringify(result, null, 2)
    }

    let formatted = []

    // Handle error responses
    if (result.error) {
      return `❌ Error: ${result.error}`
    }

    // Add main message
    if (result.message) {
      formatted.push(`📊 ${result.message}\n`)
    }

    // Handle missing columns analysis
    if (result.missing_columns) {
      if (Object.keys(result.missing_columns).length === 0) {
        formatted.push('✅ No missing values found')
      } else {
        formatted.push('📋 Missing Values:')
        Object.entries(result.missing_columns).forEach(([col, count]) => {
          formatted.push(`  • ${col}: ${count} missing values`)
        })
        if (result.total_missing) {
          formatted.push(`  Total: ${result.total_missing} missing values\n`)
        }
      }
    }

    // Handle column averages
    if (result.column_averages) {
      formatted.push('📈 Column Averages:')
      Object.entries(result.column_averages).forEach(([col, avg]) => {
        formatted.push(`  • ${col}: ${avg !== null ? avg.toFixed(4) : 'N/A'}`)
      })
      if (result.non_numeric_columns?.length > 0) {
        formatted.push(`\n⚠️ Skipped non-numeric columns: ${result.non_numeric_columns.join(', ')}`)
      }
    }

    // Handle statistical summary
    if (result.statistical_summary) {
      formatted.push('📊 Statistical Summary:')
      Object.entries(result.statistical_summary).forEach(([col, stats]) => {
        formatted.push(`\n📋 ${col}:`)
        formatted.push(`  Count: ${stats.count}`)
        formatted.push(`  Mean: ${stats.mean}`)
        formatted.push(`  Median: ${stats.median}`)
        formatted.push(`  Std Dev: ${stats.std}`)
        formatted.push(`  Min: ${stats.min} | Max: ${stats.max}`)
        if (stats.missing_values > 0) {
          formatted.push(`  Missing: ${stats.missing_values}`)
        }
      })
    }

    // Handle deep analysis
    if (result.deep_analysis) {
      formatted.push('🔍 Deep Statistical Analysis:')
      Object.entries(result.deep_analysis).forEach(([col, stats]) => {
        formatted.push(`\n📋 ${col}:`)
        formatted.push(`  Count: ${stats.count} | Missing: ${stats.missing_values}`)
        formatted.push(`  Mean: ${stats.mean} | Median: ${stats.median}`)
        formatted.push(`  Q1: ${stats.Q1} | Q3: ${stats.Q3} | IQR: ${stats.IQR}`)
        formatted.push(`  Min: ${stats.min} | Max: ${stats.max}`)
        formatted.push(`  Std Dev: ${stats.std}`)
        formatted.push(`  Skewness: ${stats.skewness} | Kurtosis: ${stats.kurtosis}`)
      })
      
      if (result.interpretation) {
        formatted.push('\n💡 Interpretation:')
        Object.entries(result.interpretation).forEach(([key, desc]) => {
          formatted.push(`  ${key}: ${desc}`)
        })
      }
    }

    // Handle outliers
    if (result.outlier_details) {
      if (Object.keys(result.outlier_details).length === 0) {
        formatted.push(`✅ No outliers detected (threshold: ${result.threshold_used})`)
      } else {
        formatted.push(`🚨 Outliers Detected (Z-score > ${result.threshold_used}):`)
        formatted.push(`Total outliers: ${result.total_outliers} across ${result.columns_with_outliers} columns\n`)
        
        Object.entries(result.outlier_details).forEach(([col, details]) => {
          formatted.push(`📋 ${col}:`)
          formatted.push(`  Count: ${details.outlier_count} (${details.percentage}%)`)
          formatted.push(`  Rows: ${details.outlier_rows.slice(0, 5).join(', ')}${details.outlier_rows.length > 5 ? '...' : ''}`)
          formatted.push(`  Values: ${details.outlier_values.slice(0, 5).join(', ')}${details.outlier_values.length > 5 ? '...' : ''}`)
        })
      }
    }

    // Handle column information
    if (result.all_columns) {
      formatted.push(`📋 Dataset Structure (${result.total_columns} columns):`)
      
      if (result.column_types) {
        Object.entries(result.column_types).forEach(([type, info]) => {
          if (info.count > 0) {
            formatted.push(`\n${getTypeEmoji(type)} ${type.charAt(0).toUpperCase() + type.slice(1)} (${info.count}):`)
            formatted.push(`  ${info.columns.join(', ')}`)
          }
        })
      }
    }

    // Handle frequency analysis
    if (result.frequencies || result.top_20_frequencies) {
      const freqs = result.frequencies || result.top_20_frequencies
      formatted.push(`📊 Frequency Analysis for "${result.column}":`)
      formatted.push(`Total unique values: ${result.total_unique_values}`)
      formatted.push(`Non-missing values: ${result.total_non_missing}`)
      if (result.missing_values > 0) {
        formatted.push(`Missing values: ${result.missing_values}`)
      }
      
      formatted.push('\nTop frequencies:')
      Object.entries(freqs).slice(0, 10).forEach(([value, count]) => {
        const percentage = result.percentages?.[value] || result.top_20_percentages?.[value] || 0
        formatted.push(`  • ${value}: ${count} (${percentage}%)`)
      })
      
      if (result.truncated) {
        formatted.push('  ... (showing top 10 of 20)')
      }
    }

    // Handle duplicate analysis
    if (result.hasOwnProperty('duplicate_rows')) {
      if (result.duplicate_rows === 0) {
        formatted.push('✅ No duplicate rows found')
      } else {
        formatted.push(`🔄 Duplicate Analysis:`)
        formatted.push(`Total rows: ${result.total_rows}`)
        formatted.push(`Duplicate rows: ${result.duplicate_rows} (${result.duplication_percentage}%)`)
        formatted.push(`Unique rows: ${result.unique_rows}`)
        
        if (result.sample_duplicates?.length > 0) {
          formatted.push('\nSample duplicates:')
          result.sample_duplicates.forEach((dup, idx) => {
            formatted.push(`  ${idx + 1}. ${JSON.stringify(dup)}`)
          })
        }
      }
    }

    // Handle comprehensive data description
    if (result.dataset_overview) {
      const overview = result.dataset_overview
      formatted.push('📊 Dataset Overview:')
      formatted.push(`  Dimensions: ${overview.total_rows} rows × ${overview.total_columns} columns`)
      formatted.push(`  Memory usage: ${overview.memory_usage_mb} MB`)
      
      if (result.missing_data_summary) {
        const missing = result.missing_data_summary
        formatted.push(`\n🔍 Missing Data:`)
        formatted.push(`  Total missing: ${missing.total_missing_values} (${missing.missing_percentage}%)`)
        formatted.push(`  Columns with missing: ${missing.columns_with_missing}`)
      }
      
      if (result.column_types) {
        formatted.push(`\n📋 Column Types:`)
        Object.entries(result.column_types).forEach(([type, count]) => {
          formatted.push(`  ${type}: ${count}`)
        })
      }
    }

    return formatted.length > 0 ? formatted.join('\n') : JSON.stringify(result, null, 2)
  }

  const getTypeEmoji = (type) => {
    const emojis = {
      numeric: '🔢',
      text: '📝',
      datetime: '📅',
      boolean: '✅'
    }
    return emojis[type] || '📋'
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
          displayText = formatAnalysisResult(analysisResult)
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