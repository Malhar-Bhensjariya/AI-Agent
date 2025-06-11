import React, { useState, useRef, useEffect } from 'react'
import { useAppContext } from '../../context/AppContext'
import MessageBubble from './MessageBubble'
import { useAgentResponse } from '../../hooks/useAgentResponse'
import { useUploadTask } from '../../hooks/useUploadTask'

const ChatBox = () => {
  const { messages, currentChat, loading, error,addMessage, clearMessages, clearCurrentFile } = useAppContext()
  const [inputMessage, setInputMessage] = useState('')
  const [uploadedFile, setUploadedFile] = useState(null)
  const fileInputRef = useRef(null)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)
  
  const { sendMessage, isLoading: agentLoading, error: agentError } = useAgentResponse()
  const { uploadFile, isUploading, uploadProgress, error: uploadError } = useUploadTask()

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }, [inputMessage])

  const handleSendMessage = async () => {
    if ((!inputMessage.trim() && !uploadedFile) || agentLoading) return

    const messageText = inputMessage.trim()
    const fileToSend = uploadedFile

    // Create user message
    const newMessage = {
      id: Date.now() + Math.random(),
      text: messageText,
      sender: 'user',
      timestamp: new Date().toISOString(),
      file: fileToSend
    }

    // Add user message to chat
    addMessage(newMessage)
    
    // Clear input immediately for better UX
    setInputMessage('')
    setUploadedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }

    try {
      // Send to agent with file path if available
      await sendMessage(messageText, fileToSend?.path)
    } catch (error) {
      console.error('Failed to send message:', error)
      // Error handling is done in useAgentResponse hook
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    try {
      const uploadedFileData = await uploadFile(file)
      setUploadedFile(uploadedFileData)
    } catch (error) {
      console.error('File upload failed:', error)
      // Error is handled in useUploadTask hook
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const removeFile = () => {
    setUploadedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const clearChat = () => {
    clearMessages()
    clearCurrentFile()
    setUploadedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const isProcessing = agentLoading || isUploading || loading

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-800">
              {currentChat?.title || 'Data Analysis Chat'}
            </h2>
            <p className="text-sm text-gray-500">
              {messages.length} message{messages.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
        
        {/* Clear Chat Button */}
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
            title="Clear chat"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        )}
      </div>

      {/* Error Banner */}
      {(error || agentError || uploadError) && (
        <div className="mx-4 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p className="text-red-800 text-sm">
              {error || agentError || uploadError}
            </p>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Welcome to Data Analysis Chat
              </h3>
              <p className="text-gray-600 mb-4">
                Upload your data files (CSV, Excel, JSON) and ask questions about your data. 
                I can help you analyze, visualize, and understand your data better.
              </p>
              <div className="flex flex-wrap justify-center gap-2 text-sm text-gray-500">
                <span className="px-2 py-1 bg-gray-100 rounded-full">📊 Data Analysis</span>
                <span className="px-2 py-1 bg-gray-100 rounded-full">📈 Visualizations</span>
                <span className="px-2 py-1 bg-gray-100 rounded-full">🔍 Insights</span>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
        
        {/* Loading indicator */}
        {agentLoading && (
          <div className="flex justify-start">
            <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
              <span className="text-sm text-gray-600">Analyzing...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white">
        {/* File Upload Preview */}
        {uploadedFile && (
          <div className="mx-4 mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-blue-800">{uploadedFile.name}</p>
                  <p className="text-xs text-blue-600">
                    {uploadedFile.size ? `${Math.round(uploadedFile.size / 1024)} KB` : 'Ready to analyze'}
                  </p>
                </div>
              </div>
              <button
                onClick={removeFile}
                className="text-blue-600 hover:text-blue-800 p-1 rounded-md hover:bg-blue-100 transition-colors"
                title="Remove file"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Upload Progress */}
        {isUploading && (
          <div className="mx-4 mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-700">Uploading file...</p>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
              <span className="text-sm text-gray-500">{uploadProgress}%</span>
            </div>
          </div>
        )}

        {/* Input Bar */}
        <div className="p-4">
          <div className="flex items-end space-x-3">
            {/* File Upload Button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="flex-shrink-0 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
              title="Upload file"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            </button>
            
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
              accept=".csv,.xlsx,.xls,.json,.txt,.pdf,.tsv"
            />

            {/* Message Input */}
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder={uploadedFile ? "Ask a question about your data..." : "Type your message or upload a file..."}
                className="w-full p-3 pr-12 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="1"
                style={{ minHeight: '44px', maxHeight: '120px' }}
                disabled={isProcessing}
              />
              
              {/* Character count for long messages */}
              {inputMessage.length > 100 && (
                <div className="absolute bottom-1 right-12 text-xs text-gray-400">
                  {inputMessage.length}
                </div>
              )}
            </div>

            {/* Send Button */}
            <button
              onClick={handleSendMessage}
              disabled={(!inputMessage.trim() && !uploadedFile) || isProcessing}
              className="flex-shrink-0 p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              title="Send message"
            >
              {isProcessing ? (
                <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatBox