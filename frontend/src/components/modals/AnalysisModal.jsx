import React, { useState } from 'react';
import { 
  X, 
  Settings, 
  Database, 
  Zap, 
  Shield, 
  FileText,
  CheckSquare,
  Square,
  Play,
  Info
} from 'lucide-react';

const AnalysisModal = ({ isOpen, onClose, onAnalyze }) => {
  const [settings, setSettings] = useState({
    databaseEngine: 'auto_detect',
    analysisTypes: {
      syntax: true,
      semantic: true,
      performance: true,
      security: true,
      schema: false,
      dataQuality: false
    },
    options: {
      includeRecommendations: true,
      generateCorrectedSQL: true,
      detailedReporting: true,
      includeSchemaAnalysis: false
    },
    performance: {
      checkSelectStar: true,
      checkMissingIndexes: true,
      checkSlowQueries: true,
      checkJoinOptimization: true
    },
    security: {
      checkSQLInjection: true,
      checkPrivilegeEscalation: true,
      checkDataExposure: true,
      checkWeakAuthentication: false
    }
  });

  const databaseEngines = [
    { value: 'auto_detect', label: 'Auto-detectar', description: 'Detectar automáticamente el motor de BD' },
    { value: 'mysql', label: 'MySQL', description: 'MySQL 5.7+' },
    { value: 'postgresql', label: 'PostgreSQL', description: 'PostgreSQL 10+' },
    { value: 'sql_server', label: 'SQL Server', description: 'Microsoft SQL Server 2016+' },
    { value: 'oracle', label: 'Oracle', description: 'Oracle Database 12c+' },
    { value: 'sqlite', label: 'SQLite', description: 'SQLite 3.x' },
    { value: 'mongodb', label: 'MongoDB', description: 'MongoDB 4.0+' },
    { value: 'bigquery', label: 'BigQuery', description: 'Google BigQuery' },
    { value: 'snowflake', label: 'Snowflake', description: 'Snowflake Data Warehouse' },
    { value: 'clickhouse', label: 'ClickHouse', description: 'ClickHouse OLAP' }
  ];

  const analysisTypeInfo = {
    syntax: {
      icon: <FileText size={16} />,
      title: 'Análisis de Sintaxis',
      description: 'Detecta errores de sintaxis SQL y problemas de formato'
    },
    semantic: {
      icon: <Database size={16} />,
      title: 'Análisis Semántico',
      description: 'Verifica la lógica y coherencia de las consultas'
    },
    performance: {
      icon: <Zap size={16} />,
      title: 'Análisis de Rendimiento',
      description: 'Identifica problemas de rendimiento y optimizaciones'
    },
    security: {
      icon: <Shield size={16} />,
      title: 'Análisis de Seguridad',
      description: 'Detecta vulnerabilidades y riesgos de seguridad'
    },
    schema: {
      icon: <Database size={16} />,
      title: 'Análisis de Esquema',
      description: 'Analiza la estructura de la base de datos'
    },
    dataQuality: {
      icon: <CheckSquare size={16} />,
      title: 'Calidad de Datos',
      description: 'Evalúa la integridad y calidad de los datos'
    }
  };

  const handleAnalysisTypeChange = (type) => {
    setSettings(prev => ({
      ...prev,
      analysisTypes: {
        ...prev.analysisTypes,
        [type]: !prev.analysisTypes[type]
      }
    }));
  };

  const handleOptionChange = (category, option) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [option]: !prev[category][option]
      }
    }));
  };

  const handleDatabaseEngineChange = (e) => {
    setSettings(prev => ({
      ...prev,
      databaseEngine: e.target.value
    }));
  };

  const handleAnalyze = () => {
    // Convert settings to the format expected by the backend
    const analysisConfig = {
      database_engine: settings.databaseEngine,
      analysis_types: Object.keys(settings.analysisTypes)
        .filter(type => settings.analysisTypes[type])
        .join(','),
      options: settings.options,
      performance_checks: settings.performance,
      security_checks: settings.security
    };

    onAnalyze(analysisConfig);
  };

  const getSelectedAnalysisCount = () => {
    return Object.values(settings.analysisTypes).filter(Boolean).length;
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container large">
        <div className="modal-header">
          <div className="modal-title">
            <Settings size={20} />
            <span>Configuración de Análisis</span>
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-content">
          {/* Database Engine Selection */}
          <div className="settings-section">
            <h3>Motor de Base de Datos</h3>
            <div className="database-engine-selector">
              <select 
                value={settings.databaseEngine}
                onChange={handleDatabaseEngineChange}
                className="engine-select"
              >
                {databaseEngines.map(engine => (
                  <option key={engine.value} value={engine.value}>
                    {engine.label}
                  </option>
                ))}
              </select>
              <div className="engine-description">
                {databaseEngines.find(e => e.value === settings.databaseEngine)?.description}
              </div>
            </div>
          </div>

          {/* Analysis Types */}
          <div className="settings-section">
            <h3>Tipos de Análisis ({getSelectedAnalysisCount()} seleccionados)</h3>
            <div className="analysis-types-grid">
              {Object.entries(analysisTypeInfo).map(([type, info]) => (
                <div 
                  key={type}
                  className={`analysis-type-card ${settings.analysisTypes[type] ? 'selected' : ''}`}
                  onClick={() => handleAnalysisTypeChange(type)}
                >
                  <div className="card-header">
                    <div className="card-icon">
                      {info.icon}
                    </div>
                    <div className="card-checkbox">
                      {settings.analysisTypes[type] ? (
                        <CheckSquare size={16} />
                      ) : (
                        <Square size={16} />
                      )}
                    </div>
                  </div>
                  <div className="card-content">
                    <h4>{info.title}</h4>
                    <p>{info.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* General Options */}
          <div className="settings-section">
            <h3>Opciones Generales</h3>
            <div className="options-grid">
              <label className="option-item">
                <input
                  type="checkbox"
                  checked={settings.options.includeRecommendations}
                  onChange={() => handleOptionChange('options', 'includeRecommendations')}
                />
                <span className="option-label">Incluir recomendaciones</span>
                <span className="option-description">Generar sugerencias de mejora</span>
              </label>

              <label className="option-item">
                <input
                  type="checkbox"
                  checked={settings.options.generateCorrectedSQL}
                  onChange={() => handleOptionChange('options', 'generateCorrectedSQL')}
                />
                <span className="option-label">Generar SQL corregido</span>
                <span className="option-description">Crear versión optimizada del código</span>
              </label>

              <label className="option-item">
                <input
                  type="checkbox"
                  checked={settings.options.detailedReporting}
                  onChange={() => handleOptionChange('options', 'detailedReporting')}
                />
                <span className="option-label">Reporte detallado</span>
                <span className="option-description">Incluir información técnica completa</span>
              </label>

              <label className="option-item">
                <input
                  type="checkbox"
                  checked={settings.options.includeSchemaAnalysis}
                  onChange={() => handleOptionChange('options', 'includeSchemaAnalysis')}
                />
                <span className="option-label">Análisis de esquema</span>
                <span className="option-description">Analizar estructura de tablas y relaciones</span>
              </label>
            </div>
          </div>

          {/* Performance Options */}
          {settings.analysisTypes.performance && (
            <div className="settings-section">
              <h3>Opciones de Rendimiento</h3>
              <div className="options-grid">
                <label className="option-item">
                  <input
                    type="checkbox"
                    checked={settings.performance.checkSelectStar}
                    onChange={() => handleOptionChange('performance', 'checkSelectStar')}
                  />
                  <span className="option-label">Detectar SELECT *</span>
                  <span className="option-description">Identificar consultas con SELECT *</span>
                </label>

                <label className="option-item">
                  <input
                    type="checkbox"
                    checked={settings.performance.checkMissingIndexes}
                    onChange={() => handleOptionChange('performance', 'checkMissingIndexes')}
                  />
                  <span className="option-label">Índices faltantes</span>
                  <span className="option-description">Sugerir índices para mejorar rendimiento</span>
                </label>

                <label className="option-item">
                  <input
                    type="checkbox"
                    checked={settings.performance.checkSlowQueries}
                    onChange={() => handleOptionChange('performance', 'checkSlowQueries')}
                  />
                  <span className="option-label">Consultas lentas</span>
                  <span className="option-description">Identificar consultas potencialmente lentas</span>
                </label>

                <label className="option-item">
                  <input
                    type="checkbox"
                    checked={settings.performance.checkJoinOptimization}
                    onChange={() => handleOptionChange('performance', 'checkJoinOptimization')}
                  />
                  <span className="option-label">Optimización de JOINs</span>
                  <span className="option-description">Analizar eficiencia de las uniones</span>
                </label>
              </div>
            </div>
          )}

          {/* Security Options */}
          {settings.analysisTypes.security && (
            <div className="settings-section">
              <h3>Opciones de Seguridad</h3>
              <div className="options-grid">
                <label className="option-item">
                  <input
                    type="checkbox"
                    checked={settings.security.checkSQLInjection}
                    onChange={() => handleOptionChange('security', 'checkSQLInjection')}
                  />
                  <span className="option-label">Inyección SQL</span>
                  <span className="option-description">Detectar vulnerabilidades de inyección</span>
                </label>

                <label className="option-item">
                  <input
                    type="checkbox"
                    checked={settings.security.checkPrivilegeEscalation}
                    onChange={() => handleOptionChange('security', 'checkPrivilegeEscalation')}
                  />
                  <span className="option-label">Escalación de privilegios</span>
                  <span className="option-description">Identificar riesgos de permisos</span>
                </label>

                <label className="option-item">
                  <input
                    type="checkbox"
                    checked={settings.security.checkDataExposure}
                    onChange={() => handleOptionChange('security', 'checkDataExposure')}
                  />
                  <span className="option-label">Exposición de datos</span>
                  <span className="option-description">Detectar posible filtración de información</span>
                </label>

                <label className="option-item">
                  <input
                    type="checkbox"
                    checked={settings.security.checkWeakAuthentication}
                    onChange={() => handleOptionChange('security', 'checkWeakAuthentication')}
                  />
                  <span className="option-label">Autenticación débil</span>
                  <span className="option-description">Verificar configuraciones de seguridad</span>
                </label>
              </div>
            </div>
          )}

          {/* Analysis Summary */}
          <div className="analysis-summary">
            <div className="summary-info">
              <Info size={16} />
              <span>
                Se ejecutarán {getSelectedAnalysisCount()} tipos de análisis en el motor {' '}
                {databaseEngines.find(e => e.value === settings.databaseEngine)?.label}
              </span>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Cancelar
          </button>
          <button 
            type="button" 
            className="btn-primary"
            onClick={handleAnalyze}
            disabled={getSelectedAnalysisCount() === 0}
          >
            <Play size={16} />
            Ejecutar Análisis
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnalysisModal;
