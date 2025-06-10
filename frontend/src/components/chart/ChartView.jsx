import React from 'react'

const ChartView = ({ data, type = 'bar' }) => {
  // This is a placeholder component for charts
  // You would integrate with a charting library like Chart.js, Recharts, or D3.js
  
  if (!data) {
    return (
      <div className="w-full h-64 bg-gray-100 rounded-lg flex items-center justify-center">
        <p className="text-gray-500">No chart data available</p>
      </div>
    )
  }

  // Mock chart representation
  const renderMockChart = () => {
    switch (type) {
      case 'bar':
        return (
          <div className="w-full h-64 bg-gradient-to-t from-blue-200 to-blue-100 rounded-lg p-4 flex items-end justify-around space-x-2">
            {Array.from({ length: 5 }, (_, i) => (
              <div
                key={i}
                className="bg-blue-600 rounded-t flex-1"
                style={{ height: `${Math.random() * 80 + 20}%` }}
              />
            ))}
          </div>
        )
      case 'line':
        return (
          <div className="w-full h-64 bg-gradient-to-br from-green-100 to-green-50 rounded-lg p-4 flex items-center justify-center">
            <svg className="w-full h-full" viewBox="0 0 300 200">
              <polyline
                fill="none"
                stroke="#059669"
                strokeWidth="3"
                points="20,180 80,120 140,140 200,80 260,100"
              />
              {[20, 80, 140, 200, 260].map((x, i) => (
                <circle key={i} cx={x} cy={[180, 120, 140, 80, 100][i]} r="4" fill="#059669" />
              ))}
            </svg>
          </div>
        )
      case 'pie':
        return (
          <div className="w-full h-64 bg-gradient-to-br from-purple-100 to-purple-50 rounded-lg p-4 flex items-center justify-center">
            <svg className="w-40 h-40" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="40" fill="#8b5cf6" stroke="#fff" strokeWidth="2" strokeDasharray="75 25" strokeDashoffset="25" />
              <circle cx="50" cy="50" r="40" fill="#a78bfa" stroke="#fff" strokeWidth="2" strokeDasharray="25 75" strokeDashoffset="0" />
            </svg>
          </div>
        )
      default:
        return (
          <div className="w-full h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Chart type: {type}</p>
          </div>
        )
    }
  }

  return (
    <div className="chart-container">
      <div className="mb-2">
        <h4 className="text-sm font-medium text-gray-700">
          {data.title || 'Chart'}
        </h4>
      </div>
      {renderMockChart()}
      <div className="mt-2 text-xs text-gray-500">
        {data.description || 'Generated chart based on your data'}
      </div>
    </div>
  )
}

export default ChartView