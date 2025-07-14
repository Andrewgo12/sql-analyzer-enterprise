import { useState, useCallback } from 'react'
import toast from 'react-hot-toast'

export const useFileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState(null)

  const validateFile = useCallback((file) => {
    const maxSize = 50 * 1024 * 1024 // 50MB
    const allowedTypes = ['.sql', '.txt']
    
    if (!file) {
      return 'No se seleccionó archivo'
    }

    if (file.size > maxSize) {
      return `Archivo demasiado grande (${(file.size / (1024 * 1024)).toFixed(1)}MB). Máximo: 50MB`
    }

    const extension = '.' + file.name.split('.').pop().toLowerCase()
    if (!allowedTypes.includes(extension)) {
      return `Tipo de archivo no válido. Permitidos: ${allowedTypes.join(', ')}`
    }

    return null
  }, [])

  const selectFile = useCallback((file) => {
    const validationError = validateFile(file)
    
    if (validationError) {
      setError(validationError)
      toast.error(validationError)
      return false
    }

    setSelectedFile(file)
    setError(null)
    toast.success(`Archivo seleccionado: ${file.name}`)
    return true
  }, [validateFile])

  const clearFile = useCallback(() => {
    setSelectedFile(null)
    setError(null)
    setUploadProgress(0)
  }, [])

  const resetUpload = useCallback(() => {
    setIsUploading(false)
    setUploadProgress(0)
    setError(null)
  }, [])

  return {
    selectedFile,
    isUploading,
    uploadProgress,
    error,
    selectFile,
    clearFile,
    resetUpload,
    setIsUploading,
    setUploadProgress,
    setError
  }
}

export default useFileUpload
