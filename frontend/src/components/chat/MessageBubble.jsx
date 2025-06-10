import React from 'react'
import ChartView from '../chart/ChartView'

const MessageBubble = ({ message }) => {
  const isUser = message.sender === 'user'
  const isAgent = message.sender === 'agent'

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar */}
        <div className={`flex items-end space-x-2 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
            isUser ? 'bg-blue-600' : 'bg-gray-600'
          }`}>
            {isUser ? 'U' : 'AI'}
          </div>
          
          <div className={`rounded-2xl px-4 py-2 ${
            isUser 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {/* File attachment preview */}
            {message.file && (
              <div className={`mb-2 p-2 rounded-lg ${
                isUser ? 'bg-blue-500' : 'bg-gray-200'
              }`}>
                <div className="flex items-center space-x-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="text-sm">{message.file.name}</span>
                </div>
              </div>
            )}
            
            {/* Message text */}
            {message.text && (
              <div className="whitespace-pre-wrap">
                {message.text}
              </div>
            )}
            
            {/* Chart/Plot rendering for agent messages */}
            {isAgent && message.chartData && (
              <div className="mt-3">
                <ChartView data={message.chartData} />
              </div>
            )}
          </div>
        </div>
        
        {/* Timestamp */}
        <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  )
}

export default MessageBubble