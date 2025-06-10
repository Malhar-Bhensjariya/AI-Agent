import React, { useState, useRef } from 'react'
import { useAppContext } from '../../context/AppContext'
import MessageBubble from './MessageBubble'
import { useAgentResponse } from '../../hooks/useAgentResponse'
import { useUploadTask } from '../../hooks/useUploadTask'

const ChatBox = () => {
  const { messages, currentChat, dispatch } = useAppContext()
  const [inputMessage, setInputMessage] = useState('')
  const [uploadedFile, setUploadedFile] = useState(null)
  const fileInputRef = useRef(null)
  
  const { sendMessage, isLoading } = useAgentResponse()
  const { uploadFile, isUploading } = useUploadTask()

  const handleSendMessage = async () => {
    if (!inputMessage.trim() && !uploadedFile) return

    const newMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toISOString(),
      file: uploadedFile
    }

    dispatch({ type: 'ADD_MESSAGE', payload: newMessage })
    
    // Send to agent
    await sendMessage(inputMessage, uploadedFile)
    
    // Clear input
    setInputMessage('')
    setUploadedFile(null)
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (file) {
      const uploadedFileData = await uploadFile(file)
      setUploadedFile(uploadedFileData)
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

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-800">
          {currentChat?.title || 'New Chat'}
        </h2>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <svg className="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p>Start a conversation by typing a message or uploading a file</p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        {/* File Upload Preview */}
        {uploadedFile && (
          <div className="mb-3 p-2 bg-blue-50 border border-blue-200 rounded-lg flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="text-sm text-blue-800">{uploadedFile.name}</span>
            </div>
            <button
              onClick={removeFile}
              className="text-blue-600 hover:text-blue-800"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Input Bar */}
        <div className="flex items-end space-x-2">
          {/* File Upload Button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition duration-200"
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
            accept=".csv,.xlsx,.xls,.json,.txt"
          />

          {/* Message Input */}
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="1"
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
          </div>

          {/* Send Button */}
          <button
            onClick={handleSendMessage}
            disabled={(!inputMessage.trim() && !uploadedFile) || isLoading}
            className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition duration-200"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatBox