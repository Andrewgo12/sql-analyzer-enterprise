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
 * Analyze SQL file
 * @param {File} file - SQL file to analyze
 * @returns {Promise<Object>} Analysis results
 */
export const analyzeFile = async (file) => {
  if (!file) {
    throw new Error('No se proporcionó archivo')
  }

  // Validate file
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    throw new Error(`Archivo demasiado grande (${(file.size / (1024 * 1024)).toFixed(1)}MB). Máximo: 50MB`)
  }

  const allowedTypes = ['.sql', '.txt']
  const extension = '.' + file.name.split('.').pop().toLowerCase()
  if (!allowedTypes.includes(extension)) {
    throw new Error(`Tipo de archivo no válido. Permitidos: ${allowedTypes.join(', ')}`)
  }

  // Create FormData
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await api.post('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      // Progress tracking could be added here
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
 * Download analysis results in specified format
 * @param {Object} results - Analysis results to download
 * @param {string} format - Download format (json, html, txt, csv)
 * @param {string} filename - Optional custom filename
 */
export const downloadResult = async (results, format, filename = null) => {
  const validFormats = ['json', 'html', 'txt', 'csv', 'sql', 'md']

  if (!validFormats.includes(format)) {
    throw new Error(`Formato no válido. Formatos soportados: ${validFormats.join(', ')}`)
  }

  if (!results) {
    throw new Error('No hay resultados para descargar')
  }

  try {
    const response = await api.post('/download', {
      results: results,
      format: format
    }, {
      responseType: 'blob', // Important for file downloads
    })

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
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
  } catch (error) {
    console.error('Error downloading file:', error)
    throw error
  }
}

/**
 * Check API health
 * @returns {Promise<Object>} Health status
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
 * Get system information
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

// Export default api instance for custom requests
export default api
