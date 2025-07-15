import React, { useState } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Download, 
  Settings, 
  BarChart3, 
  Shield, 
  Zap, 
  AlertTriangle,
  CheckCircle,
  Info,
  FileText,
  Database,
  TrendingUp
} from 'lucide-react';

const RightPanel = ({ 
  collapsed, 
  onToggle, 
  currentAnalysis, 
  onExport, 
  onAnalysisSettings 
}) => {
  const [activeTab, setActiveTab] = useState('summary');

  const getSeverityIcon = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="severity-icon error" size={16} />;
      case 'medium':
        return <AlertTriangle className="severity-icon warning" size={16} />;
      case 'low':
        return <Info className="severity-icon info" size={16} />;
      default:
        return <CheckCircle className="severity-icon success" size={16} />;
    }
  };

  const formatScore = (score) => {
    if (score >= 90) return { value: score, level: 'excellent', color: 'success' };
    if (score >= 75) return { value: score, level: 'good', color: 'info' };
    if (score >= 60) return { value: score, level: 'fair', color: 'warning' };
    return { value: score, level: 'poor', color: 'error' };
  };

  return (
    <div className={`right-panel ${collapsed ? 'collapsed' : ''}`}>
      {/* Panel Header */}
      <div className="panel-header">
        <div className="panel-title">
          {!collapsed && (
            <>
              <BarChart3 className="panel-icon" />
              <span>Análisis</span>
            </>
          )}
        </div>
        <button 
          className="panel-toggle"
          onClick={onToggle}
          title={collapsed ? 'Expandir panel' : 'Contraer panel'}
        >
          {collapsed ? <ChevronLeft /> : <ChevronRight />}
        </button>
      </div>

      {!collapsed && (
        <>
          {/* Tab Navigation */}
          <div className="panel-nav">
            <button 
              className={`nav-tab ${activeTab === 'summary' ? 'active' : ''}`}
              onClick={() => setActiveTab('summary')}
            >
              <BarChart3 size={14} />
              <span>Resumen</span>
            </button>
            <button 
              className={`nav-tab ${activeTab === 'details' ? 'active' : ''}`}
              onClick={() => setActiveTab('details')}
            >
              <FileText size={14} />
              <span>Detalles</span>
            </button>
            <button 
              className={`nav-tab ${activeTab === 'export' ? 'active' : ''}`}
              onClick={() => setActiveTab('export')}
            >
              <Download size={14} />
              <span>Exportar</span>
            </button>
          </div>

          {/* Panel Content */}
          <div className="panel-content">
            {!currentAnalysis ? (
              <div className="no-analysis">
                <BarChart3 className="no-analysis-icon" />
                <h3>Sin Análisis</h3>
                <p>Ejecuta un análisis para ver los resultados aquí</p>
              </div>
            ) : (
              <>
                {/* Summary Tab */}
                {activeTab === 'summary' && (
                  <div className="summary-tab">
                    <div className="summary-section">
                      <h4>Métricas Generales</h4>
                      
                      <div className="metric-card">
                        <div className="metric-header">
                          <AlertTriangle size={16} />
                          <span>Errores Detectados</span>
                        </div>
                        <div className="metric-value error">
                          {currentAnalysis.summary?.total_errors || 0}
                        </div>
                      </div>

                      <div className="metric-card">
                        <div className="metric-header">
                          <Zap size={16} />
                          <span>Rendimiento</span>
                        </div>
                        <div className={`metric-value ${formatScore(currentAnalysis.summary?.performance_score || 100).color}`}>
                          {currentAnalysis.summary?.performance_score || 100}%
                        </div>
                        <div className="metric-level">
                          {formatScore(currentAnalysis.summary?.performance_score || 100).level}
                        </div>
                      </div>

                      <div className="metric-card">
                        <div className="metric-header">
                          <Shield size={16} />
                          <span>Seguridad</span>
                        </div>
                        <div className={`metric-value ${formatScore(currentAnalysis.summary?.security_score || 100).color}`}>
                          {currentAnalysis.summary?.security_score || 100}%
                        </div>
                        <div className="metric-level">
                          {formatScore(currentAnalysis.summary?.security_score || 100).level}
                        </div>
                      </div>
                    </div>

                    {/* Recommendations */}
                    {currentAnalysis.summary?.recommendations && currentAnalysis.summary.recommendations.length > 0 && (
                      <div className="summary-section">
                        <h4>Recomendaciones</h4>
                        <div className="recommendations-list">
                          {currentAnalysis.summary.recommendations.slice(0, 3).map((rec, index) => (
                            <div key={index} className={`recommendation-item ${rec.priority || 'medium'}`}>
                              <div className="recommendation-header">
                                {getSeverityIcon(rec.priority)}
                                <span className="recommendation-title">{rec.title || rec.message}</span>
                              </div>
                              {rec.action && (
                                <div className="recommendation-action">
                                  {rec.action}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Quick Stats */}
                    <div className="summary-section">
                      <h4>Estadísticas</h4>
                      <div className="stats-grid">
                        <div className="stat-item">
                          <span className="stat-label">Líneas</span>
                          <span className="stat-value">{currentAnalysis.line_count || 0}</span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-label">Tamaño</span>
                          <span className="stat-value">{Math.round((currentAnalysis.file_size || 0) / 1024)}KB</span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-label">Motor DB</span>
                          <span className="stat-value">{currentAnalysis.database_engine || 'Auto'}</span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-label">Tiempo</span>
                          <span className="stat-value">{(currentAnalysis.processing_time || 0).toFixed(2)}s</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Details Tab */}
                {activeTab === 'details' && (
                  <div className="details-tab">
                    <div className="details-section">
                      <h4>Errores por Categoría</h4>
                      {currentAnalysis.analysis?.errors && currentAnalysis.analysis.errors.length > 0 ? (
                        <div className="error-categories">
                          {currentAnalysis.analysis.errors.slice(0, 5).map((error, index) => (
                            <div key={index} className="error-item">
                              <div className="error-header">
                                {getSeverityIcon(error.severity)}
                                <span className="error-category">{error.category}</span>
                              </div>
                              <div className="error-message">{error.message}</div>
                              {error.line && (
                                <div className="error-location">Línea {error.line}</div>
                              )}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="no-errors">
                          <CheckCircle className="success-icon" />
                          <span>No se encontraron errores</span>
                        </div>
                      )}
                    </div>

                    {/* Performance Issues */}
                    {currentAnalysis.analysis?.performance_issues && currentAnalysis.analysis.performance_issues.length > 0 && (
                      <div className="details-section">
                        <h4>Problemas de Rendimiento</h4>
                        <div className="performance-issues">
                          {currentAnalysis.analysis.performance_issues.slice(0, 3).map((issue, index) => (
                            <div key={index} className="issue-item">
                              <div className="issue-header">
                                <TrendingUp size={14} />
                                <span className="issue-type">{issue.type}</span>
                              </div>
                              <div className="issue-message">{issue.message}</div>
                              {issue.recommendation && (
                                <div className="issue-recommendation">{issue.recommendation}</div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Export Tab */}
                {activeTab === 'export' && (
                  <div className="export-tab">
                    <div className="export-section">
                      <h4>Formatos de Exportación</h4>
                      <div className="export-options">
                        <button className="export-option" onClick={() => onExport('json')}>
                          <FileText size={16} />
                          <span>JSON</span>
                          <small>Datos estructurados</small>
                        </button>
                        <button className="export-option" onClick={() => onExport('html')}>
                          <FileText size={16} />
                          <span>HTML</span>
                          <small>Reporte web</small>
                        </button>
                        <button className="export-option" onClick={() => onExport('pdf')}>
                          <FileText size={16} />
                          <span>PDF</span>
                          <small>Documento profesional</small>
                        </button>
                        <button className="export-option" onClick={() => onExport('xlsx')}>
                          <Database size={16} />
                          <span>Excel</span>
                          <small>Hoja de cálculo</small>
                        </button>
                      </div>
                    </div>

                    <div className="export-section">
                      <h4>Configuración</h4>
                      <button 
                        className="btn-secondary full-width"
                        onClick={onAnalysisSettings}
                      >
                        <Settings size={16} />
                        Configurar Análisis
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </>
      )}

      {/* Collapsed State */}
      {collapsed && (
        <div className="panel-collapsed">
          <button 
            className="collapsed-btn"
            onClick={() => {
              setActiveTab('summary');
              onToggle();
            }}
            title="Resumen"
          >
            <BarChart3 size={20} />
          </button>
          <button 
            className="collapsed-btn"
            onClick={() => {
              setActiveTab('export');
              onToggle();
            }}
            title="Exportar"
          >
            <Download size={20} />
          </button>
          <button 
            className="collapsed-btn"
            onClick={onAnalysisSettings}
            title="Configuración"
          >
            <Settings size={20} />
          </button>
        </div>
      )}
    </div>
  );
};

export default RightPanel;
