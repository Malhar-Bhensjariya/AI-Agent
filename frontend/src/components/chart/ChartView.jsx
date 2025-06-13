import React, { useRef, useEffect, useState } from 'react'
import * as Chart from 'chart.js'

// Register Chart.js components
Chart.Chart.register(
  Chart.CategoryScale,
  Chart.LinearScale,
  Chart.BarElement,
  Chart.LineElement,
  Chart.PointElement,
  Chart.ArcElement,
  Chart.Title,
  Chart.Tooltip,
  Chart.Legend,
  Chart.RadialLinearScale,
  Chart.PolarAreaController,
  Chart.DoughnutController,
  Chart.PieController,
  Chart.BarController,
  Chart.LineController,
  Chart.ScatterController,
  Chart.BubbleController,
  Chart.RadarController
)

const ChartView = ({ data, type = 'bar' }) => {
  const canvasRef = useRef(null)
  const chartRef = useRef(null)
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!data || !canvasRef.current) {
      setIsLoading(false)
      return
    }

    // Clean up previous chart
    if (chartRef.current) {
      chartRef.current.destroy()
      chartRef.current = null
    }

    try {
      setIsLoading(true)
      setError(null)

      const ctx = canvasRef.current.getContext('2d')
      
      let chartConfig = null
      
      // Handle different data formats from backend
      if (typeof data === 'string') {
        try {
          chartConfig = JSON.parse(data)
        } catch (parseError) {
          throw new Error('Invalid JSON format from backend')
        }
      } else if (data.config) {
        // Handle if data is wrapped in config property (from useAgentResponse)
        if (typeof data.config === 'string') {
          chartConfig = JSON.parse(data.config)
        } else {
          chartConfig = data.config
        }
      } else if (data.chartConfig) {
        // Handle if data is wrapped in chartConfig property
        if (typeof data.chartConfig === 'string') {
          chartConfig = JSON.parse(data.chartConfig)
        } else {
          chartConfig = data.chartConfig
        }
      } else if (data.labels && data.datasets) {
        // Handle raw Chart.js data format
        chartConfig = buildChartConfig(data, type)
      } else {
        // Assume data is already a chart config
        chartConfig = data
      }

      // Validate chart config structure
      if (!chartConfig || typeof chartConfig !== 'object') {
        throw new Error('Invalid chart configuration')
      }

      // Ensure we have required Chart.js structure
      if (!chartConfig.type) {
        chartConfig.type = type
      }

      // Handle tooltip callbacks that come as strings from Python
      if (chartConfig.options?.plugins?.tooltip?.callbacks) {
        const callbacks = chartConfig.options.plugins.tooltip.callbacks
        Object.keys(callbacks).forEach(key => {
          if (typeof callbacks[key] === 'string') {
            try {
              // Convert string function to actual function for pie chart tooltips
              const funcString = callbacks[key]
              if (funcString.includes('function(context)')) {
                callbacks[key] = new Function('context', funcString.replace(/^function\(context\)\s*\{?\s*return\s*/, '').replace(/;?\s*\}?$/, ''))
              } else {
                // Simple replacement for the pie chart tooltip format
                callbacks[key] = function(context) {
                  const total = context.dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = ((context.parsed / total) * 100).toFixed(1)
                  return context.label + ": " + context.parsed + " (" + percentage + "%)"
                }
              }
            } catch (e) {
              // If conversion fails, use default callback
              delete callbacks[key]
            }
          }
        })
      }

      // Enhance options with responsive settings
      chartConfig.options = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index',
          ...chartConfig.options?.interaction
        },
        plugins: {
          legend: {
            display: true,
            position: chartConfig.type === 'pie' || chartConfig.type === 'doughnut' ? 'right' : 'top',
            ...chartConfig.options?.plugins?.legend
          },
          tooltip: {
            enabled: true,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            borderColor: '#ffffff',
            borderWidth: 1,
            ...chartConfig.options?.plugins?.tooltip
          },
          ...chartConfig.options?.plugins
        },
        ...chartConfig.options
      }

      // Create the chart
      chartRef.current = new Chart.Chart(ctx, chartConfig)
      setIsLoading(false)
    } catch (err) {
      console.error('Chart rendering error:', err)
      setError(err.message || 'Failed to render chart')
      setIsLoading(false)
    }

    // Cleanup function
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy()
        chartRef.current = null
      }
    }
  }, [data, type])

  // Build Chart.js config from raw data (fallback)
  const buildChartConfig = (rawData, chartType) => {
    if (!rawData.labels || !rawData.datasets) {
      throw new Error('Invalid chart data format - missing labels or datasets')
    }

    const config = {
      type: chartType,
      data: {
        labels: rawData.labels,
        datasets: rawData.datasets.map((dataset, index) => ({
          label: dataset.label || `Dataset ${index + 1}`,
          data: dataset.data,
          backgroundColor: dataset.backgroundColor || getDefaultColors(chartType, index),
          borderColor: dataset.borderColor || getDefaultBorderColors(chartType, index),
          borderWidth: dataset.borderWidth || (chartType === 'line' ? 2 : 1),
          fill: dataset.fill !== undefined ? dataset.fill : (chartType === 'line' ? false : true),
          tension: dataset.tension || (chartType === 'line' ? 0.4 : 0),
          ...dataset
        }))
      },
      options: getDefaultOptions(chartType)
    }

    return config
  }

  // Get default colors for different chart types
  const getDefaultColors = (chartType, index) => {
    const colors = [
      'rgba(59, 130, 246, 0.6)',   // Blue
      'rgba(16, 185, 129, 0.6)',   // Green
      'rgba(245, 101, 101, 0.6)',  // Red
      'rgba(251, 191, 36, 0.6)',   // Yellow
      'rgba(139, 92, 246, 0.6)',   // Purple
      'rgba(236, 72, 153, 0.6)',   // Pink
      'rgba(6, 182, 212, 0.6)',    // Cyan
      'rgba(34, 197, 94, 0.6)'     // Emerald
    ]

    if (chartType === 'pie' || chartType === 'doughnut' || chartType === 'polarArea') {
      return colors
    }

    return colors[index % colors.length]
  }

  // Get default border colors
  const getDefaultBorderColors = (chartType, index) => {
    const colors = [
      'rgb(59, 130, 246)',   // Blue
      'rgb(16, 185, 129)',   // Green
      'rgb(245, 101, 101)',  // Red
      'rgb(251, 191, 36)',   // Yellow
      'rgb(139, 92, 246)',   // Purple
      'rgb(236, 72, 153)',   // Pink
      'rgb(6, 182, 212)',    // Cyan
      'rgb(34, 197, 94)'     // Emerald
    ]

    if (chartType === 'pie' || chartType === 'doughnut' || chartType === 'polarArea') {
      return colors
    }

    return colors[index % colors.length]
  }

  // Get default options for different chart types
  const getDefaultOptions = (chartType) => {
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false
    }

    switch (chartType) {
      case 'line':
        return {
          ...baseOptions,
          scales: {
            x: {
              display: true,
              title: {
                display: false
              }
            },
            y: {
              display: true,
              title: {
                display: false
              }
            }
          }
        }
      case 'bar':
        return {
          ...baseOptions,
          scales: {
            x: {
              display: true,
              title: {
                display: false
              }
            },
            y: {
              display: true,
              beginAtZero: true,
              title: {
                display: false
              }
            }
          }
        }
      case 'pie':
      case 'doughnut':
        return {
          ...baseOptions,
          plugins: {
            legend: {
              position: 'right'
            }
          }
        }
      case 'radar':
        return {
          ...baseOptions,
          scales: {
            r: {
              beginAtZero: true
            }
          }
        }
      default:
        return baseOptions
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="chart-container bg-gray-50 rounded-lg p-4">
        <div className="w-full h-64 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading chart...</span>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="chart-container bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="w-full h-64 flex flex-col items-center justify-center">
          <svg className="w-12 h-12 text-red-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <p className="text-red-600 text-center font-medium">
            Failed to render chart
          </p>
          <p className="text-red-500 text-sm text-center mt-1">
            {error}
          </p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-3 px-4 py-2 bg-red-100 text-red-700 rounded-md text-sm hover:bg-red-200 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  // No data state
  if (!data) {
    return (
      <div className="chart-container bg-gray-50 rounded-lg p-4">
        <div className="w-full h-64 flex items-center justify-center">
          <div className="text-center">
            <svg className="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p className="text-gray-500">No chart data available</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="chart-container bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
      {/* Chart Canvas */}
      <div className="relative" style={{ height: '400px' }}>
        <canvas ref={canvasRef} />
      </div>
    </div>
  )
}

export default ChartView