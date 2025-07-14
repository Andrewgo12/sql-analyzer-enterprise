/**
 * Application constants and configuration
 */

export const APP_CONFIG = {
  name: 'SQL Analyzer Enterprise',
  version: '2.0',
  description: 'Herramienta profesional de análisis SQL con interfaz moderna',
  author: 'SQL Analyzer Team'
}

export const API_CONFIG = {
  baseURL: '/api',
  timeout: 30000, // 30 seconds
  maxRetries: 3,
  retryDelay: 1000 // 1 second
}

export const FILE_CONFIG = {
  maxSize: 50 * 1024 * 1024, // 50MB
  allowedExtensions: ['.sql', '.txt'],
  allowedMimeTypes: ['text/plain', 'application/sql']
}

export const DOWNLOAD_FORMATS = {
  json: {
    label: 'JSON',
    description: 'Datos estructurados en formato JSON',
    mimeType: 'application/json',
    icon: 'Code'
  },
  html: {
    label: 'HTML',
    description: 'Reporte visual en formato HTML',
    mimeType: 'text/html',
    icon: 'Globe'
  },
  txt: {
    label: 'TXT',
    description: 'Reporte de texto plano',
    mimeType: 'text/plain',
    icon: 'FileText'
  },
  csv: {
    label: 'CSV',
    description: 'Datos tabulares en formato CSV',
    mimeType: 'text/csv',
    icon: 'Table'
  },
  sql: {
    label: 'SQL',
    description: 'Código SQL procesado',
    mimeType: 'text/plain',
    icon: 'Database'
  },
  md: {
    label: 'Markdown',
    description: 'Documentación en formato Markdown',
    mimeType: 'text/markdown',
    icon: 'FileText'
  }
}

export const QUALITY_SCORE_RANGES = {
  excellent: { min: 80, max: 100, color: 'green', label: 'Excelente' },
  good: { min: 60, max: 79, color: 'blue', label: 'Bueno' },
  fair: { min: 40, max: 59, color: 'yellow', label: 'Regular' },
  poor: { min: 0, max: 39, color: 'red', label: 'Deficiente' }
}

export const ERROR_SEVERITIES = {
  ERROR: {
    label: 'Error',
    color: 'red',
    icon: 'XCircle',
    priority: 3
  },
  WARNING: {
    label: 'Advertencia',
    color: 'yellow',
    icon: 'AlertTriangle',
    priority: 2
  },
  INFO: {
    label: 'Información',
    color: 'blue',
    icon: 'Info',
    priority: 1
  }
}

export const RECOMMENDATION_PRIORITIES = {
  HIGH: {
    label: 'Alta',
    color: 'red',
    weight: 3
  },
  MEDIUM: {
    label: 'Media',
    color: 'yellow',
    weight: 2
  },
  LOW: {
    label: 'Baja',
    color: 'blue',
    weight: 1
  }
}

export const ANALYSIS_FEATURES = [
  {
    id: 'syntax',
    name: 'Análisis de Sintaxis',
    description: 'Detecta errores de sintaxis SQL',
    icon: 'Bug'
  },
  {
    id: 'performance',
    name: 'Análisis de Rendimiento',
    description: 'Identifica problemas de rendimiento',
    icon: 'TrendingUp'
  },
  {
    id: 'security',
    name: 'Análisis de Seguridad',
    description: 'Detecta vulnerabilidades de seguridad',
    icon: 'Shield'
  },
  {
    id: 'schema',
    name: 'Análisis de Esquema',
    description: 'Analiza estructura de base de datos',
    icon: 'Database'
  },
  {
    id: 'recommendations',
    name: 'Recomendaciones',
    description: 'Sugerencias de mejora',
    icon: 'MessageSquare'
  }
]

export const NAVIGATION_ITEMS = [
  {
    name: 'Inicio',
    href: '/',
    icon: 'Home'
  },
  {
    name: 'Analizar',
    href: '/analyze',
    icon: 'Search'
  }
]

export const STATISTICS_LABELS = {
  total_lines: 'Líneas Totales',
  non_empty_lines: 'Líneas con Contenido',
  comment_lines: 'Líneas de Comentarios',
  character_count: 'Caracteres',
  sql_statements: 'Statements SQL',
  tables_found: 'Tablas Encontradas',
  queries_found: 'Consultas Encontradas',
  total_errors: 'Errores Totales',
  total_warnings: 'Advertencias Totales',
  critical_errors: 'Errores Críticos'
}

export const LOADING_MESSAGES = [
  'Analizando estructura SQL...',
  'Detectando errores de sintaxis...',
  'Evaluando rendimiento...',
  'Verificando seguridad...',
  'Generando recomendaciones...',
  'Calculando score de calidad...',
  'Finalizando análisis...'
]

export const SUCCESS_MESSAGES = {
  fileSelected: 'Archivo seleccionado correctamente',
  analysisComplete: 'Análisis completado exitosamente',
  downloadStarted: 'Descarga iniciada',
  systemReady: 'Sistema listo para usar'
}

export const ERROR_MESSAGES = {
  fileTooBig: 'Archivo demasiado grande',
  invalidFileType: 'Tipo de archivo no válido',
  noFileSelected: 'No se seleccionó archivo',
  analysisError: 'Error durante el análisis',
  networkError: 'Error de conexión',
  serverError: 'Error del servidor',
  unknownError: 'Error desconocido'
}

export const BREAKPOINTS = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px'
}

export const ANIMATION_DURATIONS = {
  fast: 150,
  normal: 300,
  slow: 500
}

export const Z_INDEX = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modal: 1040,
  popover: 1050,
  tooltip: 1060,
  toast: 1070
}
