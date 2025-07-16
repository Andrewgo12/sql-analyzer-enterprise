import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  Code,
  Play,
  Square,
  Save,
  Upload,
  Download,
  RefreshCw,
  Settings,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2,
  Copy,
  Check,
  AlertTriangle,
  CheckCircle,
  Info,
  Database,
  FileText,
  Clock,
  Zap,
  BarChart3,
  Search,
  Filter,
  MoreHorizontal,
  Layers,
  Target,
  Shield,
  Activity,
  TrendingUp,
  TrendingDown,
  Plus,
  Minus,
  RotateCcw,
  BookOpen,
  HelpCircle,
  Lightbulb,
  Bug,
  Gauge,
  PieChart,
  List,
  Grid,
  Terminal,
  Cpu,
  HardDrive,
  Network,
  Lock,
  Unlock,
  Star,
  Bookmark,
  Tag,
  Hash,
  Type,
  AlignLeft,
  Indent,
  Outdent,
  WrapText,
  MousePointer,
  Keyboard,
  Monitor,
  Smartphone,
  Tablet
} from 'lucide-react';
import DatabaseEngineSelector from '../DatabaseEngineSelector';
import { Card, Button, Input, Dropdown } from '../ui';

const SQLAnalysisView = ({
  sqlContent = '',
  setSqlContent,
  analysisResults = null,
  isAnalyzing = false,
  analysisProgress = 0,
  onAnalyze,
  currentConnection = null,
  selectedDatabaseEngine = 'mysql',
  onDatabaseEngineChange,
  onSave,
  onExport,
  dragActive = false,
  onDragOver,
  onDragLeave,
  onDrop
}) => {
  // Enhanced editor settings with more options
  const [editorSettings, setEditorSettings] = useState({
    fontSize: 14,
    theme: 'github-light',
    wordWrap: true,
    lineNumbers: true,
    minimap: false,
    autoComplete: true,
    syntaxHighlighting: true,
    bracketMatching: true,
    autoIndent: true,
    showWhitespace: false,
    highlightActiveLine: true,
    showGutter: true,
    tabSize: 2,
    useSoftTabs: true
  });
  // Enhanced state management
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showResults, setShowResults] = useState(true);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState('editor');
  const [viewMode, setViewMode] = useState('split'); // split, editor-only, results-only
  const [analysisMode, setAnalysisMode] = useState('comprehensive'); // quick, comprehensive, security
  const [autoSave, setAutoSave] = useState(true);
  const [liveValidation, setLiveValidation] = useState(true);
  const [showMinimap, setShowMinimap] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [replaceQuery, setReplaceQuery] = useState('');
  const [showSearchReplace, setShowSearchReplace] = useState(false);
  const [bookmarks, setBookmarks] = useState([]);
  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [validationErrors, setValidationErrors] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });
  const [selectedText, setSelectedText] = useState('');
  const [executionPlan, setExecutionPlan] = useState(null);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [queryComplexity, setQueryComplexity] = useState(null);
  const [showSettings, setShowSettings] = useState(false);

  const textareaRef = useRef(null);
  const editorContainerRef = useRef(null);
  const autoSaveTimeoutRef = useRef(null);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sqlContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleFormat = () => {
    // Simple SQL formatting
    const formatted = sqlContent
      .replace(/\s+/g, ' ')
      .replace(/,/g, ',\n    ')
      .replace(/\bSELECT\b/gi, 'SELECT\n    ')
      .replace(/\bFROM\b/gi, '\nFROM ')
      .replace(/\bWHERE\b/gi, '\nWHERE ')
      .replace(/\bORDER BY\b/gi, '\nORDER BY ')
      .replace(/\bGROUP BY\b/gi, '\nGROUP BY ')
      .replace(/\bHAVING\b/gi, '\nHAVING ')
      .replace(/\bJOIN\b/gi, '\nJOIN ')
      .replace(/\bINNER JOIN\b/gi, '\nINNER JOIN ')
      .replace(/\bLEFT JOIN\b/gi, '\nLEFT JOIN ')
      .replace(/\bRIGHT JOIN\b/gi, '\nRIGHT JOIN ')
      .trim();

    setSqlContent(formatted);
  };

  const getLineCount = () => sqlContent.split('\n').length;
  const getCharCount = () => sqlContent.length;
  const getWordCount = () => sqlContent.trim().split(/\s+/).filter(word => word.length > 0).length;

  // Enhanced utility functions
  const analyzeQueryComplexity = useCallback((query) => {
    if (!query.trim()) return { score: 0, level: 'none', factors: [] };

    const factors = [];
    let score = 0;

    // Count different SQL elements
    const joins = (query.match(/\bJOIN\b/gi) || []).length;
    const subqueries = (query.match(/\(\s*SELECT\b/gi) || []).length;
    const unions = (query.match(/\bUNION\b/gi) || []).length;
    const aggregates = (query.match(/\b(COUNT|SUM|AVG|MAX|MIN|GROUP_CONCAT)\b/gi) || []).length;
    const conditions = (query.match(/\b(WHERE|HAVING)\b/gi) || []).length;

    if (joins > 0) {
      score += joins * 2;
      factors.push(`${joins} JOIN${joins > 1 ? 's' : ''}`);
    }
    if (subqueries > 0) {
      score += subqueries * 3;
      factors.push(`${subqueries} subquer${subqueries > 1 ? 'ies' : 'y'}`);
    }
    if (unions > 0) {
      score += unions * 2;
      factors.push(`${unions} UNION${unions > 1 ? 's' : ''}`);
    }
    if (aggregates > 0) {
      score += aggregates;
      factors.push(`${aggregates} aggregate function${aggregates > 1 ? 's' : ''}`);
    }
    if (conditions > 0) {
      score += conditions;
      factors.push(`${conditions} condition${conditions > 1 ? 's' : ''}`);
    }

    const level = score === 0 ? 'none' :
      score <= 3 ? 'simple' :
        score <= 8 ? 'moderate' :
          score <= 15 ? 'complex' : 'very complex';

    return { score, level, factors };
  }, []);

  const validateSQL = useCallback((query) => {
    const errors = [];
    const warnings = [];

    if (!query.trim()) {
      return { errors, warnings, isValid: true };
    }

    // Basic SQL validation
    const keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'INSERT', 'UPDATE', 'DELETE'];
    const hasKeyword = keywords.some(keyword =>
      new RegExp(`\\b${keyword}\\b`, 'i').test(query)
    );

    if (!hasKeyword) {
      errors.push({
        line: 1,
        column: 1,
        message: 'No valid SQL keywords found',
        severity: 'error'
      });
    }

    // Check for common issues
    const openParens = (query.match(/\(/g) || []).length;
    const closeParens = (query.match(/\)/g) || []).length;

    if (openParens !== closeParens) {
      errors.push({
        line: 1,
        column: 1,
        message: 'Mismatched parentheses',
        severity: 'error'
      });
    }

    // Check for potential security issues
    if (/\b(DROP|DELETE|TRUNCATE)\b/i.test(query)) {
      warnings.push({
        line: 1,
        column: 1,
        message: 'Potentially destructive operation detected',
        severity: 'warning'
      });
    }

    return { errors, warnings, isValid: errors.length === 0 };
  }, []);

  const addToHistory = useCallback((content) => {
    if (content && content !== history[historyIndex]) {
      const newHistory = history.slice(0, historyIndex + 1);
      newHistory.push(content);
      setHistory(newHistory);
      setHistoryIndex(newHistory.length - 1);
    }
  }, [history, historyIndex]);

  const handleUndo = () => {
    if (historyIndex > 0) {
      setHistoryIndex(historyIndex - 1);
      setSqlContent(history[historyIndex - 1]);
    }
  };

  const handleRedo = () => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(historyIndex + 1);
      setSqlContent(history[historyIndex + 1]);
    }
  };

  const handleBookmark = () => {
    const bookmark = {
      id: Date.now(),
      content: sqlContent,
      timestamp: new Date().toISOString(),
      name: `Bookmark ${bookmarks.length + 1}`
    };
    setBookmarks([...bookmarks, bookmark]);
  };

  const loadBookmark = (bookmark) => {
    setSqlContent(bookmark.content);
    addToHistory(bookmark.content);
  };

  // Auto-save functionality
  useEffect(() => {
    if (autoSave && sqlContent) {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }

      autoSaveTimeoutRef.current = setTimeout(() => {
        console.log('Auto-saving SQL content...');
        // In real implementation, this would save to backend
      }, 2000);
    }

    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, [sqlContent, autoSave]);

  // Live validation
  useEffect(() => {
    if (liveValidation && sqlContent) {
      const validation = validateSQL(sqlContent);
      setValidationErrors(validation.errors);

      const complexity = analyzeQueryComplexity(sqlContent);
      setQueryComplexity(complexity);
    }
  }, [sqlContent, liveValidation, validateSQL, analyzeQueryComplexity]);

  const editorTabs = [
    { id: 'editor', label: 'Editor SQL', icon: Code },
    { id: 'results', label: 'Resultados', icon: BarChart3, disabled: !analysisResults },
    { id: 'settings', label: 'Configuración', icon: Settings }
  ];

  const renderEditor = () => (
    <div className="sql-editor-container">
      <div className="editor-toolbar">
        <div className="toolbar-left">
          <button
            className="toolbar-btn primary"
            onClick={onAnalyze}
            disabled={isAnalyzing || !sqlContent.trim()}
          >
            {isAnalyzing ? (
              <>
                <RefreshCw size={16} className="spinning" />
                Analizando...
              </>
            ) : (
              <>
                <Play size={16} />
                Analizar SQL
              </>
            )}
          </button>

          <button
            className="toolbar-btn"
            onClick={handleFormat}
            disabled={!sqlContent.trim()}
          >
            <Code size={16} />
            Formatear
          </button>

          <button
            className="toolbar-btn"
            onClick={onSave}
            disabled={!sqlContent.trim()}
          >
            <Save size={16} />
            Guardar
          </button>

          <button
            className="toolbar-btn"
            onClick={handleCopy}
            disabled={!sqlContent.trim()}
          >
            {copied ? <Check size={16} /> : <Copy size={16} />}
            {copied ? 'Copiado' : 'Copiar'}
          </button>
        </div>

        <div className="toolbar-right">
          <div className="connection-indicator">
            {currentConnection ? (
              <>
                <Database size={14} />
                <span>{currentConnection.name}</span>
                <div className="connection-status active"></div>
              </>
            ) : (
              <>
                <Database size={14} />
                <span>Sin conexión</span>
                <div className="connection-status inactive"></div>
              </>
            )}
          </div>

          <button
            className="toolbar-btn"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
          </button>
        </div>
      </div>

      <div
        className={`editor-content ${dragActive ? 'drag-active' : ''} ${isFullscreen ? 'fullscreen' : ''}`}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
      >
        <div className="editor-gutter">
          {editorSettings.lineNumbers && (
            <div className="line-numbers">
              {Array.from({ length: getLineCount() }, (_, i) => (
                <div key={i + 1} className="line-number">{i + 1}</div>
              ))}
            </div>
          )}
        </div>

        <textarea
          ref={textareaRef}
          value={sqlContent}
          onChange={(e) => setSqlContent(e.target.value)}
          placeholder="-- Escribe tu consulta SQL aquí...\n-- Ejemplo:\nSELECT \n    u.id,\n    u.nombre,\n    u.email\nFROM usuarios u\nWHERE u.activo = 1\nORDER BY u.fecha_registro DESC;"
          className="sql-textarea"
          style={{
            fontSize: `${editorSettings.fontSize}px`,
            wordWrap: editorSettings.wordWrap ? 'break-word' : 'normal'
          }}
          spellCheck={false}
        />

        {dragActive && (
          <div className="drag-overlay">
            <Upload size={48} />
            <p>Suelta el archivo SQL aquí</p>
          </div>
        )}
      </div>

      <div className="editor-footer">
        <div className="editor-stats">
          <span>Líneas: {getLineCount()}</span>
          <span>Palabras: {getWordCount()}</span>
          <span>Caracteres: {getCharCount()}</span>
        </div>

        {isAnalyzing && (
          <div className="analysis-progress">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${analysisProgress}%` }}
              ></div>
            </div>
            <span className="progress-text">{Math.round(analysisProgress)}%</span>
          </div>
        )}
      </div>
    </div>
  );

  const renderResults = () => {
    if (!analysisResults) {
      return (
        <div className="no-results">
          <BarChart3 size={64} className="no-results-icon" />
          <h3>Sin Resultados de Análisis</h3>
          <p>Ejecuta un análisis SQL para ver los resultados aquí</p>
          <button
            className="btn-primary"
            onClick={onAnalyze}
            disabled={!sqlContent.trim()}
          >
            <Play size={16} />
            Analizar SQL
          </button>
        </div>
      );
    }

    const {
      summary,
      analysis,
      performance_analysis,
      security_analysis,
      schema_analysis,
      metadata
    } = analysisResults;

    return (
      <div className="analysis-results">
        <div className="results-header">
          <h3>Resultados del Análisis</h3>
          <div className="results-actions">
            <button className="btn-secondary" onClick={onExport}>
              <Download size={16} />
              Exportar
            </button>
          </div>
        </div>

        <div className="results-summary">
          <div className="summary-card error">
            <AlertTriangle className="summary-icon" size={20} />
            <div className="summary-content">
              <div className="summary-value">{summary?.total_errors || 0}</div>
              <div className="summary-label">Errores</div>
            </div>
          </div>

          <div className="summary-card warning">
            <AlertTriangle className="summary-icon" size={20} />
            <div className="summary-content">
              <div className="summary-value">{summary?.total_warnings || 0}</div>
              <div className="summary-label">Advertencias</div>
            </div>
          </div>

          <div className="summary-card success">
            <CheckCircle className="summary-icon" size={20} />
            <div className="summary-content">
              <div className="summary-value">{summary?.performance_score || performance_analysis?.overall_score || 100}%</div>
              <div className="summary-label">Rendimiento</div>
            </div>
          </div>

          <div className="summary-card info">
            <Zap className="summary-icon" size={20} />
            <div className="summary-content">
              <div className="summary-value">{summary?.security_score || security_analysis?.overall_score || 100}%</div>
              <div className="summary-label">Seguridad</div>
            </div>
          </div>

          <div className="summary-card neutral">
            <Database className="summary-icon" size={20} />
            <div className="summary-content">
              <div className="summary-value">{schema_analysis?.tables_count || 0}</div>
              <div className="summary-label">Tablas</div>
            </div>
          </div>

          <div className="summary-card neutral">
            <Clock className="summary-icon" size={20} />
            <div className="summary-content">
              <div className="summary-value">{metadata?.analysis_time || '0.0'}s</div>
              <div className="summary-label">Tiempo</div>
            </div>
          </div>
        </div>

        <div className="results-details">
          {analysis?.errors?.length > 0 && (
            <div className="results-section">
              <h4 className="section-title error">
                <AlertTriangle size={16} />
                Errores Encontrados ({analysis.errors.length})
              </h4>
              <div className="issues-list">
                {analysis.errors.map((error, index) => (
                  <div key={index} className="issue-item error">
                    <div className="issue-header">
                      <span className="issue-type">Error</span>
                      <span className="issue-line">Línea {error.line || 'N/A'}</span>
                    </div>
                    <div className="issue-message">{error.message}</div>
                    {error.suggestion && (
                      <div className="issue-suggestion">
                        <strong>Sugerencia:</strong> {error.suggestion}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {analysis?.warnings?.length > 0 && (
            <div className="results-section">
              <h4 className="section-title warning">
                <AlertTriangle size={16} />
                Advertencias ({analysis.warnings.length})
              </h4>
              <div className="issues-list">
                {analysis.warnings.map((warning, index) => (
                  <div key={index} className="issue-item warning">
                    <div className="issue-header">
                      <span className="issue-type">Advertencia</span>
                      <span className="issue-line">Línea {warning.line || 'N/A'}</span>
                    </div>
                    <div className="issue-message">{warning.message}</div>
                    {warning.suggestion && (
                      <div className="issue-suggestion">
                        <strong>Sugerencia:</strong> {warning.suggestion}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {analysis?.suggestions?.length > 0 && (
            <div className="results-section">
              <h4 className="section-title info">
                <CheckCircle size={16} />
                Sugerencias de Mejora ({analysis.suggestions.length})
              </h4>
              <div className="suggestions-list">
                {analysis.suggestions.map((suggestion, index) => (
                  <div key={index} className="suggestion-item">
                    <div className="suggestion-message">{suggestion.message}</div>
                    {suggestion.example && (
                      <div className="suggestion-example">
                        <strong>Ejemplo:</strong>
                        <code>{suggestion.example}</code>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Performance Analysis Section */}
          {performance_analysis && (
            <div className="results-section">
              <h4 className="section-title performance">
                <Zap size={16} />
                Análisis de Rendimiento
              </h4>
              <div className="performance-details">
                {performance_analysis.query_complexity && (
                  <div className="performance-metric">
                    <span className="metric-label">Complejidad de Consulta:</span>
                    <span className={`metric-value ${performance_analysis.query_complexity.level}`}>
                      {performance_analysis.query_complexity.level} ({performance_analysis.query_complexity.score}/100)
                    </span>
                  </div>
                )}

                {performance_analysis.index_recommendations?.length > 0 && (
                  <div className="recommendations">
                    <h5>Recomendaciones de Índices:</h5>
                    <ul>
                      {performance_analysis.index_recommendations.map((rec, index) => (
                        <li key={index}>
                          <strong>{rec.table}:</strong> {rec.recommendation}
                          {rec.impact && <span className="impact">Impacto: {rec.impact}</span>}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {performance_analysis.optimization_suggestions?.length > 0 && (
                  <div className="recommendations">
                    <h5>Sugerencias de Optimización:</h5>
                    <ul>
                      {performance_analysis.optimization_suggestions.map((suggestion, index) => (
                        <li key={index}>
                          <strong>{suggestion.type}:</strong> {suggestion.description}
                          {suggestion.example && (
                            <div className="suggestion-example">
                              <code>{suggestion.example}</code>
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Security Analysis Section */}
          {security_analysis && (
            <div className="results-section">
              <h4 className="section-title security">
                <AlertTriangle size={16} />
                Análisis de Seguridad
              </h4>
              <div className="security-details">
                {security_analysis.vulnerabilities?.length > 0 && (
                  <div className="vulnerabilities">
                    <h5>Vulnerabilidades Detectadas:</h5>
                    {security_analysis.vulnerabilities.map((vuln, index) => (
                      <div key={index} className={`vulnerability-item ${vuln.severity}`}>
                        <div className="vuln-header">
                          <span className="vuln-type">{vuln.type}</span>
                          <span className={`vuln-severity ${vuln.severity}`}>
                            {vuln.severity.toUpperCase()}
                          </span>
                        </div>
                        <div className="vuln-description">{vuln.description}</div>
                        {vuln.recommendation && (
                          <div className="vuln-recommendation">
                            <strong>Recomendación:</strong> {vuln.recommendation}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {security_analysis.sql_injection_risk && (
                  <div className="security-metric">
                    <span className="metric-label">Riesgo de Inyección SQL:</span>
                    <span className={`metric-value ${security_analysis.sql_injection_risk.level}`}>
                      {security_analysis.sql_injection_risk.level}
                    </span>
                  </div>
                )}

                {security_analysis.data_exposure_risk && (
                  <div className="security-metric">
                    <span className="metric-label">Riesgo de Exposición de Datos:</span>
                    <span className={`metric-value ${security_analysis.data_exposure_risk.level}`}>
                      {security_analysis.data_exposure_risk.level}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Schema Analysis Section */}
          {schema_analysis && (
            <div className="results-section">
              <h4 className="section-title schema">
                <Database size={16} />
                Análisis de Esquema
              </h4>
              <div className="schema-details">
                {schema_analysis.tables?.length > 0 && (
                  <div className="tables-analysis">
                    <h5>Tablas Analizadas ({schema_analysis.tables.length}):</h5>
                    <div className="tables-grid">
                      {schema_analysis.tables.map((table, index) => (
                        <div key={index} className="table-item">
                          <div className="table-name">{table.name}</div>
                          <div className="table-info">
                            <span>Columnas: {table.columns?.length || 0}</span>
                            {table.primary_key && <span>PK: {table.primary_key}</span>}
                            {table.indexes && <span>Índices: {table.indexes.length}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {schema_analysis.relationships?.length > 0 && (
                  <div className="relationships">
                    <h5>Relaciones Detectadas:</h5>
                    <ul>
                      {schema_analysis.relationships.map((rel, index) => (
                        <li key={index}>
                          <strong>{rel.from_table}.{rel.from_column}</strong> →
                          <strong>{rel.to_table}.{rel.to_column}</strong>
                          <span className="relationship-type">({rel.type})</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {schema_analysis.data_quality && (
                  <div className="data-quality">
                    <h5>Calidad de Datos:</h5>
                    <div className="quality-metrics">
                      <div className="quality-metric">
                        <span>Completitud:</span>
                        <span>{schema_analysis.data_quality.completeness}%</span>
                      </div>
                      <div className="quality-metric">
                        <span>Consistencia:</span>
                        <span>{schema_analysis.data_quality.consistency}%</span>
                      </div>
                      <div className="quality-metric">
                        <span>Validez:</span>
                        <span>{schema_analysis.data_quality.validity}%</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderSettings = () => (
    <div className="editor-settings">
      <h3>Configuración del Editor</h3>

      <div className="settings-group">
        <label>Tamaño de Fuente</label>
        <input
          type="range"
          min="10"
          max="24"
          value={editorSettings.fontSize}
          onChange={(e) => setEditorSettings(prev => ({ ...prev, fontSize: parseInt(e.target.value) }))}
        />
        <span>{editorSettings.fontSize}px</span>
      </div>

      <div className="settings-group">
        <label>
          <input
            type="checkbox"
            checked={editorSettings.lineNumbers}
            onChange={(e) => setEditorSettings(prev => ({ ...prev, lineNumbers: e.target.checked }))}
          />
          Mostrar números de línea
        </label>
      </div>

      <div className="settings-group">
        <label>
          <input
            type="checkbox"
            checked={editorSettings.wordWrap}
            onChange={(e) => setEditorSettings(prev => ({ ...prev, wordWrap: e.target.checked }))}
          />
          Ajuste de línea automático
        </label>
      </div>
    </div>
  );

  return (
    <div className="sql-analysis-view">
      <div className="view-header">
        <div className="header-title">
          <Code size={24} />
          <h1>Análisis SQL</h1>
        </div>

        <div className="header-controls">
          <DatabaseEngineSelector
            selectedEngine={selectedDatabaseEngine}
            onEngineChange={onDatabaseEngineChange}
            disabled={isAnalyzing}
            compact={true}
            showLabel={true}
          />
        </div>

        <div className="view-tabs">
          {editorTabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''} ${tab.disabled ? 'disabled' : ''}`}
              onClick={() => !tab.disabled && setActiveTab(tab.id)}
              disabled={tab.disabled}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="view-content">
        {activeTab === 'editor' && renderEditor()}
        {activeTab === 'results' && renderResults()}
        {activeTab === 'settings' && renderSettings()}
      </div>
    </div>
  );
};

export default SQLAnalysisView;
