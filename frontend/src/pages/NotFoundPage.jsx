import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Home, Search, AlertTriangle } from 'lucide-react'

const NotFoundPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center py-12">
      <div className="max-w-md mx-auto text-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          {/* 404 Icon */}
          <div className="mb-8">
            <motion.div
              animate={{ 
                rotate: [0, 10, -10, 0],
                scale: [1, 1.1, 1]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="w-24 h-24 bg-gradient-to-r from-red-500 to-pink-500 rounded-3xl flex items-center justify-center mx-auto mb-6"
            >
              <AlertTriangle className="w-12 h-12 text-white" />
            </motion.div>
            
            <h1 className="text-6xl font-bold text-gray-900 mb-2">
              404
            </h1>
          </div>

          {/* Error Message */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Página no encontrada
            </h2>
            <p className="text-gray-600 leading-relaxed">
              Lo sentimos, la página que estás buscando no existe o ha sido movida.
              Verifica la URL o regresa al inicio.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="space-y-4">
            <Link
              to="/"
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              <Home className="w-5 h-5" />
              <span>Volver al Inicio</span>
            </Link>
            
            <Link
              to="/analyze"
              className="btn-secondary w-full flex items-center justify-center space-x-2"
            >
              <Search className="w-5 h-5" />
              <span>Ir a Análisis</span>
            </Link>
          </div>

          {/* Help Text */}
          <div className="mt-8 p-4 bg-gray-50 rounded-xl">
            <h3 className="font-medium text-gray-900 mb-2">
              ¿Necesitas ayuda?
            </h3>
            <p className="text-sm text-gray-600">
              Si crees que esto es un error, verifica que la URL esté correcta
              o contacta al administrador del sistema.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default NotFoundPage
