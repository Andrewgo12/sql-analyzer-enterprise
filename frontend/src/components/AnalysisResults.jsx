import React from 'react'
import { motion } from 'framer-motion'
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Info,
  FileText,
  Database,
  Clock,
  TrendingUp,
  Download,
  ChevronDown
} from 'lucide-react'
import { useState } from 'react'

const AnalysisResults = ({ results, onDownload }) => {
  const [expandedSections, setExpandedSections] = useState({
    errors: true,
    recommendations: true,
    statistics: false
  })

  if (!results || !results.filename) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-8 text-center"
      >
        <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Error en el Análisis
        </h3>
        <p className="text-gray-600">
          {results?.error || 'Ha ocurrido un error inesperado durante el análisis.'}
        </p>
      </motion.div>
    )
  }

  const getQualityScoreClass = (score) => {
    if (score >= 80) return 'excellent'
    if (score >= 60) return 'good'
    if (score >= 40) return 'fair'
    return 'poor'
  }

  const getQualityScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-blue-600'
    if (score >= 40) return 'text-yellow-600'
    return 'text-red-600'
  }

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const stats = [
    { label: 'Líneas', value: results.line_count || 0, icon: FileText },
    { label: 'Errores', value: results.summary?.total_errors || 0, icon: XCircle },
    { label: 'Tamaño', value: `${Math.round((results.file_size || 0) / 1024)} KB`, icon: Database },
    { label: 'Performance', value: `${results.summary?.performance_score || 100}%`, icon: TrendingUp }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header with Download */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Resultados del Análisis
          </h2>
          <p className="text-gray-600 mt-1">
            Archivo: {results.filename}
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => onDownload(results, 'json')}
            className="btn-secondary text-sm"
          >
            <Download className="w-4 h-4 mr-2" />
            JSON
          </button>
          <button
            onClick={() => onDownload(results, 'html')}
            className="btn-secondary text-sm"
          >
            <Download className="w-4 h-4 mr-2" />
            HTML
          </button>
          <button
            onClick={() => onDownload(results, 'txt')}
            className="btn-secondary text-sm"
          >
            <Download className="w-4 h-4 mr-2" />
            TXT
          </button>
        </div>
      </div>

      {/* Quality Score */}
      <div className={`quality-score ${getQualityScoreClass(results.summary?.performance_score || 100)}`}>
        <div className={`text-6xl font-bold mb-2 ${getQualityScoreColor(results.summary?.performance_score || 100)}`}>
          {results.summary?.performance_score || 100}%
        </div>
        <div className="text-lg font-medium text-gray-700">
          Score de Rendimiento
        </div>
        <div className="text-sm text-gray-500 mt-2">
          Basado en análisis de rendimiento y mejores prácticas
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="card p-6 text-center"
            >
              <Icon className="w-8 h-8 text-primary-500 mx-auto mb-3" />
              <div className="text-2xl font-bold text-gray-900 mb-1">
                {stat.value}
              </div>
              <div className="text-sm text-gray-600">
                {stat.label}
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Errors and Warnings */}
      {results.analysis?.errors && results.analysis.errors.length > 0 && (
        <div className="card">
          <button
            onClick={() => toggleSection('errors')}
            className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
              <h3 className="text-lg font-semibold text-gray-900">
                Errores y Advertencias ({results.analysis.errors.length})
              </h3>
            </div>
            <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${expandedSections.errors ? 'rotate-180' : ''
              }`} />
          </button>

          {expandedSections.errors && (
            <div className="px-6 pb-6 space-y-3">
              {results.analysis.errors.map((error, index) => (
                <div
                  key={index}
                  className={`error-item ${error.severity === 'ERROR' ? 'error' : 'warning'}`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-0.5">
                      {error.severity === 'ERROR' ? (
                        <XCircle className="w-4 h-4 text-red-500" />
                      ) : (
                        <AlertTriangle className="w-4 h-4 text-yellow-500" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-sm font-medium text-gray-900">
                          Línea {error.line}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded-full ${error.severity === 'ERROR'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-yellow-100 text-yellow-700'
                          }`}>
                          {error.severity}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">
                        {error.message}
                      </p>
                      {error.code && (
                        <code className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded block">
                          {error.code}
                        </code>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Recommendations */}
      {results.summary?.recommendations && results.summary.recommendations.length > 0 && (
        <div className="card">
          <button
            onClick={() => toggleSection('recommendations')}
            className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <TrendingUp className="w-5 h-5 text-blue-500" />
              <h3 className="text-lg font-semibold text-gray-900">
                Recomendaciones ({results.summary.recommendations.length})
              </h3>
            </div>
            <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${expandedSections.recommendations ? 'rotate-180' : ''
              }`} />
          </button>

          {expandedSections.recommendations && (
            <div className="px-6 pb-6 space-y-4">
              {results.summary.recommendations.map((rec, index) => (
                <div key={index} className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center bg-blue-100`}>
                      <Info className={`w-4 h-4 text-blue-600`} />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-medium text-gray-900">
                        {rec.type || 'Recomendación'}
                      </h4>
                      <span className={`text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700`}>
                        INFO
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">
                      {rec.message}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Analysis Info */}
      <div className="card p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Clock className="w-5 h-5 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900">
            Información del Análisis
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Timestamp:</span>
            <span className="ml-2 text-gray-900">
              {new Date(results.analysis_timestamp).toLocaleString('es-ES')}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Versión del Analizador:</span>
            <span className="ml-2 text-gray-900">
              {results.analyzer_version}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Caracteres:</span>
            <span className="ml-2 text-gray-900">
              {results.statistics?.character_count?.toLocaleString() || 0}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Statements SQL:</span>
            <span className="ml-2 text-gray-900">
              {results.statistics?.sql_statements || 0}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default AnalysisResults
