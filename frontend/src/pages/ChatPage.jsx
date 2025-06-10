import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { Sidebar } from '../components/Sidebar'
import axios from 'axios'

export function ChatPage({ darkMode }) {
  const [messages, setMessages] = useState([
    {
      text: "Hello! I'm DARA, your AI research assistant. How can I help?",
      isUser: false,
      type: 'system'
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [file, setFile] = useState(null)
  const [currentFile, setCurrentFile] = useState(() => {
    const saved = localStorage.getItem('daraFile')
    return saved ? JSON.parse(saved) : null
  })
  const fileInputRef = useRef(null)
  const messagesEndRef = useRef(null)
  const API_URL = 'http://localhost:5000'

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (currentFile) {
      localStorage.setItem('daraFile', JSON.stringify(currentFile))
    }
  }, [currentFile])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() && !file) return

    const userMessage = {
      text: input,
      isUser: true,
      ...(file && { file: { name: file.name, size: file.size } })
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      let filename = currentFile?.filename

      if (file) {
        const formData = new FormData()
        formData.append('file', file)

        const uploadRes = await axios.post(`${API_URL}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        filename = uploadRes.data.filename
        setCurrentFile({
          filename,
          originalName: file.name,
          uploadedAt: new Date().toISOString()
        })
      }

      const payload = {
        question: input,
        ...(filename && { filename })
      }

      const analyzeRes = await axios.post(`${API_URL}/analyze`, payload)
      
      const botResponse = {
        ...analyzeRes.data,
        isUser: false,
        timestamp: Date.now()
      }

      setMessages(prev => [...prev, botResponse])
    } catch (err) {
      const errorMessage = {
        text: err.response?.data?.message || 'Analysis failed. Please try again.',
        isUser: false,
        type: 'error',
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setFile(null)
      setIsLoading(false)
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (!selectedFile) return

    setFile(selectedFile)
    setInput(prev => prev || `Analyze ${selectedFile.name}`)
  }

  const clearCurrentFile = () => {
    setCurrentFile(null)
    localStorage.removeItem('daraFile')
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <Sidebar darkMode={darkMode} />

      <div className="flex-1 flex flex-col">
        <div className={`p-4 border-b ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">AI Research Analyst</h2>
            {currentFile && (
              <div className={`p-2 rounded-lg flex items-center ${darkMode ? 'bg-gray-700' : 'bg-blue-50'}`}>
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="truncate max-w-xs">{currentFile.originalName}</span>
                <button onClick={clearCurrentFile} className="ml-2 text-red-500 hover:text-red-700">
                  &times;
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.map((msg, i) => (
            <div key={i}>
              {msg.type === 'global_analysis' && (
                <div className="text-xs font-semibold mb-1 px-2 py-1 w-fit rounded-full bg-purple-100 text-purple-800 dark:bg-purple-700 dark:text-white">
                  Global Analysis
                </div>
              )}

              <div className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-3xl rounded-xl p-4 whitespace-pre-wrap ${msg.isUser ? 'bg-blue-500 text-white rounded-br-none' : darkMode ? 'bg-gray-700 text-white rounded-bl-none' : 'bg-gray-100 text-black rounded-bl-none'}`}>
                  <ReactMarkdown>
                    {msg.text || msg.content}
                  </ReactMarkdown>

                  {msg.plot_url && (
                    <div className="mt-4">
                      <img 
                        src={`${API_URL}${msg.plot_url}`}
                        alt="Data visualization"
                        className="rounded-lg border dark:border-gray-600 max-w-full h-auto"
                      />
                      <div className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                        {msg.caption}
                        <button 
                          onClick={() => navigator.clipboard.writeText(msg.code)}
                          className="ml-2 text-blue-500 hover:text-blue-700"
                        >
                          Copy Code
                        </button>
                      </div>
                    </div>
                  )}

                  {msg.sources && (
                    <div className="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600 text-xs text-gray-600 dark:text-gray-300">
                      <strong>Sources:</strong> {msg.sources.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className={`p-4 rounded-xl ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} rounded-bl-none`}>
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

            <input type="file" ref={fileInputRef} onChange={handleFileChange} accept=".csv,.xlsx,.xls" className="hidden" />

            <div className="flex-1 relative">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask anything or upload data for analysis..."
                className={`w-full p-4 pr-16 rounded-xl ${darkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'} border focus:outline-none focus:ring-2 focus:ring-blue-500`}
              />
              {file && (
                <span className="absolute right-16 top-1/2 transform -translate-y-1/2 text-xs px-2 py-1 rounded-full bg-blue-500 text-white">
                  New File
                </span>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading || (!input.trim() && !file)}
              className={`p-4 rounded-xl ${isLoading || (!input.trim() && !file) ? 'bg-gray-300 dark:bg-gray-600 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'} text-white transition-colors`}
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