/**
 * Utility functions for formatting data in the frontend
 */

export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export const formatTimestamp = (timestamp) => {
  try {
    const date = new Date(timestamp)
    return date.toLocaleString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    return timestamp
  }
}

export const formatDuration = (milliseconds) => {
  const seconds = Math.floor(milliseconds / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`
  } else {
    return `${seconds}s`
  }
}

export const formatNumber = (number) => {
  if (typeof number !== 'number') return '0'
  return number.toLocaleString('es-ES')
}

export const formatPercentage = (value, decimals = 1) => {
  if (typeof value !== 'number') return '0%'
  return `${value.toFixed(decimals)}%`
}

export const getQualityScoreClass = (score) => {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'fair'
  return 'poor'
}

export const getQualityScoreColor = (score) => {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-blue-600'
  if (score >= 40) return 'text-yellow-600'
  return 'text-red-600'
}

export const getSeverityIcon = (severity) => {
  const icons = {
    'ERROR': '❌',
    'WARNING': '⚠️',
    'INFO': 'ℹ️',
    'SUCCESS': '✅'
  }
  return icons[severity] || '•'
}

export const getSeverityClass = (severity) => {
  const classes = {
    'ERROR': 'error',
    'WARNING': 'warning',
    'INFO': 'info',
    'SUCCESS': 'success'
  }
  return classes[severity] || 'info'
}

export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export const capitalizeFirst = (str) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

export const formatErrorCode = (code) => {
  if (!code) return ''
  return code.length > 80 ? code.substring(0, 80) + '...' : code
}

export const getFileExtension = (filename) => {
  if (!filename) return ''
  return filename.split('.').pop().toLowerCase()
}

export const isValidSQLFile = (filename) => {
  const validExtensions = ['sql', 'txt']
  const extension = getFileExtension(filename)
  return validExtensions.includes(extension)
}

export const generateDownloadFilename = (format, originalFilename = null) => {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0]
  const baseName = originalFilename 
    ? originalFilename.replace(/\.[^/.]+$/, '') 
    : 'sql_analysis'
  
  return `${baseName}_${timestamp}.${format}`
}

export const formatAnalysisSummary = (results) => {
  if (!results || !results.summary) return null
  
  const { summary } = results
  
  return {
    totalIssues: (summary.total_errors || 0) + (summary.total_warnings || 0),
    criticalIssues: summary.critical_errors || 0,
    tablesFound: summary.tables_found || 0,
    queriesFound: summary.queries_found || 0,
    qualityScore: results.quality_score || 0
  }
}

export const groupErrorsBySeverity = (errors) => {
  if (!Array.isArray(errors)) return { errors: [], warnings: [] }
  
  return errors.reduce((acc, error) => {
    if (error.severity === 'ERROR') {
      acc.errors.push(error)
    } else {
      acc.warnings.push(error)
    }
    return acc
  }, { errors: [], warnings: [] })
}

export const sortRecommendationsByPriority = (recommendations) => {
  if (!Array.isArray(recommendations)) return []
  
  const priorityOrder = { 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1 }
  
  return recommendations.sort((a, b) => {
    const priorityA = priorityOrder[a.priority] || 0
    const priorityB = priorityOrder[b.priority] || 0
    return priorityB - priorityA
  })
}
