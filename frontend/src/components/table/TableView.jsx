import React, { useState } from 'react'
import { useAppContext } from '../../context/AppContext'

const TableView = () => {
  const { dispatch } = useAppContext()
  const [tableData, setTableData] = useState([])
  const [headers, setHeaders] = useState([])
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)

  // Mock data - replace with actual data from context/API
  React.useEffect(() => {
    // This would normally come from your app context or API
    const mockHeaders = ['ID', 'Name', 'Value', 'Category', 'Date']
    const mockData = Array.from({ length: 50 }, (_, i) => ({
      id: i + 1,
      name: `Item ${i + 1}`,
      value: Math.floor(Math.random() * 1000),
      category: ['A', 'B', 'C'][Math.floor(Math.random() * 3)],
      date: new Date(2024, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1).toLocaleDateString()
    }))
    
    setHeaders(mockHeaders)
    setTableData(mockData)
  }, [])

  const closeTableView = () => {
    dispatch({ type: 'SET_TABLE_VIEW', payload: false })
  }

  // Pagination logic
  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = tableData.slice(indexOfFirstItem, indexOfLastItem)
  const totalPages = Math.ceil(tableData.length / itemsPerPage)

  const goToPage = (pageNumber) => {
    setCurrentPage(pageNumber)
  }

  return (
    <div className="h-full bg-white flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800">Data Table</h3>
        <button
          onClick={closeTableView}
          className="text-gray-500 hover:text-gray-700 p-1 rounded"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              {headers.map((header, index) => (
                <th
                  key={index}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200"
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {currentItems.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                {Object.values(row).map((cell, cellIndex) => (
                  <td
                    key={cellIndex}
                    className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap"
                  >
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>

        {tableData.length === 0 && (
          <div className="flex items-center justify-center h-32">
            <p className="text-gray-500">No data available</p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="p-4 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-gray-500">
            Showing {indexOfFirstItem + 1} to {Math.min(indexOfLastItem, tableData.length)} of {tableData.length} entries
          </div>
          <div className="flex space-x-1">
            <button
              onClick={() => goToPage(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => goToPage(page)}
                className={`px-3 py-1 text-sm border rounded ${
                  currentPage === page
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'border-gray-300 hover:bg-gray-50'
                }`}
              >
                {page}
              </button>
            ))}
            <button
              onClick={() => goToPage(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default TableView