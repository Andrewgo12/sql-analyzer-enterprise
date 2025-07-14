import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Database, Home, Search, Menu, X } from 'lucide-react'

const Layout = ({ children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const location = useLocation()

  const navigation = [
    { name: 'Inicio', href: '/', icon: Home },
    { name: 'Analizar', href: '/analyze', icon: Search },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 backdrop-blur-sm bg-white/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link 
              to="/" 
              className="flex items-center space-x-3 group"
            >
              <div className="p-2 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl group-hover:scale-105 transition-transform duration-200">
                <Database className="h-6 w-6 text-white" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold text-gray-900">
                  SQL Analyzer
                </h1>
                <p className="text-xs text-gray-500 -mt-1">Enterprise</p>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-1">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`
                      flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200
                      ${isActive(item.href)
                        ? 'bg-primary-50 text-primary-700 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-colors duration-200"
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-gray-200 bg-white"
          >
            <div className="px-4 py-3 space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`
                      flex items-center space-x-3 px-3 py-3 rounded-xl text-base font-medium transition-all duration-200
                      ${isActive(item.href)
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </div>
          </motion.div>
        )}
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Brand */}
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl">
                  <Database className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">SQL Analyzer Enterprise</h3>
                  <p className="text-sm text-gray-500">Versión 2.0</p>
                </div>
              </div>
              <p className="text-sm text-gray-600 max-w-md">
                Herramienta profesional de análisis SQL con interfaz moderna, 
                diseñada para detectar errores y optimizar bases de datos.
              </p>
            </div>

            {/* Features */}
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900">Características</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                  <span>Detección de errores avanzada</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                  <span>Análisis de rendimiento</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                  <span>Múltiples formatos de exportación</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                  <span>Interfaz responsive</span>
                </li>
              </ul>
            </div>

            {/* Technical */}
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900">Tecnología</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>React 18 + Vite</li>
                <li>Tailwind CSS</li>
                <li>Python Flask Backend</li>
                <li>Arquitectura moderna</li>
              </ul>
            </div>
          </div>

          {/* Bottom */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
              <p className="text-sm text-gray-500">
                © 2024 SQL Analyzer Enterprise. Todos los derechos reservados.
              </p>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span>Hecho con ❤️ para desarrolladores</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout
