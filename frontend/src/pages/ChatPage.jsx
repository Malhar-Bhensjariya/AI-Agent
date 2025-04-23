import { useState, useRef, useEffect } from 'react'
import { Sidebar } from '../components/Sidebar'

export function ChatPage({ darkMode }) {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm DARA, your research assistant. How can I help?", isUser: false }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [file, setFile] = useState(null)
  const fileInputRef = useRef(null)
  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() && !file) return
    
    // Add user message
    const userMessage = { text: input, isUser: true }
    if (file) {
      userMessage.file = { name: file.name, size: file.size }
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setFile(null)
    setIsLoading(true)

    // Simulate API call
    setTimeout(() => {
      const botResponse = {
        text: file 
          ? `I've analyzed ${file.name}. It contains sales data for Q3 2023 with 1,240 records. Key insights: Revenue increased by 12% quarter-over-quarter.`
          : "I can help analyze that. For detailed insights, please upload your data file.",
        isUser: false
      }
      setMessages(prev => [...prev, botResponse])
      setIsLoading(false)
    }, 1500)
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setInput(prev => prev ? prev : `Analyze ${selectedFile.name}`)
    }
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <Sidebar darkMode={darkMode} />
      
      <div className="flex-1 flex flex-col">
        {/* Chat header */}
        <div className={`p-4 border-b ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <h2 className="text-xl font-semibold">Data Analysis</h2>
          {file && (
            <div className={`mt-2 p-2 rounded-lg flex items-center ${darkMode ? 'bg-gray-700' : 'bg-blue-50'}`}>
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="truncate">{file.name}</span>
              <span className="text-xs ml-auto">{Math.round(file.size / 1024)} KB</span>
              <button 
                onClick={() => setFile(null)}
                className="ml-2 text-gray-500 hover:text-gray-700"
              >
                &times;
              </button>
            </div>
          )}
        </div>

        {/* Messages container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div 
              key={i} 
              className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-3xl rounded-xl p-4 ${
                  msg.isUser 
                    ? 'bg-blue-500 text-white rounded-br-none' 
                    : darkMode 
                      ? 'bg-gray-700 rounded-bl-none' 
                      : 'bg-gray-100 rounded-bl-none'
                }`}
              >
                {msg.text}
                {msg.file && (
                  <div className={`mt-2 p-2 rounded-lg flex items-center ${
                    darkMode ? 'bg-gray-800' : 'bg-blue-100'
                  }`}>
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span className="text-sm truncate">{msg.file.name}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className={`p-4 rounded-xl ${
                darkMode ? 'bg-gray-700' : 'bg-gray-100'
              } rounded-bl-none`}>
                <div className="flex space-x-2">
                  <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce"></div>
                  <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <form onSubmit={handleSubmit} className={`p-4 border-t ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <div className="flex items-end gap-2">
            <button
              type="button"
              onClick={() => fileInputRef.current.click()}
              className={`p-2 rounded-lg ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".csv,.xlsx,.xls"
              className="hidden"
            />
            
            <div className="flex-1 relative">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask DARA anything or upload data..."
                className={`w-full p-4 pr-16 rounded-xl ${
                  darkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
                } border focus:outline-none focus:ring-2 focus:ring-blue-500`}
              />
              {file && (
                <span className="absolute right-16 top-1/2 transform -translate-y-1/2 text-xs px-2 py-1 rounded-full bg-blue-500 text-white">
                  File
                </span>
              )}
            </div>
            
            <button
              type="submit"
              disabled={isLoading || (!input.trim() && !file)}
              className={`p-4 rounded-xl ${
                isLoading || (!input.trim() && !file)
                  ? 'bg-gray-300 dark:bg-gray-600 cursor-not-allowed'
                  : 'bg-blue-500 hover:bg-blue-600'
              } text-white transition-colors`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}