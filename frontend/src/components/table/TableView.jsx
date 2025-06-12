import React, { useState, useEffect, useMemo } from 'react'
import { useAppContext } from '../../context/AppContext'

const TableView = () => {
  const { 
    getCurrentTableData, 
    getCurrentHeaders, 
    hasActiveFile, 
    getActiveFileName,
    getActiveFileInfo 
  } = useAppContext()
  
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(20)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })

  // Get data directly from context
  const rawData = getCurrentTableData()
  const headers = getCurrentHeaders()
  const fileInfo = getActiveFileInfo()

  // Reset page when data changes
  useEffect(() => {
    setCurrentPage(1)
  }, [rawData])

  // Reorder data to match header order (ensure column consistency)
  const reorderedData = useMemo(() => {
    if (!rawData.length || !headers.length) return rawData
    
    return rawData.map((row, index) => {
      const reorderedRow = { _tableId: index }
      // Add columns in the exact order specified by headers
      headers.forEach(header => {
        reorderedRow[header] = row[header]
      })
      return reorderedRow
    })
  }, [rawData, headers])

  // Use reordered data instead of raw data
  const displayData = reorderedData

  // Filter data based on search term
  const filteredData = useMemo(() => {
    if (!searchTerm.trim()) return displayData

    return displayData.filter(row =>
      headers.some(header => {
        const value = row[header]
        if (value == null) return false
        return value.toString().toLowerCase().includes(searchTerm.toLowerCase())
      })
    )
  }, [displayData, headers, searchTerm])

  // Sort data
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return filteredData

    return [...filteredData].sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]

      // Handle null/undefined values
      if (aValue == null && bValue == null) return 0
      if (aValue == null) return sortConfig.direction === 'asc' ? 1 : -1
      if (bValue == null) return sortConfig.direction === 'asc' ? -1 : 1

      // Try numeric comparison first
      const aNum = Number(aValue)
      const bNum = Number(bValue)
      
      if (!isNaN(aNum) && !isNaN(bNum)) {
        return sortConfig.direction === 'asc' ? aNum - bNum : bNum - aNum
      }

      // String comparison
      const aStr = aValue.toString().toLowerCase()
      const bStr = bValue.toString().toLowerCase()
      
      if (aStr < bStr) return sortConfig.direction === 'asc' ? -1 : 1
      if (aStr > bStr) return sortConfig.direction === 'asc' ? 1 : -1
      return 0
    })
  }, [filteredData, sortConfig])

  // Pagination
  const totalPages = Math.ceil(sortedData.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const paginatedData = sortedData.slice(startIndex, startIndex + itemsPerPage)

  // Sorting handler
  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  // Pagination handlers
  const goToPage = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)))
  }

  const formatCellValue = (value) => {
    if (value == null) return ''
    if (typeof value === 'number') {
      return value.toLocaleString()
    }
    return value.toString()
  }

  // Show loading or empty state
  if (!hasActiveFile()) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <div className="text-xl mb-2">📊</div>
          <div>No data to display</div>
          <div className="text-sm">Upload a CSV file to see your data here</div>
        </div>
      </div>
    )
  }

  if (!headers.length || !rawData.length) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <div className="text-xl mb-2">⚠️</div>
          <div>No data available</div>
          <div className="text-sm">The file appears to be empty or invalid</div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header with file info and controls */}
      <div className="flex-shrink-0 border-b bg-gray-50 p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              📄 {getActiveFileName()}
            </h2>
            {fileInfo && (
              <div className="text-sm text-gray-600 mt-1">
                {fileInfo.rowCount.toLocaleString()} rows • {headers.length} columns
                {fileInfo.updatedAt && (
                  <span className="ml-2">• Updated {new Date(fileInfo.updatedAt).toLocaleTimeString()}</span>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Search */}
        <div className="flex items-center gap-4">
          <div className="flex-1 max-w-md">
            <input
              type="text"
              placeholder="Search in table..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="text-sm text-gray-600">
            Showing {paginatedData.length} of {sortedData.length} rows
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              {headers.map((header) => (
                <th
                  key={header}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 border-b"
                  onClick={() => handleSort(header)}
                >
                  <div className="flex items-center gap-1">
                    <span>{header}</span>
                    {sortConfig.key === header && (
                      <span className="text-blue-500">
                        {sortConfig.direction === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedData.map((row) => (
              <tr 
                key={row._tableId} 
                className="hover:bg-gray-50 transition-colors"
              >
                {headers.map((header) => (
                  <td 
                    key={`${row._tableId}-${header}`}
                    className="px-4 py-3 text-sm text-gray-900 max-w-xs truncate"
                    title={formatCellValue(row[header])}
                  >
                    {formatCellValue(row[header])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex-shrink-0 border-t bg-gray-50 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Page {currentPage} of {totalPages}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => goToPage(1)}
                disabled={currentPage === 1}
                className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                First
              </button>
              <button
                onClick={() => goToPage(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                Previous
              </button>
              <button
                onClick={() => goToPage(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                Next
              </button>
              <button
                onClick={() => goToPage(totalPages)}
                disabled={currentPage === totalPages}
                className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                Last
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TableView