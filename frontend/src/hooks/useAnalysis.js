import { useState, useCallback } from 'react'
import { analyzeFile } from '../utils/api'
import toast from 'react-hot-toast'

export const useAnalysis = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState(null)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [analysisError, setAnalysisError] = useState(null)

  const startAnalysis = useCallback(async (file) => {
    if (!file) {
      toast.error('No se proporcionó archivo para analizar')
      return false
    }

    setIsAnalyzing(true)
    setAnalysisProgress(0)
    setAnalysisError(null)
    setAnalysisResults(null)

    // Simulate progress updates
    const progressInterval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + Math.random() * 15
      })
    }, 300)

    try {
      const results = await analyzeFile(file)

      clearInterval(progressInterval)
      setAnalysisProgress(100)

      // Small delay for better UX
      setTimeout(() => {
        setAnalysisResults(results)
        setIsAnalyzing(false)
        setAnalysisProgress(0)

        // Check if analysis was successful based on the new response format
        if (results && results.filename) {
          const errorCount = results.summary?.total_errors || 0
          if (errorCount === 0) {
            toast.success('Análisis completado exitosamente - Sin errores detectados')
          } else {
            toast.success(`Análisis completado - ${errorCount} problema(s) detectado(s)`)
          }
        } else {
          toast.error('Error en el análisis: ' + (results.error || 'Error desconocido'))
          setAnalysisError(results.error || 'Error desconocido')
        }
      }, 500)

      return true

    } catch (error) {
      clearInterval(progressInterval)
      setIsAnalyzing(false)
      setAnalysisProgress(0)

      const errorMessage = error.message || 'Error procesando el archivo'
      setAnalysisError(errorMessage)
      toast.error(errorMessage)

      console.error('Analysis error:', error)
      return false
    }
  }, [])

  const clearResults = useCallback(() => {
    setAnalysisResults(null)
    setAnalysisError(null)
    setAnalysisProgress(0)
  }, [])

  const resetAnalysis = useCallback(() => {
    setIsAnalyzing(false)
    setAnalysisResults(null)
    setAnalysisProgress(0)
    setAnalysisError(null)
  }, [])

  return {
    isAnalyzing,
    analysisResults,
    analysisProgress,
    analysisError,
    startAnalysis,
    clearResults,
    resetAnalysis
  }
}

export default useAnalysis
