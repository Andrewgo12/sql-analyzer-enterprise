import React, { useState, useRef, useEffect } from 'react';
import {
  Plus,
  X,
  Play,
  Save,
  FileText,
  Database,
  AlertTriangle,
  CheckCircle,
  Zap,
  Shield,
  BarChart3,
  Code,
  Eye,
  Settings,
  Activity
} from 'lucide-react';

import CodeEditor from './CodeEditor';
import AnalysisResults from './AnalysisResults';

const MainWorkspace = ({
  activeTabs,
  activeTabId,
  onTabSelect,
  onTabClose,
  onTabContentChange,
  onNewTab,
  onAnalyze,
  onOpenMetrics,
  isAnalyzing,
  analysisProgress,
  currentAnalysis
}) => {
  const [viewMode, setViewMode] = useState('split'); // 'editor', 'results', 'split'
  const [editorSettings, setEditorSettings] = useState({
    theme: 'dark',
    fontSize: 14,
    wordWrap: true,
    lineNumbers: true,
    minimap: true
  });

  const currentTab = activeTabs.find(tab => tab.id === activeTabId);

  const handleTabContentChange = (content) => {
    if (currentTab) {
      onTabContentChange(currentTab.id, content);
    }
  };

  const getTabIcon = (tab) => {
    switch (tab.type) {
      case 'sql':
        return <Database size={14} />;
      case 'result':
        return <BarChart3 size={14} />;
      default:
        return <FileText size={14} />;
    }
  };

  const getAnalysisStatusIcon = (analysis) => {
    if (!analysis) return null;

    const errorCount = analysis.summary?.total_errors || 0;
    if (errorCount === 0) {
      return <CheckCircle className="status-icon success" size={14} />;
    } else if (errorCount < 5) {
      return <AlertTriangle className="status-icon warning" size={14} />;
    } else {
      return <AlertTriangle className="status-icon error" size={14} />;
    }
  };

  return (
    <div className="main-workspace">
      {/* Tab Bar */}
      <div className="tab-bar">
        <div className="tabs-container">
          {activeTabs.map(tab => (
            <div
              key={tab.id}
              className={`tab ${tab.id === activeTabId ? 'active' : ''} ${tab.isDirty ? 'dirty' : ''}`}
              onClick={() => onTabSelect(tab.id)}
            >
              <div className="tab-content">
                {getTabIcon(tab)}
                <span className="tab-title">{tab.title}</span>
                {tab.isDirty && <div className="dirty-indicator" />}
                {getAnalysisStatusIcon(tab.analysis)}
              </div>
              <button
                className="tab-close"
                onClick={(e) => {
                  e.stopPropagation();
                  onTabClose(tab.id);
                }}
              >
                <X size={12} />
              </button>
            </div>
          ))}

          <button
            className="new-tab-btn"
            onClick={onNewTab}
            title="Nueva pestaña"
          >
            <Plus size={16} />
          </button>
        </div>

        {/* Toolbar */}
        <div className="workspace-toolbar">
          <div className="view-mode-selector">
            <button
              className={`view-btn ${viewMode === 'editor' ? 'active' : ''}`}
              onClick={() => setViewMode('editor')}
              title="Solo editor"
            >
              <Code size={16} />
            </button>
            <button
              className={`view-btn ${viewMode === 'split' ? 'active' : ''}`}
              onClick={() => setViewMode('split')}
              title="Vista dividida"
            >
              <Eye size={16} />
            </button>
            <button
              className={`view-btn ${viewMode === 'results' ? 'active' : ''}`}
              onClick={() => setViewMode('results')}
              title="Solo resultados"
            >
              <BarChart3 size={16} />
            </button>
          </div>

          <div className="action-buttons">
            <button
              className="btn-primary"
              onClick={onAnalyze}
              disabled={!currentTab || !currentTab.content.trim() || isAnalyzing}
              title="Analizar SQL"
            >
              <Play size={16} />
              {isAnalyzing ? 'Analizando...' : 'Analizar'}
            </button>

            <button
              className="btn-secondary"
              onClick={onOpenMetrics}
              title="Ver Métricas del Sistema"
            >
              <Activity size={16} />
              Métricas
            </button>

            <button
              className="btn-secondary"
              disabled={!currentTab}
              title="Guardar archivo"
            >
              <Save size={16} />
            </button>

            <button
              className="btn-icon"
              title="Configuración del editor"
            >
              <Settings size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      {isAnalyzing && (
        <div className="analysis-progress">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${analysisProgress}%` }}
            />
          </div>
          <span className="progress-text">
            Analizando... {analysisProgress}%
          </span>
        </div>
      )}

      {/* Content Area */}
      <div className="workspace-content">
        {!currentTab ? (
          <div className="empty-workspace">
            <div className="empty-content">
              <Database className="empty-icon" />
              <h2>Bienvenido a SQL Analyzer Enterprise</h2>
              <p>Selecciona un archivo o crea una nueva consulta para comenzar</p>
              <div className="empty-actions">
                <button
                  className="btn-primary"
                  onClick={onNewTab}
                >
                  <Plus size={16} />
                  Nueva Consulta
                </button>
                <button className="btn-secondary">
                  <FileText size={16} />
                  Abrir Archivo
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className={`content-panels view-${viewMode}`}>
            {/* Editor Panel */}
            {(viewMode === 'editor' || viewMode === 'split') && (
              <div className="editor-panel">
                <div className="panel-header">
                  <h3>
                    <Code size={16} />
                    Editor SQL
                  </h3>
                  <div className="panel-info">
                    <span className="file-info">
                      {currentTab.title}
                      {currentTab.content && (
                        <small>({currentTab.content.length} caracteres)</small>
                      )}
                    </span>
                  </div>
                </div>

                <CodeEditor
                  value={currentTab.content}
                  onChange={handleTabContentChange}
                  language="sql"
                  theme={editorSettings.theme}
                  fontSize={editorSettings.fontSize}
                  wordWrap={editorSettings.wordWrap}
                  lineNumbers={editorSettings.lineNumbers}
                  minimap={editorSettings.minimap}
                  readOnly={isAnalyzing}
                />
              </div>
            )}

            {/* Results Panel */}
            {(viewMode === 'results' || viewMode === 'split') && (
              <div className="results-panel">
                <div className="panel-header">
                  <h3>
                    <BarChart3 size={16} />
                    Resultados del Análisis
                  </h3>
                  {currentTab.analysis && (
                    <div className="analysis-summary">
                      <span className="error-count">
                        <AlertTriangle size={14} />
                        {currentTab.analysis.summary?.total_errors || 0} errores
                      </span>
                      <span className="performance-score">
                        <Zap size={14} />
                        {currentTab.analysis.summary?.performance_score || 100}%
                      </span>
                      <span className="security-score">
                        <Shield size={14} />
                        {currentTab.analysis.summary?.security_score || 100}%
                      </span>
                    </div>
                  )}
                </div>

                {currentTab.analysis ? (
                  <AnalysisResults
                    analysis={currentTab.analysis}
                    isLoading={isAnalyzing}
                  />
                ) : (
                  <div className="no-analysis">
                    <div className="no-analysis-content">
                      <BarChart3 className="no-analysis-icon" />
                      <h3>No hay análisis disponible</h3>
                      <p>Ejecuta el análisis para ver los resultados aquí</p>
                      <button
                        className="btn-primary"
                        onClick={onAnalyze}
                        disabled={!currentTab.content.trim() || isAnalyzing}
                      >
                        <Play size={16} />
                        Analizar Ahora
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="workspace-status">
        <div className="status-left">
          {currentTab && (
            <>
              <span className="status-item">
                Líneas: {(currentTab.content.match(/\n/g) || []).length + 1}
              </span>
              <span className="status-item">
                Caracteres: {currentTab.content.length}
              </span>
              {currentTab.analysis && (
                <span className="status-item">
                  Última análisis: {new Date(currentTab.analysis.timestamp || Date.now()).toLocaleTimeString()}
                </span>
              )}
            </>
          )}
        </div>

        <div className="status-right">
          <span className="status-item">SQL</span>
          <span className="status-item">UTF-8</span>
          {editorSettings.theme === 'dark' ? '🌙' : '☀️'}
        </div>
      </div>
    </div>
  );
};

export default MainWorkspace;
