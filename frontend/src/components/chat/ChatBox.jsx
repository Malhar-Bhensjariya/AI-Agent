import React, { useState, useRef, useEffect } from 'react'
import { useAppContext } from '../../context/AppContext'
import MessageBubble from './MessageBubble'
import { useAgentResponse } from '../../hooks/useAgentResponse'
import { useUploadTask } from '../../hooks/useUploadTask'
import { 
  MessageCircle, 
  Trash2, 
  AlertTriangle, 
  BarChart3, 
  TrendingUp, 
  Search, 
  FileText, 
  Paperclip, 
  X, 
  RefreshCw, 
  ArrowUp, 
  Loader2 
} from 'lucide-react'

const ChatBox = () => {
  const { messages, currentChat, loading, error, addMessage, clearMessages, clearCurrentFile, setCurrentFile } = useAppContext()
  const [inputMessage, setInputMessage] = useState('')
  const [uploadedFile, setUploadedFile] = useState(null)
  const [isParsingFile, setIsParsingFile] = useState(false)
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
    const messageText = inputMessage.trim()

    // Allow sending if either message or file exists
    if (!messageText || agentLoading) return

    // Create user message - handle file-only uploads
    // Create user message
    const newMessage = {
      id: Date.now() + Math.random(),
      text: messageText,
      sender: 'user',
      timestamp: new Date().toISOString()
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
      // Send message - useAgentResponse will handle active file automatically
      await sendMessage(messageText)      
    } catch (error) {
      console.error('Failed to send message:', error)
      // Error handling is done in useAgentResponse hook
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    try {
      // Use the upload hook which now handles local parsing
      const fileInfo = await uploadFile(file)
      
      // Auto-send analysis message
      addMessage({
        id: Date.now() + Math.random(),
        text: `Loaded ${file.name} with ${fileInfo.tableData.length} rows`,
        sender: 'user',
        timestamp: new Date().toISOString(),
        fileLoaded: true
      })
      
      // Add agent confirmation
      addMessage({
        id: Date.now() + Math.random(),
        text: `Great! I've loaded your file "${file.name}" with ${fileInfo.tableData.length} rows and ${fileInfo.headers.length} columns. You can view the data in the table view, or ask me questions about it!`,
        sender: 'agent',
        timestamp: new Date().toISOString()
      })
      
    } catch (error) {
        console.error('File upload failed:', error)
        addMessage({
          id: Date.now() + Math.random(),
          text: `❌ Failed to upload file: ${error.message}`,
          sender: 'agent',
          timestamp: new Date().toISOString(),
          error: true
        })
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
  
  // Check if we can send (either message or file)
  const canSend = (inputMessage.trim() || uploadedFile) && !isProcessing

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <MessageCircle className="w-4 h-4 text-white" />
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
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Error Banner */}
      {(error || agentError || uploadError) && (
        <div className="mx-4 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-400 mr-2" />
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
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Welcome to Data Analysis Chat
              </h3>
              <p className="text-gray-600 mb-4">
                Upload your data files (CSV, Excel, JSON) and ask questions about your data. 
                I can help you analyze, visualize, and understand your data better.
              </p>
              <div className="flex flex-wrap justify-center gap-2 text-sm text-gray-500">
                <span className="px-2 py-1 bg-gray-100 rounded-full flex items-center gap-1">
                  <BarChart3 className="w-3 h-3" />
                  Data Analysis
                </span>
                <span className="px-2 py-1 bg-gray-100 rounded-full flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  Visualizations
                </span>
                <span className="px-2 py-1 bg-gray-100 rounded-full flex items-center gap-1">
                  <Search className="w-3 h-3" />
                  Insights
                </span>
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
                  <FileText className="w-4 h-4 text-blue-600" />
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
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Upload Progress */}
        {isUploading && (
          <div className="mx-4 mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
            <div className="flex items-center space-x-3">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
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
          <div className="flex items-center space-x-3">
            {/* File Upload Button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="flex-shrink-0 p-2.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
              title="Upload file"
            >
              <Paperclip className="w-5 h-5" />
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
                placeholder={uploadedFile ? "Ask a question about your data or just press send to analyze the file..." : "Type your message or upload a file..."}
                className="w-full p-3 pr-12 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent scrollbar-hide overflow-hidden"
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
              disabled={!canSend}
              className="flex-shrink-0 p-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              title="Send message"
            >
              {isProcessing ? (
                <RefreshCw className="w-5 h-5 animate-spin" />
              ) : (
                <ArrowUp className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatBox