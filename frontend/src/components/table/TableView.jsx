import React, { useState, useEffect } from 'react'
import { useAppContext } from '../../context/AppContext'

const TableView = () => {
  const { tableData: contextTableData, currentFile } = useAppContext()
  const [displayData, setDisplayData] = useState([])
  const [headers, setHeaders] = useState([])
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(20)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })
  const [debugInfo, setDebugInfo] = useState('')

  // Debug: Log the contextTableData to see what we're getting
  useEffect(() => {
    console.log('=== TableView Debug Info ===')
    console.log('contextTableData:', contextTableData)
    console.log('contextTableData type:', typeof contextTableData)
    console.log('contextTableData is array:', Array.isArray(contextTableData))
    console.log('currentFile:', currentFile)
    
    if (contextTableData) {
      console.log('contextTableData keys:', Object.keys(contextTableData))
      if (Array.isArray(contextTableData)) {
        console.log('Array length:', contextTableData.length)
        console.log('First item:', contextTableData[0])
      }
      setDebugInfo(`Type: ${typeof contextTableData}, IsArray: ${Array.isArray(contextTableData)}, Keys: ${Object.keys(contextTableData).join(', ')}`)
    } else {
      setDebugInfo('contextTableData is null/undefined')
    }
    console.log('=== End Debug Info ===')
  }, [contextTableData, currentFile])

  // Update display data when context table data changes
  useEffect(() => {
    if (contextTableData) {
      try {
        // Handle different table data formats
        let processedHeaders = []
        let processedRows = []

        console.log('Processing table data...')

        // Check for standard format: { headers: [], rows: [[]] }
        if (contextTableData.headers && contextTableData.rows) {
          console.log('Using headers/rows format')
          processedHeaders = contextTableData.headers
          processedRows = contextTableData.rows
        } 
        // Check for array of objects format: [{ col1: val1, col2: val2 }, ...]
        else if (Array.isArray(contextTableData)) {
          console.log('Using array format')
          if (contextTableData.length > 0 && typeof contextTableData[0] === 'object') {
            processedHeaders = Object.keys(contextTableData[0])
            processedRows = contextTableData.map(row => 
              processedHeaders.map(header => row[header])
            )
          }
        } 
        // Check for nested format: { data: [...] }
        else if (contextTableData.data) {
          console.log('Using nested data format')
          const data = contextTableData.data
          if (Array.isArray(data) && data.length > 0) {
            if (typeof data[0] === 'object') {
              processedHeaders = Object.keys(data[0])
              processedRows = data.map(row => 
                processedHeaders.map(header => row[header])
              )
            }
          }
        }
        // Try to handle other object formats
        else if (typeof contextTableData === 'object') {
          console.log('Trying to handle generic object format')
          const keys = Object.keys(contextTableData)
          
          // Check if any key contains array data
          for (const key of keys) {
            if (Array.isArray(contextTableData[key]) && contextTableData[key].length > 0) {
              console.log(`Found array data in key: ${key}`)
              const data = contextTableData[key]
              if (typeof data[0] === 'object') {
                processedHeaders = Object.keys(data[0])
                processedRows = data.map(row => 
                  processedHeaders.map(header => row[header])
                )
                break
              }
            }
          }
        }

        console.log('Processed headers:', processedHeaders)
        console.log('Processed rows count:', processedRows.length)
        console.log('First row sample:', processedRows[0])

        setHeaders(processedHeaders)
        
        // Convert rows to objects for easier manipulation
        const dataObjects = processedRows.map((row, index) => {
          const obj = { _id: index }
          processedHeaders.forEach((header, headerIndex) => {
            obj[header] = row[headerIndex]
          })
          return obj
        })
        
        console.log('Final data objects count:', dataObjects.length)
        console.log('First data object:', dataObjects[0])
        
        setDisplayData(dataObjects)
        setCurrentPage(1) // Reset to first page when data changes
      } catch (error) {
        console.error('Error processing table data:', error)
        setHeaders([])
        setDisplayData([])
      }
    } else {
      console.log('No contextTableData available')
      setHeaders([])
      setDisplayData([])
    }
  }, [contextTableData])

  // Filter data based on search term
  const filteredData = displayData.filter(row =>
    headers.some(header => {
      const value = row[header]
      return value && value.toString().toLowerCase().includes(searchTerm.toLowerCase())
    })
  )

  // Sort data
  const sortedData = React.useMemo(() => {
    if (!sortConfig.key) return filteredData

    return [...filteredData].sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]

      // Handle null/undefined values
      if (aValue == null && bValue == null) return 0
      if (aValue == null) return 1
      if (bValue == null) return -1

      // Try to parse as numbers for proper numeric sorting
      const aNum = parseFloat(aValue)
      const bNum = parseFloat(bValue)
      
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

  // Pagination logic
  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = sortedData.slice(indexOfFirstItem, indexOfLastItem)
  const totalPages = Math.ceil(sortedData.length / itemsPerPage)

  const goToPage = (pageNumber) => {
    setCurrentPage(Math.max(1, Math.min(pageNumber, totalPages)))
  }

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  const formatCellValue = (value) => {
    if (value == null) return ''
    if (typeof value === 'number') {
      // Format numbers with appropriate decimal places
      return value % 1 === 0 ? value.toString() : value.toFixed(2)
    }
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No'
    }
    return value.toString()
  }

  const exportToCSV = () => {
    if (!headers.length || !sortedData.length) return

    const csvContent = [
      headers.join(','),
      ...sortedData.map(row => 
        headers.map(header => {
          const value = row[header]
          // Escape quotes and wrap in quotes if contains comma
          const stringValue = formatCellValue(value)
          return stringValue.includes(',') ? `"${stringValue.replace(/"/g, '""')}"` : stringValue
        }).join(',')
      )
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `${currentFile?.name || 'table'}-export-${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const getSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) {
      return '↕️'
    }
    return sortConfig.direction === 'asc' ? '↑' : '↓'
  }

  // Generate pagination buttons
  const renderPaginationButtons = () => {
    const buttons = []
    const maxVisibleButtons = 5
    
    let startPage = Math.max(1, currentPage - Math.floor(maxVisibleButtons / 2))
    let endPage = Math.min(totalPages, startPage + maxVisibleButtons - 1)
    
    if (endPage - startPage + 1 < maxVisibleButtons) {
      startPage = Math.max(1, endPage - maxVisibleButtons + 1)
    }

    // First page and previous
    if (currentPage > 1) {
      buttons.push(
        <button
          key="first"
          onClick={() => goToPage(1)}
          className="px-3 py-1 mx-1 bg-gray-200 hover:bg-gray-300 rounded"
        >
          First
        </button>
      )
      buttons.push(
        <button
          key="prev"
          onClick={() => goToPage(currentPage - 1)}
          className="px-3 py-1 mx-1 bg-gray-200 hover:bg-gray-300 rounded"
        >
          ←
        </button>
      )
    }

    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
      buttons.push(
        <button
          key={i}
          onClick={() => goToPage(i)}
          className={`px-3 py-1 mx-1 rounded ${
            i === currentPage
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 hover:bg-gray-300'
          }`}
        >
          {i}
        </button>
      )
    }

    // Next and last page
    if (currentPage < totalPages) {
      buttons.push(
        <button
          key="next"
          onClick={() => goToPage(currentPage + 1)}
          className="px-3 py-1 mx-1 bg-gray-200 hover:bg-gray-300 rounded"
        >
          →
        </button>
      )
      buttons.push(
        <button
          key="last"
          onClick={() => goToPage(totalPages)}
          className="px-3 py-1 mx-1 bg-gray-200 hover:bg-gray-300 rounded"
        >
          Last
        </button>
      )
    }

    return buttons
  }

  // Show placeholder when no data is available
  if (!contextTableData || !headers.length) {
    return (
      <div className="h-full bg-white border-l border-gray-200 flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b bg-gray-50">
          <div className="flex items-center space-x-4">
            <h2 className="text-xl font-semibold">Data View</h2>
            <span className="text-sm text-gray-500">
              {currentFile ? `File: ${currentFile.name}` : 'No file selected'}
            </span>
          </div>
        </div>

        {/* Debug Info */}
        <div className="p-4 bg-yellow-50 border-b">
          <p className="text-sm text-yellow-800">
            <strong>Debug:</strong> {debugInfo}
          </p>
          <p className="text-xs text-yellow-700 mt-1">
            Check browser console for detailed logs
          </p>
        </div>

        {/* Placeholder Content */}
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md p-8">
            <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              {currentFile ? 'Processing File Data' : 'No Data Available'}
            </h3>
            <p className="text-gray-600 text-sm">
              {currentFile 
                ? 'Upload a data file and ask questions to see the data visualization here.' 
                : 'Upload a data file (CSV, Excel, JSON) to view and analyze your data.'}
            </p>
            {currentFile && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800 font-medium">{currentFile.name}</p>
                <p className="text-xs text-blue-600">
                  {currentFile.size ? `${Math.round(currentFile.size / 1024)} KB` : 'Processing...'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-white border-l border-gray-200 flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center p-4 border-b bg-gray-50">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold">Data View</h2>
          <span className="text-sm text-gray-500">
            {sortedData.length} rows, {headers.length} columns
          </span>
          {currentFile && (
            <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
              {currentFile.name}
            </span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={exportToCSV}
            className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 text-sm"
          >
            Export CSV
          </button>
        </div>
      </div>

      {/* Search and Controls */}
      <div className="p-4 border-b bg-gray-50">
        <div className="flex justify-between items-center">
          <input
            type="text"
            placeholder="Search table data..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-3 py-2 border rounded-lg w-64 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="text-sm text-gray-600">
            Showing {Math.min(indexOfFirstItem + 1, sortedData.length)}-{Math.min(indexOfLastItem, sortedData.length)} of {sortedData.length} entries
            {searchTerm && ` (filtered from ${displayData.length} total)`}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead className="bg-gray-100 sticky top-0">
            <tr>
              {headers.map((header) => (
                <th
                  key={header}
                  className="px-4 py-3 text-left text-sm font-medium text-gray-700 cursor-pointer hover:bg-gray-200 select-none"
                  onClick={() => handleSort(header)}
                >
                  <div className="flex items-center justify-between">
                    <span className="truncate">{header}</span>
                    <span className="ml-2 text-gray-400">
                      {getSortIcon(header)}
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentItems.map((row, index) => (
              <tr
                key={row._id}
                className={`border-b hover:bg-gray-50 ${
                  index % 2 === 0 ? 'bg-white' : 'bg-gray-25'
                }`}
              >
                {headers.map((header) => (
                  <td
                    key={`${row._id}-${header}`}
                    className="px-4 py-3 text-sm text-gray-900"
                  >
                    <div className="max-w-xs truncate" title={formatCellValue(row[header])}>
                      {formatCellValue(row[header])}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="p-4 border-t bg-gray-50">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </div>
            <div className="flex items-center">
              {renderPaginationButtons()}
            </div>
            <div className="text-sm text-gray-600">
              {itemsPerPage} per page
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TableView