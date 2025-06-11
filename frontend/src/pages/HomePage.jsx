import React from 'react'
import { useAppContext } from '../context/AppContext'
import Sidebar from '../components/layout/Sidebar'
import ChatBox from '../components/chat/ChatBox'
import TableView from '../components/table/TableView'

const HomePage = () => {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content Area - Always split between chat and table */}
      <div className="flex-1 flex">
        {/* Chat Area - Always takes half the width */}
        <div className="w-1/2 flex flex-col">
          <ChatBox />
        </div>
        
        {/* Table View - Always visible, takes other half */}
        <div className="w-1/2">
          <TableView />
        </div>
      </div>
    </div>
  )
}

export default HomePage