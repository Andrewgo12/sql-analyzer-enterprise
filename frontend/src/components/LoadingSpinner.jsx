import React from 'react'
import { motion } from 'framer-motion'
import { Database } from 'lucide-react'

const LoadingSpinner = ({ size = 'default', message = 'Cargando...' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    default: 'w-8 h-8',
    large: 'w-12 h-12'
  }

  const containerClasses = {
    small: 'p-2',
    default: 'p-4',
    large: 'p-8'
  }

  return (
    <div className={`flex flex-col items-center justify-center ${containerClasses[size]}`}>
      {/* Animated Logo */}
      <motion.div
        animate={{ 
          rotate: 360,
          scale: [1, 1.1, 1]
        }}
        transition={{ 
          rotate: { duration: 2, repeat: Infinity, ease: "linear" },
          scale: { duration: 1, repeat: Infinity, ease: "easeInOut" }
        }}
        className={`${sizeClasses[size]} mb-3 text-primary-600`}
      >
        <Database className="w-full h-full" />
      </motion.div>

      {/* Loading Dots */}
      <div className="flex space-x-1 mb-2">
        {[0, 1, 2].map((index) => (
          <motion.div
            key={index}
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: index * 0.2,
              ease: "easeInOut"
            }}
            className="w-2 h-2 bg-primary-500 rounded-full"
          />
        ))}
      </div>

      {/* Message */}
      {message && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-sm text-gray-600 font-medium"
        >
          {message}
        </motion.p>
      )}
    </div>
  )
}

// Full screen loading component
export const FullScreenLoader = ({ message = 'Cargando SQL Analyzer Enterprise...' }) => {
  return (
    <div className="fixed inset-0 bg-white flex items-center justify-center z-50">
      <div className="text-center">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center">
            <Database className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            SQL Analyzer Enterprise
          </h2>
          <p className="text-gray-600 mb-8">
            {message}
          </p>
        </motion.div>

        <LoadingSpinner size="large" message="" />
      </div>
    </div>
  )
}

// Inline loading component
export const InlineLoader = ({ message = 'Procesando...' }) => {
  return (
    <div className="flex items-center justify-center py-8">
      <LoadingSpinner size="default" message={message} />
    </div>
  )
}

// Button loading state
export const ButtonLoader = () => {
  return (
    <div className="flex items-center space-x-2">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
      />
      <span>Procesando...</span>
    </div>
  )
}

export default LoadingSpinner
