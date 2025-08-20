import React, { useState, useEffect } from 'react'
import { Download, ChevronDown as DropdownIcon, CheckCircle, AlertCircle } from 'lucide-react'

const DownloadFile = ({ 
  headers, 
  sortedData, 
  fileName, 
  searchTerm, 
  sortConfig,
  disabled = false 
}) => {
  const [isDownloading, setIsDownloading] = useState(false)
  const [downloadFormat, setDownloadFormat] = useState('csv')
  const [showDropdown, setShowDropdown] = useState(false)
  const [toast, setToast] = useState(null)

  // Format options configuration
  const formatOptions = [
    { value: 'csv', label: 'CSV', description: 'Comma-separated values' },
    { value: 'excel', label: 'Excel', description: 'Excel spreadsheet (.xls)' },
    { value: 'html', label: 'HTML', description: 'Print-ready HTML document' },
    { value: 'pdf', label: 'PDF', description: 'Portable Document Format' }
  ]

  // Toast notification system
  const showToast = (message, type = 'success') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 4000)
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showDropdown && !event.target.closest('.download-dropdown')) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [showDropdown])

  // Main download handler
  const downloadFile = async () => {
    if (!headers.length || !sortedData.length) {
      showToast('No data available to download', 'error')
      return
    }

    setIsDownloading(true)

    try {
      const baseFilename = fileName.replace(/\.[^/.]+$/, '') // Remove extension
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0]
      
      switch (downloadFormat) {
        case 'csv':
          await downloadCSV(baseFilename, timestamp)
          showToast(`CSV file downloaded successfully!`)
          break
        case 'excel':
          await downloadExcel(baseFilename, timestamp)
          showToast(`Excel file downloaded successfully!`)
          break
        case 'html':
          await downloadHTML(baseFilename, timestamp)
          showToast(`HTML file downloaded! You can print it to PDF from your browser.`)
          break
        case 'pdf':
          await downloadPDF(baseFilename, timestamp)
          showToast(`PDF file downloaded successfully!`)
          break
        default:
          await downloadCSV(baseFilename, timestamp)
          showToast(`CSV file downloaded successfully!`)
      }
    } catch (error) {
      console.error(`Error downloading ${downloadFormat.toUpperCase()}:`, error)
      showToast(`Error downloading ${downloadFormat.toUpperCase()} file. Please try again.`, 'error')
    } finally {
      setIsDownloading(false)
      setShowDropdown(false)
    }
  }

  // CSV export function
  const downloadCSV = async (baseFilename, timestamp) => {
    const csvRows = []
    
    // Add header row
    csvRows.push(headers.join(','))
    
    // Add data rows
    sortedData.forEach(row => {
      const csvRow = headers.map(header => {
        const value = row[header]
        if (value == null) return ''
        
        // Escape quotes and wrap in quotes if contains comma, quote, or newline
        const stringValue = value.toString()
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`
        }
        return stringValue
      })
      csvRows.push(csvRow.join(','))
    })

    const csvContent = csvRows.join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const filename = `${baseFilename}_modified_${timestamp}.csv`
    downloadBlob(blob, filename)
  }

  // Excel export function
  const downloadExcel = async (baseFilename, timestamp) => {
    let htmlContent = `
      <html>
        <head>
          <meta charset="utf-8">
          <style>
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; font-weight: bold; }
          </style>
        </head>
        <body>
          <table>
            <thead>
              <tr>
    `
    
    // Add headers
    headers.forEach(header => {
      htmlContent += `<th>${escapeHtml(header)}</th>`
    })
    
    htmlContent += `
              </tr>
            </thead>
            <tbody>
    `
    
    // Add data rows
    sortedData.forEach(row => {
      htmlContent += '<tr>'
      headers.forEach(header => {
        const value = row[header]
        const cellValue = value == null ? '' : escapeHtml(value.toString())
        htmlContent += `<td>${cellValue}</td>`
      })
      htmlContent += '</tr>'
    })
    
    htmlContent += `
            </tbody>
          </table>
        </body>
      </html>
    `
    
    const blob = new Blob([htmlContent], { 
      type: 'application/vnd.ms-excel;charset=utf-8;' 
    })
    const filename = `${baseFilename}_modified_${timestamp}.xls`
    downloadBlob(blob, filename)
  }

  // HTML export function (fixed)
  const downloadHTML = async (baseFilename, timestamp) => {
    try {
      let htmlContent = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${escapeHtml(baseFilename)} - Data Export</title>
  <style>
    body { 
      font-family: Arial, sans-serif; 
      margin: 20px; 
      font-size: 12px;
      color: #333;
    }
    h1 { 
      color: #333; 
      font-size: 18px; 
      margin-bottom: 20px;
      border-bottom: 2px solid #007bff;
      padding-bottom: 10px;
    }
    table { 
      border-collapse: collapse; 
      width: 100%; 
      margin-top: 10px;
    }
    th, td { 
      border: 1px solid #ddd; 
      padding: 6px; 
      text-align: left; 
      word-wrap: break-word;
      max-width: 150px;
    }
    th { 
      background-color: #f8f9fa; 
      font-weight: bold; 
      font-size: 11px;
    }
    tr:nth-child(even) { 
      background-color: #f9f9f9; 
    }
    .summary {
      margin-bottom: 15px;
      padding: 10px;
      background-color: #f0f7ff;
      border-left: 4px solid #007bff;
      border-radius: 4px;
    }
    .footer {
      margin-top: 20px;
      text-align: center;
      color: #666;
      font-size: 10px;
    }
    @media print {
      body { margin: 10px; }
      table { font-size: 10px; }
      th, td { padding: 4px; }
    }
  </style>
</head>
<body>
  <h1>Data Export - ${escapeHtml(baseFilename)}</h1>
  <div class="summary">
    <strong>Export Summary:</strong><br>
    Total Rows: ${sortedData.length.toLocaleString()}<br>
    Total Columns: ${headers.length}<br>
    Export Date: ${new Date().toLocaleString()}<br>`

      if (searchTerm) {
        htmlContent += `    Filter Applied: "${escapeHtml(searchTerm)}"<br>`
      }
      
      if (sortConfig && sortConfig.key) {
        htmlContent += `    Sorted by: ${escapeHtml(sortConfig.key)} (${escapeHtml(sortConfig.direction)})<br>`
      }

      htmlContent += `  </div>
  <table>
    <thead>
      <tr>`
    
      // Add headers
      headers.forEach(header => {
        htmlContent += `<th>${escapeHtml(header)}</th>`
      })
      
      htmlContent += `</tr>
    </thead>
    <tbody>`
      
      // Add data rows (limit to first 1000 rows for performance)
      const dataToExport = sortedData.slice(0, 1000)
      dataToExport.forEach(row => {
        htmlContent += '<tr>'
        headers.forEach(header => {
          const value = row[header]
          let cellValue = value == null ? '' : value.toString()
          // Truncate very long values for readability
          if (cellValue.length > 50) {
            cellValue = cellValue.substring(0, 47) + '...'
          }
          htmlContent += `<td>${escapeHtml(cellValue)}</td>`
        })
        htmlContent += '</tr>'
      })
      
      if (sortedData.length > 1000) {
        htmlContent += `<tr>
          <td colspan="${headers.length}" style="text-align: center; font-style: italic; color: #666;">
            ... and ${(sortedData.length - 1000).toLocaleString()} more rows (HTML limited to first 1000 rows)
          </td>
        </tr>`
      }
      
      htmlContent += `    </tbody>
  </table>
  <div class="footer">
    Generated on ${new Date().toLocaleString()}
  </div>
</body>
</html>`
      
      const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8;' })
      const filename = `${baseFilename}_modified_${timestamp}.html`
      downloadBlob(blob, filename)
    } catch (error) {
      console.error('HTML generation error:', error)
      throw new Error('Failed to generate HTML content')
    }
  }

  // PDF export function
  const downloadPDF = async (baseFilename, timestamp) => {
    try {
      // Create a new window for printing
      const printWindow = window.open('', '_blank')
      
      // Build HTML content for PDF
      let htmlContent = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${escapeHtml(baseFilename)} - Data Export</title>
  <style>
    body { 
      font-family: Arial, sans-serif; 
      margin: 15px; 
      font-size: 12px;
      color: #333;
    }
    h1 { 
      color: #333; 
      font-size: 18px; 
      margin-bottom: 15px;
      border-bottom: 2px solid #007bff;
      padding-bottom: 8px;
    }
    table { 
      border-collapse: collapse; 
      width: 100%; 
      margin-top: 10px;
      page-break-inside: auto;
    }
    th, td { 
      border: 1px solid #ddd; 
      padding: 6px; 
      text-align: left; 
      word-wrap: break-word;
      max-width: 150px;
    }
    th { 
      background-color: #f8f9fa; 
      font-weight: bold; 
      font-size: 11px;
    }
    tr { 
      page-break-inside: avoid; 
      page-break-after: auto;
    }
    tr:nth-child(even) { 
      background-color: #f9f9f9; 
    }
    .summary {
      margin-bottom: 15px;
      padding: 10px;
      background-color: #f0f7ff;
      border-left: 4px solid #007bff;
      border-radius: 4px;
    }
    .footer {
      margin-top: 20px;
      text-align: center;
      color: #666;
      font-size: 10px;
    }
    @media print {
      body { margin: 10px; }
      table { font-size: 10px; }
      th, td { padding: 4px; }
      .summary {
        page-break-inside: avoid;
      }
    }
  </style>
</head>
<body>
  <h1>Data Export - ${escapeHtml(baseFilename)}</h1>
  <div class="summary">
    <strong>Export Summary:</strong><br>
    Total Rows: ${sortedData.length.toLocaleString()}<br>
    Total Columns: ${headers.length}<br>
    Export Date: ${new Date().toLocaleString()}<br>`

      if (searchTerm) {
        htmlContent += `    Filter Applied: "${escapeHtml(searchTerm)}"<br>`
      }
      
      if (sortConfig && sortConfig.key) {
        htmlContent += `    Sorted by: ${escapeHtml(sortConfig.key)} (${escapeHtml(sortConfig.direction)})<br>`
      }

      htmlContent += `  </div>
  <table>
    <thead>
      <tr>`
    
      // Add headers
      headers.forEach(header => {
        htmlContent += `<th>${escapeHtml(header)}</th>`
      })
      
      htmlContent += `</tr>
    </thead>
    <tbody>`
      
      // Add data rows
      sortedData.forEach(row => {
        htmlContent += '<tr>'
        headers.forEach(header => {
          const value = row[header]
          let cellValue = value == null ? '' : value.toString()
          // Truncate very long values for readability
          if (cellValue.length > 50) {
            cellValue = cellValue.substring(0, 47) + '...'
          }
          htmlContent += `<td>${escapeHtml(cellValue)}</td>`
        })
        htmlContent += '</tr>'
      })
      
      htmlContent += `    </tbody>
  </table>
  <div class="footer">
    Generated on ${new Date().toLocaleString()}
  </div>
</body>
</html>`

      // Write content to the new window
      printWindow.document.write(htmlContent)
      printWindow.document.close()
      
      // Wait for content to load then trigger print
      printWindow.onload = function() {
        setTimeout(() => {
          printWindow.print()
          // Close the window after a short delay
          setTimeout(() => {
            printWindow.close()
          }, 500)
        }, 250)
      }
    } catch (error) {
      console.error('PDF generation error:', error)
      throw new Error('Failed to generate PDF')
    }
  }

  // HTML escape utility function
  const escapeHtml = (text) => {
    if (text == null) return ''
    return text.toString()
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;')
  }

  // Utility function to download blob
  const downloadBlob = (blob, filename) => {
    try {
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.href = url
      link.download = filename
      link.style.display = 'none'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      // Clean up the URL object after a short delay
      setTimeout(() => {
        URL.revokeObjectURL(url)
      }, 100)
    } catch (error) {
      console.error('Download error:', error)
      throw new Error('Failed to download file')
    }
  }

  return (
    <div className="relative download-dropdown">
      {/* Toast Notification */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 max-w-sm p-4 rounded-lg shadow-lg transition-all duration-300 ${
          toast.type === 'error' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
        }`}>
          <div className="flex items-center gap-2">
            {toast.type === 'error' ? (
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
            ) : (
              <CheckCircle className="w-5 h-5 flex-shrink-0" />
            )}
            <p className="text-sm font-medium">{toast.message}</p>
          </div>
        </div>
      )}

      <div className="flex">
        <button
          onClick={downloadFile}
          disabled={disabled || isDownloading || !headers.length || !sortedData.length}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-l-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          <Download className="w-4 h-4" />
          {isDownloading ? 'Downloading...' : `Download ${downloadFormat.toUpperCase()}`}
        </button>
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          disabled={disabled || isDownloading || !headers.length || !sortedData.length}
          className="px-2 py-2 bg-blue-600 text-white rounded-r-lg border-l border-blue-500 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          <DropdownIcon className="w-4 h-4" />
        </button>
      </div>
      
      {showDropdown && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          <div className="py-2">
            <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-100">
              Export Format
            </div>
            {formatOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => {
                  setDownloadFormat(option.value)
                  setShowDropdown(false)
                }}
                className={`w-full text-left px-4 py-3 text-sm hover:bg-gray-50 transition-colors duration-150 ${
                  downloadFormat === option.value ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{option.label}</div>
                    <div className="text-xs text-gray-500">{option.description}</div>
                  </div>
                  {downloadFormat === option.value && (
                    <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                  )}
                </div>
              </button>
            ))}
            <div className="border-t border-gray-100 mt-2 pt-2 px-4 pb-2">
              <div className="text-xs text-gray-500">
                {downloadFormat === 'html' && '• HTML exports first 1000 rows for performance'}
                {downloadFormat === 'excel' && '• Excel format (.xls) compatible'}
                {downloadFormat === 'csv' && '• Standard CSV format'}
                {downloadFormat === 'pdf' && '• PDF uses browser print functionality'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DownloadFile