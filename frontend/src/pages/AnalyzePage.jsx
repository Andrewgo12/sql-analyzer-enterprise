import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Upload, Zap } from 'lucide-react'
import toast from 'react-hot-toast'

// Components
import FileUpload from '../components/FileUpload'
import AnalysisResults from '../components/AnalysisResults'
import { InlineLoader } from '../components/LoadingSpinner'

// Hooks
import useFileUpload from '../hooks/useFileUpload'
import useAnalysis from '../hooks/useAnalysis'

// Utils
import { downloadResult } from '../utils/api'

const AnalyzePage = () => {
  const {
    selectedFile,
    selectFile,
    clearFile,
    isUploading
  } = useFileUpload()

  const {
    isAnalyzing,
    analysisResults,
    analysisProgress,
    startAnalysis,
    clearResults
  } = useAnalysis()

  const handleFileSelect = (file) => {
    if (selectFile(file)) {
      clearResults()
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile) {
      toast.error('Por favor selecciona un archivo SQL')
      return
    }

    await startAnalysis(selectedFile)
  }

  const handleDownload = async (format) => {
    try {
      await downloadResult(format)
      toast.success(`Descarga iniciada en formato ${format.toUpperCase()}`)
    } catch (error) {
      console.error('Error downloading:', error)
      toast.error('Error en la descarga')
    }
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl mb-6">
            <Search className="w-8 h-8 text-white" />
          </div>

          <h1 className="heading-lg text-gray-900 mb-4">
            Análisis de Archivos SQL
          </h1>

          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Sube tu archivo SQL y obtén un análisis completo con detección de errores,
            recomendaciones de optimización y reportes detallados.
          </p>
        </motion.div>

        {/* Upload Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-8 mb-8"
        >
          <div className="flex items-center space-x-3 mb-6">
            <Upload className="w-6 h-6 text-primary-500" />
            <h2 className="text-xl font-semibold text-gray-900">
              Subir Archivo SQL
            </h2>
          </div>

          <FileUpload
            onFileSelect={handleFileSelect}
            isLoading={isAnalyzing || isUploading}
          />

          {selectedFile && !isAnalyzing && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-6 pt-6 border-t border-gray-200"
            >
              <button
                onClick={handleAnalyze}
                className="btn-primary w-full sm:w-auto flex items-center justify-center space-x-2"
              >
                <Zap className="w-5 h-5" />
                <span>Analizar Archivo</span>
              </button>
            </motion.div>
          )}
        </motion.div>

        {/* Progress Section */}
        <AnimatePresence>
          {isAnalyzing && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="card p-8 mb-8"
            >
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 rounded-xl mb-4">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  >
                    <Zap className="w-6 h-6 text-primary-600" />
                  </motion.div>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Analizando archivo...
                </h3>

                <p className="text-gray-600 mb-6">
                  Procesando {selectedFile?.name}
                </p>

                <div className="max-w-md mx-auto">
                  <div className="progress-bar mb-2">
                    <motion.div
                      className="progress-fill"
                      initial={{ width: 0 }}
                      animate={{ width: `${analysisProgress}%` }}
                      transition={{ duration: 0.3 }}
                    />
                  </div>
                  <p className="text-sm text-gray-500">
                    {Math.round(analysisProgress)}% completado
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results Section */}
        <AnimatePresence>
          {analysisResults && !isAnalyzing && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <AnalysisResults
                results={analysisResults}
                onDownload={handleDownload}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Help Section */}
        {!selectedFile && !isAnalyzing && !analysisResults && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card p-8 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              ¿Cómo funciona?
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Upload className="w-6 h-6 text-blue-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-2">1. Sube tu archivo</h4>
                <p className="text-sm text-gray-600">
                  Arrastra o selecciona tu archivo SQL (.sql o .txt)
                </p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Zap className="w-6 h-6 text-blue-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-2">2. Análisis automático</h4>
                <p className="text-sm text-gray-600">
                  Nuestro sistema analiza errores, rendimiento y seguridad
                </p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Search className="w-6 h-6 text-blue-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-2">3. Resultados detallados</h4>
                <p className="text-sm text-gray-600">
                  Obtén reportes completos y recomendaciones de mejora
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default AnalyzePage
