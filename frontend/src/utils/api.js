import axios from 'axios'

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Response Error:', error)

    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response

      switch (status) {
        case 400:
          throw new Error(data.error || 'Solicitud inválida')
        case 404:
          throw new Error('Recurso no encontrado')
        case 413:
          throw new Error('Archivo demasiado grande')
        case 500:
          throw new Error('Error interno del servidor')
        default:
          throw new Error(data.error || `Error del servidor (${status})`)
      }
    } else if (error.request) {
      // Network error
      throw new Error('Error de conexión. Verifica tu conexión a internet.')
    } else {
      // Other error
      throw new Error(error.message || 'Error inesperado')
    }
  }
)

/**
 * Analyze SQL file (legacy function - use analyzeSQLWithEngine for new code)
 * @param {File} file - SQL file to analyze
 * @returns {Promise<Object>} Analysis results
 */
export const analyzeFile = async (file) => {
  return analyzeSQLWithEngine(file, 'mysql')
}

/**
 * Download analysis results in specified format (legacy function)
 * @param {Object} results - Analysis results to download
 * @param {string} format - Download format
 * @param {string} filename - Optional custom filename
 */
export const downloadResult = async (results, format, filename = null) => {
  if (!results) {
    throw new Error('No hay resultados para descargar')
  }

  try {
    const blob = await exportAnalysis(results, format)
    downloadFile(blob, format, filename)
  } catch (error) {
    console.error('Error downloading file:', error)
    throw error
  }
}

/**
 * Check API health with comprehensive system metrics
 * @returns {Promise<Object>} Health status with performance data
 */
export const checkHealth = async () => {
  try {
    const response = await api.get('/health')
    return response.data
  } catch (error) {
    console.error('Health check failed:', error)
    throw error
  }
}

/**
 * Get supported database engines
 * @returns {Promise<Object>} Database engines list
 */
export const getSupportedDatabases = async () => {
  try {
    const response = await api.get('/databases/supported')
    return response.data
  } catch (error) {
    console.error('Failed to get database engines:', error)
    throw error
  }
}

/**
 * Get supported export formats
 * @returns {Promise<Object>} Export formats list
 */
export const getExportFormats = async () => {
  try {
    const response = await api.get('/export/formats')
    return response.data
  } catch (error) {
    console.error('Failed to get export formats:', error)
    throw error
  }
}

/**
 * Get dashboard metrics
 * @returns {Promise<Object>} Dashboard metrics data
 */
export const getDashboardMetrics = async () => {
  try {
    const response = await api.get('/metrics/dashboard')
    return response.data
  } catch (error) {
    console.error('Failed to get dashboard metrics:', error)
    throw error
  }
}

/**
 * Get system metrics
 * @returns {Promise<Object>} System performance metrics
 */
export const getSystemMetrics = async () => {
  try {
    const response = await api.get('/metrics')
    return response.data
  } catch (error) {
    console.error('Failed to get system metrics:', error)
    throw error
  }
}

/**
 * Export analysis results in specified format
 * @param {Object} analysisData - Analysis results to export
 * @param {string} format - Export format
 * @returns {Promise<Blob>} Exported file blob
 */
export const exportAnalysis = async (analysisData, format) => {
  try {
    const response = await api.post(`/export/${format}`, analysisData, {
      responseType: 'blob'
    })
    return response.data
  } catch (error) {
    console.error(`Failed to export as ${format}:`, error)
    throw error
  }
}

/**
 * Analyze SQL with database engine selection
 * @param {File} file - SQL file to analyze
 * @param {string} databaseEngine - Target database engine
 * @returns {Promise<Object>} Analysis results
 */
export const analyzeSQLWithEngine = async (file, databaseEngine = 'mysql') => {
  if (!file) {
    throw new Error('No se proporcionó archivo')
  }

  // Validate file
  const maxSize = 100 * 1024 * 1024 // 100MB
  if (file.size > maxSize) {
    throw new Error(`Archivo demasiado grande (${(file.size / (1024 * 1024)).toFixed(1)}MB). Máximo: 100MB`)
  }

  const allowedTypes = ['.sql', '.txt']
  const extension = '.' + file.name.split('.').pop().toLowerCase()
  if (!allowedTypes.includes(extension)) {
    throw new Error(`Tipo de archivo no válido. Permitidos: ${allowedTypes.join(', ')}`)
  }

  // Create FormData
  const formData = new FormData()
  formData.append('file', file)
  formData.append('database_engine', databaseEngine)

  try {
    const response = await api.post('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
        console.log(`Upload progress: ${percentCompleted}%`)
      },
    })

    return response.data
  } catch (error) {
    console.error('Error analyzing file:', error)
    throw error
  }
}

/**
 * Get system information with enhanced health data
 * @returns {Promise<Object>} System info
 */
export const getSystemInfo = async () => {
  try {
    const health = await checkHealth()
    return {
      status: health.status,
      version: health.version,
      timestamp: health.timestamp,
      components: health.components,
      performance: health.performance,
      system: health.system,
      cache_stats: health.cache_stats
    }
  } catch (error) {
    return {
      status: 'error',
      version: 'unknown',
      timestamp: new Date().toISOString(),
      components: {},
      error: error.message,
    }
  }
}

/**
 * Download exported file with proper filename
 * @param {Blob} blob - File blob
 * @param {string} format - File format
 * @param {string} filename - Optional custom filename
 */
export const downloadFile = (blob, format, filename = null) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url

  // Set filename
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const downloadName = filename || `sql_analysis_${timestamp}.${format}`
  link.download = downloadName

  // Trigger download
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  // Clean up
  window.URL.revokeObjectURL(url)

  console.log(`Download completed: ${downloadName}`)
}

// Export default api instance for custom requests
export default api
