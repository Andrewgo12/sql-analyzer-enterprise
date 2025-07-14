import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Database,
  Shield,
  Download,
  Globe,
  Bug,
  MessageSquare,
  TrendingUp,
  Play,
  Info
} from 'lucide-react'

const HomePage = () => {
  const features = [
    {
      icon: Bug,
      title: 'Detección de Errores',
      description: 'Identifica errores de sintaxis, lógica y rendimiento automáticamente'
    },
    {
      icon: MessageSquare,
      title: 'Comentarios Inteligentes',
      description: 'Agrega comentarios explicativos automáticamente en español'
    },
    {
      icon: Shield,
      title: 'Análisis de Seguridad',
      description: 'Detecta vulnerabilidades y problemas de seguridad en SQL'
    },
    {
      icon: TrendingUp,
      title: 'Optimización',
      description: 'Sugerencias para mejorar el rendimiento de consultas'
    },
    {
      icon: Download,
      title: 'Múltiples Formatos',
      description: 'Exporta resultados en JSON, HTML, CSV y más formatos'
    },
    {
      icon: Globe,
      title: 'Interfaz en Español',
      description: 'Completamente localizado para usuarios hispanohablantes'
    }
  ]

  const stats = [
    { number: '99.9%', label: 'Precisión' },
    { number: '50MB', label: 'Archivos Grandes' },
    { number: '6+', label: 'Formatos' },
    { number: '0', label: 'Errores Sistema' }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="hero-gradient text-white py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="mb-8"
            >
              <div className="inline-flex items-center justify-center w-20 h-20 bg-white/20 rounded-3xl backdrop-blur-sm mb-8">
                <Database className="w-10 h-10 text-white" />
              </div>

              <h1 className="heading-xl text-white mb-6">
                SQL Analyzer Enterprise
              </h1>

              <p className="text-xl lg:text-2xl text-white/90 mb-8 max-w-3xl mx-auto leading-relaxed">
                Herramienta profesional de análisis SQL para detectar errores, agregar comentarios
                y optimizar sus scripts de base de datos con precisión de nivel empresarial.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <Link
                to="/analyze"
                className="btn-primary bg-white text-primary-600 hover:bg-gray-50 flex items-center space-x-2 text-lg px-8 py-4"
              >
                <Play className="w-5 h-5" />
                <span>Iniciar Análisis</span>
              </Link>

              <button className="btn-secondary bg-white/10 text-white border-white/20 hover:bg-white/20 flex items-center space-x-2 text-lg px-8 py-4">
                <Info className="w-5 h-5" />
                <span>Más Información</span>
              </button>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="heading-lg text-gray-900 mb-4">
              Características Principales
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Potentes herramientas de análisis SQL diseñadas para desarrolladores
              y administradores de bases de datos profesionales.
            </p>
          </motion.div>

          <div className="feature-grid">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="card-interactive p-8 text-center group"
                >
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-200">
                    <Icon className="w-8 h-8 text-white" />
                  </div>

                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    {feature.title}
                  </h3>

                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </motion.div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="stats-grid">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="text-4xl lg:text-5xl font-bold text-gradient mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-600 font-medium">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="heading-lg text-gray-900 mb-6">
              ¿Listo para optimizar tu SQL?
            </h2>

            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Comienza a analizar tus archivos SQL ahora mismo y descubre
              cómo mejorar la calidad y rendimiento de tus consultas.
            </p>

            <Link
              to="/analyze"
              className="btn-primary text-lg px-8 py-4 inline-flex items-center space-x-2"
            >
              <Database className="w-5 h-5" />
              <span>Comenzar Análisis</span>
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
