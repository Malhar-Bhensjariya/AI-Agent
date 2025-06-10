import React from 'react'
import { useAppContext } from '../context/AppContext'
import Sidebar from '../components/layout/Sidebar'
import ChatBox from '../components/chat/ChatBox'
import TableView from '../components/table/TableView'

const HomePage = () => {
  const { isTableViewVisible } = useAppContext()

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content Area */}
      <div className="flex-1 flex">
        {/* Chat Area */}
        <div className={`${isTableViewVisible ? 'w-1/2' : 'w-full'} flex flex-col transition-all duration-300`}>
          <ChatBox />
        </div>
        
        {/* Table View - appears on the right when visible */}
        {isTableViewVisible && (
          <div className="w-1/2 border-l border-gray-300">
            <TableView />
          </div>
        )}
      </div>
    </div>
  )
}

export default HomePage