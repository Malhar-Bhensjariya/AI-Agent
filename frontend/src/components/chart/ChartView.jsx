import React, { useState, useEffect } from 'react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'

const ChartView = ({ data, type = 'bar' }) => {
  const [chartData, setChartData] = useState(null)
  const [chartConfig, setChartConfig] = useState(null)
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  // Default color palette
  const colors = [
    '#3B82F6', // Blue
    '#10B981', // Green
    '#F56565', // Red
    '#FBBF24', // Yellow
    '#8B5CF6', // Purple
    '#EC4899', // Pink
    '#06B6D4', // Cyan
    '#22C55E'  // Emerald
  ]

  useEffect(() => {
    if (!data) {
      setIsLoading(false)
      return
    }

    try {
      setIsLoading(true)
      setError(null)

      console.log('ChartView received data:', data)
      console.log('ChartView data type:', typeof data)

      let parsedData = null
      let config = null

      // Handle different data formats
      if (typeof data === 'string') {
        try {
          parsedData = JSON.parse(data)
        } catch (parseError) {
          throw new Error('Invalid JSON format from backend')
        }
      } else if (data.config) {
        console.log('Using data.config:', data.config)
        if (typeof data.config === 'string') {
          parsedData = JSON.parse(data.config)
        } else {
          parsedData = data.config
        }
      } else if (data.chartConfig) {
        if (typeof data.chartConfig === 'string') {
          parsedData = JSON.parse(data.chartConfig)
        } else {
          parsedData = data.chartConfig
        }
      } else {
        parsedData = data
      }

      if (!parsedData || typeof parsedData !== 'object') {
        throw new Error('Invalid chart configuration')
      }

      // Convert Chart.js format to Recharts format
      const convertedData = convertToRechartsFormat(parsedData, type)
      setChartData(convertedData.data)
      setChartConfig(convertedData.config)
      setIsLoading(false)

    } catch (err) {
      console.error('Chart processing error:', err)
      setError(err.message || 'Failed to process chart data')
      setIsLoading(false)
    }
  }, [data, type])

  const convertToRechartsFormat = (inputData, chartType) => {
    // If it's already in Recharts format (array of objects)
    if (Array.isArray(inputData)) {
      return {
        data: inputData,
        config: { type: chartType, datasets: [] }
      }
    }

    // Handle Chart.js format
    if (inputData.data && inputData.data.labels && inputData.data.datasets) {
      const { labels, datasets } = inputData.data
      const convertedType = inputData.type || chartType

      if (convertedType === 'pie' || convertedType === 'doughnut') {
        // For pie charts, convert to array of objects with name and value
        const pieData = labels.map((label, index) => ({
          name: label,
          value: datasets[0]?.data[index] || 0
        }))
        return {
          data: pieData,
          config: {
            type: convertedType,
            datasets: datasets
          }
        }
      } else if (convertedType === 'radar') {
        // For radar charts, convert to array of objects
        const radarData = labels.map((label, index) => {
          const item = { subject: label }
          datasets.forEach((dataset, datasetIndex) => {
            item[dataset.label || `Dataset ${datasetIndex + 1}`] = dataset.data[index] || 0
          })
          return item
        })
        return {
          data: radarData,
          config: {
            type: convertedType,
            datasets: datasets
          }
        }
      } else {
        // For bar/line charts, convert to array of objects
        const chartData = labels.map((label, index) => {
          const item = { name: label }
          datasets.forEach((dataset, datasetIndex) => {
            item[dataset.label || `Dataset ${datasetIndex + 1}`] = dataset.data[index] || 0
          })
          return item
        })
        return {
          data: chartData,
          config: {
            type: convertedType,
            datasets: datasets
          }
        }
      }
    }

    // If it's raw data with labels and datasets at root level
    if (inputData.labels && inputData.datasets) {
      return convertToRechartsFormat({ data: inputData }, chartType)
    }

    // Default fallback
    return {
      data: [],
      config: { type: chartType, datasets: [] }
    }
  }

  const renderChart = () => {
    if (!chartData || chartData.length === 0) {
      return (
        <div className="w-full h-64 flex items-center justify-center">
          <div className="text-center">
            <svg className="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p className="text-gray-500">No chart data available</p>
          </div>
        </div>
      )
    }

    const chartType = chartConfig?.type || type

    switch (chartType) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              {chartConfig?.datasets?.map((dataset, index) => (
                <Bar
                  key={index}
                  dataKey={dataset.label || `Dataset ${index + 1}`}
                  fill={dataset.backgroundColor || colors[index % colors.length]}
                />
              )) || <Bar dataKey="value" fill={colors[0]} />}
            </BarChart>
          </ResponsiveContainer>
        )

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              {chartConfig?.datasets?.map((dataset, index) => (
                <Line
                  key={index}
                  type="monotone"
                  dataKey={dataset.label || `Dataset ${index + 1}`}
                  stroke={dataset.borderColor || colors[index % colors.length]}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              )) || <Line type="monotone" dataKey="value" stroke={colors[0]} strokeWidth={2} />}
            </LineChart>
          </ResponsiveContainer>
        )

      case 'pie':
      case 'doughnut':
        const CustomTooltip = ({ active, payload }) => {
          if (active && payload && payload.length) {
            const data = payload[0]
            const total = chartData.reduce((sum, item) => sum + item.value, 0)
            const percentage = ((data.value / total) * 100).toFixed(1)
            return (
              <div className="bg-gray-800 text-white p-2 rounded shadow-lg">
                <p>{`${data.payload.name}: ${data.value} (${percentage}%)`}</p>
              </div>
            )
          }
          return null
        }

        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={chartType === 'doughnut' ? 60 : 0}
                outerRadius={120}
                paddingAngle={2}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )

      case 'radar':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={chartData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="subject" />
              <PolarRadiusAxis />
              <Tooltip />
              <Legend />
              {chartConfig?.datasets?.map((dataset, index) => (
                <Radar
                  key={index}
                  name={dataset.label || `Dataset ${index + 1}`}
                  dataKey={dataset.label || `Dataset ${index + 1}`}
                  stroke={colors[index % colors.length]}
                  fill={colors[index % colors.length]}
                  fillOpacity={0.3}
                />
              ))}
            </RadarChart>
          </ResponsiveContainer>
        )

      default:
        return (
          <div className="w-full h-64 flex items-center justify-center">
            <p className="text-gray-500">Unsupported chart type: {chartType}</p>
          </div>
        )
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

  return (
    <div className="chart-container bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
      {renderChart()}
    </div>
  )
}

export default ChartView