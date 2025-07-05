import React from 'react'
import { useAppContext } from '../context/AppContext'
import Sidebar from '../components/layout/Sidebar'
import ChatBox from '../components/chat/ChatBox'
import TableView from '../components/table/TableView'

const HomePage = () => {
  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content Area - Always split between chat and table */}
      <div className="flex-1 flex min-w-0">
        {/* Chat Area - Always takes half the width */}
        <div className="w-1/2 flex flex-col border-r border-gray-200">
          <ChatBox />
        </div>
        
        {/* Table View - Always visible, takes other half */}
        <div className="w-1/2 flex flex-col">
          <TableView />
        </div>
      </div>
    </div>
  )
}

export default HomePage