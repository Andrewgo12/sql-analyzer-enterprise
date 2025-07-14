import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, File, X, AlertCircle, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'

const FileUpload = ({ onFileSelect, isLoading = false }) => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [error, setError] = useState(null)

  const validateFile = (file) => {
    const maxSize = 50 * 1024 * 1024 // 50MB
    const allowedTypes = ['.sql', '.txt']
    
    // Check file size
    if (file.size > maxSize) {
      return `Archivo demasiado grande (${(file.size / (1024 * 1024)).toFixed(1)}MB). Máximo: 50MB`
    }
    
    // Check file extension
    const extension = '.' + file.name.split('.').pop().toLowerCase()
    if (!allowedTypes.includes(extension)) {
      return `Tipo de archivo no válido. Permitidos: ${allowedTypes.join(', ')}`
    }
    
    return null
  }

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setError(null)
    
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0]
      setError('Archivo rechazado. Verifique el tipo y tamaño.')
      toast.error('Archivo rechazado')
      return
    }
    
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      const validationError = validateFile(file)
      
      if (validationError) {
        setError(validationError)
        toast.error(validationError)
        return
      }
      
      setSelectedFile(file)
      setError(null)
      onFileSelect(file)
      toast.success(`Archivo seleccionado: ${file.name}`)
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.sql', '.txt'],
      'application/sql': ['.sql']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
    disabled: isLoading
  })

  const removeFile = () => {
    setSelectedFile(null)
    setError(null)
    onFileSelect(null)
  }

  const getUploadZoneClass = () => {
    let baseClass = 'upload-zone cursor-pointer transition-all duration-200'
    
    if (isLoading) {
      baseClass += ' opacity-50 cursor-not-allowed'
    } else if (isDragReject || error) {
      baseClass += ' error'
    } else if (isDragActive) {
      baseClass += ' active'
    } else if (selectedFile) {
      baseClass += ' border-green-300 bg-green-50'
    }
    
    return baseClass
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="w-full">
      <div {...getRootProps()} className={getUploadZoneClass()}>
        <input {...getInputProps()} />
        
        <AnimatePresence mode="wait">
          {selectedFile ? (
            <motion.div
              key="file-selected"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="flex items-center justify-between w-full"
            >
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-green-100 rounded-xl">
                  <File className="w-6 h-6 text-green-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {selectedFile.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      removeFile()
                    }}
                    className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                    disabled={isLoading}
                  >
                    <X className="w-4 h-4 text-gray-400" />
                  </button>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="upload-prompt"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-center"
            >
              <div className="mb-4">
                <Upload className={`w-12 h-12 mx-auto ${
                  isDragActive ? 'text-primary-500' : 
                  error ? 'text-red-500' : 'text-gray-400'
                }`} />
              </div>
              
              <div className="mb-2">
                <p className={`text-lg font-medium ${
                  isDragActive ? 'text-primary-700' : 
                  error ? 'text-red-700' : 'text-gray-900'
                }`}>
                  {isDragActive 
                    ? 'Suelta el archivo aquí' 
                    : 'Arrastra tu archivo SQL aquí'
                  }
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  o haz clic para seleccionar
                </p>
              </div>
              
              <div className="text-xs text-gray-400 space-y-1">
                <p>Formatos soportados: .sql, .txt</p>
                <p>Tamaño máximo: 50MB</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Error Message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3"
          >
            <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-lg border border-red-200">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <p className="text-sm">{error}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading State */}
      {isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 flex items-center justify-center space-x-2 text-primary-600"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
          />
          <span className="text-sm font-medium">Procesando archivo...</span>
        </motion.div>
      )}
    </div>
  )
}

export default FileUpload
