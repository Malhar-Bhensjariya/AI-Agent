import React, { useState, useEffect, useMemo } from 'react'
import { useAppContext } from '../../context/AppContext'
import DownloadFile from './DownloadFile'
import { 
  Search, 
  FileText, 
  AlertCircle, 
  ChevronUp, 
  ChevronDown, 
  ChevronLeft, 
  ChevronRight, 
  ChevronsLeft, 
  ChevronsRight,
  Database,
  Filter
} from 'lucide-react'

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
      <div className="flex flex-col items-center justify-center h-full bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-8">
        <div className="text-center max-w-md">
          <div className="mb-6 relative">
            <div className="w-20 h-20 mx-auto bg-white rounded-2xl shadow-lg flex items-center justify-center mb-4">
              <Database className="w-10 h-10 text-blue-500" />
            </div>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Waiting for Data
          </h3>
          <p className="text-gray-600 mb-6 leading-relaxed">
            Your table view is ready. Upload a CSV file in the chat to see your data displayed here with search and sorting capabilities.
          </p>
          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
            <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
              <div className="flex items-center">
                <Search className="w-4 h-4 mr-1" />
                Search
              </div>
              <div className="flex items-center">
                <Filter className="w-4 h-4 mr-1" />
                Sort
              </div>
              <div className="flex items-center">
                <FileText className="w-4 h-4 mr-1" />
                View
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!headers.length || !rawData.length) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 p-8">
        <div className="text-center max-w-md">
          <div className="mb-6">
            <div className="w-24 h-24 mx-auto bg-white rounded-2xl shadow-lg flex items-center justify-center mb-4">
              <AlertCircle className="w-12 h-12 text-orange-500" />
            </div>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No Data Available
          </h3>
          <p className="text-gray-600 mb-4 leading-relaxed">
            The uploaded file appears to be empty or contains invalid data. Please check your file and try uploading again.
          </p>
          <div className="bg-white rounded-lg p-4 shadow-sm border border-orange-200">
            <p className="text-sm text-orange-700">
              <strong>Tip:</strong> Make sure your CSV file has headers and at least one row of data.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header with file info and controls */}
      <div className="flex-shrink-0 border-b bg-gradient-to-r from-slate-50 to-blue-50 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900">
                {getActiveFileName()}
              </h2>
            </div>
            {fileInfo && (
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Database className="w-4 h-4" />
                  <span>{fileInfo.rowCount.toLocaleString()} rows</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>•</span>
                  <span>{headers.length} columns</span>
                </div>
                {fileInfo.updatedAt && (
                  <div className="flex items-center gap-1">
                    <span>•</span>
                    <span>Updated {new Date(fileInfo.updatedAt).toLocaleTimeString()}</span>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Download Component */}
          <DownloadFile
            headers={headers}
            sortedData={sortedData}
            fileName={getActiveFileName()}
            searchTerm={searchTerm}
            sortConfig={sortConfig}
          />
        </div>

        {/* Search */}
        <div className="flex items-center gap-4">
          <div className="flex-1 max-w-md relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search in table..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
            />
          </div>
          <div className="bg-white px-3 py-2 rounded-lg border border-gray-200 text-sm text-gray-600">
            Showing {paginatedData.length} of {sortedData.length} rows
            {searchTerm && ` (filtered from ${displayData.length})`}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead className="bg-gradient-to-r from-gray-50 to-slate-50 sticky top-0">
            <tr>
              {headers.map((header) => (
                <th
                  key={header}
                  className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 border-b border-gray-200 transition-colors"
                  onClick={() => handleSort(header)}
                >
                  <div className="flex items-center gap-2">
                    <span>{header}</span>
                    {sortConfig.key === header ? (
                      sortConfig.direction === 'asc' ? (
                        <ChevronUp className="w-4 h-4 text-blue-500" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-blue-500" />
                      )
                    ) : (
                      <div className="w-4 h-4 opacity-0 group-hover:opacity-50">
                        <ChevronUp className="w-4 h-4 text-gray-400" />
                      </div>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedData.map((row, index) => (
              <tr 
                key={row._tableId} 
                className={`hover:bg-blue-50 transition-colors ${
                  index % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                }`}
              >
                {headers.map((header) => (
                  <td 
                    key={`${row._tableId}-${header}`}
                    className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate"
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
        <div className="flex-shrink-0 border-t bg-gradient-to-r from-slate-50 to-blue-50 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700 font-medium">
              Page {currentPage} of {totalPages}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => goToPage(1)}
                disabled={currentPage === 1}
                className="px-3 py-2 text-sm border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white hover:shadow-sm transition-all duration-200 flex items-center gap-1"
              >
                <ChevronsLeft className="w-4 h-4" />
                First
              </button>
              <button
                onClick={() => goToPage(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-3 py-2 text-sm border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white hover:shadow-sm transition-all duration-200 flex items-center gap-1"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </button>
              <button
                onClick={() => goToPage(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-3 py-2 text-sm border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white hover:shadow-sm transition-all duration-200 flex items-center gap-1"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => goToPage(totalPages)}
                disabled={currentPage === totalPages}
                className="px-3 py-2 text-sm border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white hover:shadow-sm transition-all duration-200 flex items-center gap-1"
              >
                Last
                <ChevronsRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TableView