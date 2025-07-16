import React, { useState } from 'react';
import {
  Settings,
  Database,
  Shield,
  Zap,
  FileText,
  AlertTriangle,
  CheckCircle,
  Info,
  X
} from 'lucide-react';
import { Modal, Button, Input, Dropdown, Card } from '../ui';

const AnalysisOptionsModal = ({ isOpen, onClose, onAnalyze, initialOptions = {} }) => {
  const [options, setOptions] = useState({
    // General options
    analysisType: 'comprehensive',
    includeComments: true,
    autoFix: false,
    
    // Database options
    databaseEngine: 'mysql',
    strictMode: false,
    checkConstraints: true,
    
    // Security options
    securityScan: true,
    sqlInjectionCheck: true,
    privilegeAnalysis: false,
    
    // Performance options
    performanceAnalysis: true,
    indexSuggestions: true,
    queryOptimization: true,
    
    // Output options
    generateReport: true,
    includeMetadata: true,
    exportFormat: 'json',
    
    ...initialOptions
  });

  const [activeTab, setActiveTab] = useState('general');

  const tabs = [
    { id: 'general', label: 'General', icon: Settings },
    { id: 'database', label: 'Base de Datos', icon: Database },
    { id: 'security', label: 'Seguridad', icon: Shield },
    { id: 'performance', label: 'Rendimiento', icon: Zap },
    { id: 'output', label: 'Salida', icon: FileText }
  ];

  const analysisTypeOptions = [
    { value: 'basic', label: 'Análisis Básico' },
    { value: 'comprehensive', label: 'Análisis Completo' },
    { value: 'security', label: 'Enfoque en Seguridad' },
    { value: 'performance', label: 'Enfoque en Rendimiento' }
  ];

  const databaseEngineOptions = [
    { value: 'mysql', label: 'MySQL' },
    { value: 'postgresql', label: 'PostgreSQL' },
    { value: 'oracle', label: 'Oracle' },
    { value: 'sqlserver', label: 'SQL Server' },
    { value: 'sqlite', label: 'SQLite' }
  ];

  const exportFormatOptions = [
    { value: 'json', label: 'JSON' },
    { value: 'html', label: 'HTML' },
    { value: 'pdf', label: 'PDF' },
    { value: 'csv', label: 'CSV' },
    { value: 'xml', label: 'XML' }
  ];

  const handleOptionChange = (key, value) => {
    setOptions(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleAnalyze = () => {
    onAnalyze?.(options);
    onClose?.();
  };

  const renderGeneralTab = () => (
    <div className="options-section">
      <div className="option-group">
        <label className="option-label">Tipo de Análisis</label>
        <Dropdown
          options={analysisTypeOptions}
          value={options.analysisType}
          onChange={(value) => handleOptionChange('analysisType', value)}
        />
        <p className="option-description">
          Selecciona el nivel de profundidad del análisis
        </p>
      </div>

      <div className="option-group">
        <label className="option-checkbox">
          <input
            type="checkbox"
            checked={options.includeComments}
            onChange={(e) => handleOptionChange('includeComments', e.target.checked)}
          />
          <span>Incluir comentarios explicativos</span>
        </label>
        <p className="option-description">
          Agrega comentarios detallados en el código SQL analizado
        </p>
      </div>

      <div className="option-group">
        <label className="option-checkbox">
          <input
            type="checkbox"
            checked={options.autoFix}
            onChange={(e) => handleOptionChange('autoFix', e.target.checked)}
          />
          <span>Corrección automática</span>
        </label>
        <p className="option-description">
          Intenta corregir automáticamente errores comunes encontrados
        </p>
      </div>
    </div>
  );

  const renderDatabaseTab = () => (
    <div className="options-section">
      <div className="option-group">
        <label className="option-label">Motor de Base de Datos</label>
        <Dropdown
          options={databaseEngineOptions}
          value={options.databaseEngine}
          onChange={(value) => handleOptionChange('databaseEngine', value)}
        />
        <p className="option-description">
          Especifica el motor de base de datos para análisis específico
        </p>
      </div>

      <div className="option-group">
        <label className="option-checkbox">
          <input
            type="checkbox"
            checked={options.strictMode}
            onChange={(e) => handleOptionChange('strictMode', e.target.checked)}
          />
          <span>Modo estricto</span>
        </label>
        <p className="option-description">
          Aplica reglas de validación más estrictas
        </p>
      </div>

      <div className="option-group">
        <label className="option-checkbox">
          <input
            type="checkbox"
            checked={options.checkConstraints}
            onChange={(e) => handleOptionChange('checkConstraints', e.target.checked)}
          />
          <span>Verificar restricciones</span>
        </label>
        <p className="option-description">
          Analiza restricciones de integridad y claves foráneas
        </p>
      </div>
    </div>
  );

  const renderSecurityTab = () => (
    <div className="options-section">
      <div className="option-group">
        <label className="option-checkbox">
          <input
            type="checkbox"
            checked={options.securityScan}
            onChange={(e) => handleOptionChange('securityScan', e.target.checked)}
          />
          <span>Escaneo de seguridad</span>
        </label>
        <p className="option-description">
          Realiza un análisis completo de vulnerabilidades de seguridad
        </p>
      </div>

      <div className="option-group">
        <label className="option-checkbox">
          <input
            type="checkbox"
            checked={options.sqlInjectionCheck}
            onChange={(e) => handleOptionChange('sqlInjectionCheck', e.target.checked)}
          />
          <span>Detección de inyección SQL</span>
        </label>
        <p className="option-description">
          Identifica posibles vulnerabilidades de inyección SQL
        </p>
      </div>

      <div className="option-group">
        <label className="option-checkbox">
          <input
            type="checkbox"
            checked={options.privilegeAnalysis}
            onChange={(e) => handleOptionChange('privilegeAnalysis', e.target.checked)}
          />
          <span>Análisis de privilegios</span>
        </label>
        <p className="option-description">
          Evalúa los permisos y privilegios requeridos
        </p>
      </div>
    </div>
  );

  const renderPerformanceTab = () => (
    <div className="options-section">
      <div className="option-group">
        <label className="option-checkbox">
          <input
            type="checkbox"
            checked={options.performanceAnalysis}
            onChange={(e) => handleOptionChange('performanceAnalysis', e.target.checked)}
          />
          <span>Análisis de rendimiento</span>
        </label>
        <p className="option-description">
          Evalúa el rendimiento y eficiencia de las consultas
        </p>
      </div>

      <div className="option-group">
        <label className="option-checkbox">
          <input
            type="checkbox"
            checked={options.indexSuggestions}
            onChange={(e) => handleOptionChange('indexSuggestions', e.target.checked)}
          />
          <span>Sugerencias de índices</span>
        </label>
        <p className="option-description">
          Recomienda índices para mejorar el rendimiento
        </p>
      </div>

      <div className="option-group">
        <label className="option-checkbox">
          <input
            type="checkbox"
            checked={options.queryOptimization}
            onChange={(e) => handleOptionChange('queryOptimization', e.target.checked)}
          />
          <span>Optimización de consultas</span>
        </label>
        <p className="option-description">
          Sugiere mejoras para optimizar las consultas SQL
        </p>
      </div>
    </div>
  );

  const renderOutputTab = () => (
    <div className="options-section">
      <div className="option-group">
        <label className="option-checkbox">
          <input
            type="checkbox"
            checked={options.generateReport}
            onChange={(e) => handleOptionChange('generateReport', e.target.checked)}
          />
          <span>Generar reporte</span>
        </label>
        <p className="option-description">
          Crea un reporte detallado del análisis realizado
        </p>
      </div>

      <div className="option-group">
        <label className="option-checkbox">
          <input
            type="checkbox"
            checked={options.includeMetadata}
            onChange={(e) => handleOptionChange('includeMetadata', e.target.checked)}
          />
          <span>Incluir metadatos</span>
        </label>
        <p className="option-description">
          Agrega información adicional sobre el análisis
        </p>
      </div>

      <div className="option-group">
        <label className="option-label">Formato de exportación</label>
        <Dropdown
          options={exportFormatOptions}
          value={options.exportFormat}
          onChange={(value) => handleOptionChange('exportFormat', value)}
        />
        <p className="option-description">
          Formato del archivo de salida del análisis
        </p>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return renderGeneralTab();
      case 'database':
        return renderDatabaseTab();
      case 'security':
        return renderSecurityTab();
      case 'performance':
        return renderPerformanceTab();
      case 'output':
        return renderOutputTab();
      default:
        return renderGeneralTab();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Opciones de Análisis"
      size="large"
      className="analysis-options-modal"
    >
      <div className="modal-tabs">
        <div className="tabs-nav">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon size={16} />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="tab-content">
          {renderTabContent()}
        </div>
      </div>

      <Modal.Footer>
        <Button variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <Button onClick={handleAnalyze}>
          <Zap size={16} />
          Iniciar Análisis
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default AnalysisOptionsModal;
