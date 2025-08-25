import React, { useState, useEffect } from 'react'
import { Bar } from 'react-chartjs-2'  // Import the chart type you need
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const ChartView = ({ data, type = 'bar' }) => {
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!data) {
      setIsLoading(false)
      return
    }

    setIsLoading(false)
  }, [data])

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
          <p className="text-red-600 text-center font-medium">Failed to render chart</p>
          <p className="text-red-500 text-sm text-center mt-1">{error}</p>
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

  // Define chart config
  const chartConfig = {
    type: type, // For example 'bar' or 'line'
    data: {
      labels: data.labels || [],
      datasets: data.datasets.map(dataset => ({
        ...dataset,
        backgroundColor: dataset.backgroundColor || 'rgba(59, 130, 246, 0.6)',
        borderColor: dataset.borderColor || 'rgb(59, 130, 246)',
        borderWidth: dataset.borderWidth || 1
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        title: {
          display: true,
          text: data.title || 'Chart Title'
        }
      },
      scales: {
        x: {
          display: true,
        },
        y: {
          display: true,
          beginAtZero: true
        }
      }
    }
  }

  // Return chart component
  return (
    <div className="chart-container bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
      <div style={{ height: '400px' }}>
        <Bar data={chartConfig.data} options={chartConfig.options} />
      </div>

      {/* Debug info */}
      <div className="mt-2 p-2 bg-gray-100 rounded text-xs text-gray-600 space-y-1">
        <div>Chart type: {data?.type || type}</div>
        <div>Labels: {data?.labels?.length || 'N/A'}</div>
        <div>Datasets: {data?.datasets?.length || 'N/A'}</div>
      </div>
    </div>
  )
}

export default ChartView
