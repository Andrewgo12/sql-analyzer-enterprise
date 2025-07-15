import React, { useState, useEffect, useCallback } from 'react';
import {
  Database,
  FileText,
  Settings,
  Download,
  Shield,
  Zap,
  BarChart3,
  Search,
  Upload,
  Play,
  AlertTriangle,
  CheckCircle,
  Clock,
  Menu,
  X,
  Home,
  History,
  Terminal,
  FolderOpen,
  Code,
  Activity,
  Users,
  HelpCircle,
  ChevronRight,
  ChevronDown
} from 'lucide-react';

import NotificationSystem, { notify } from './NotificationSystem';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';

const EnterpriseApp = () => {
  // UI State
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeView, setActiveView] = useState('dashboard');
  const [activeModal, setActiveModal] = useState(null);

  // Application State
  const [sqlContent, setSqlContent] = useState('-- Escribe tu consulta SQL aquí\nSELECT * FROM usuarios WHERE activo = 1;');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [connections, setConnections] = useState([]);
  const [currentConnection, setCurrentConnection] = useState(null);
  const [terminalOutput, setTerminalOutput] = useState([]);
  const [terminalInput, setTerminalInput] = useState('');

  // File Upload State
  const [uploadedFile, setUploadedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  // Menu Configuration
  const menuSections = [
    {
      title: 'Principal',
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: Home, description: 'Vista general del sistema' },
        { id: 'sql-analysis', label: 'Análisis SQL', icon: Code, description: 'Analizar consultas SQL' }
      ]
    },
    {
      title: 'Base de Datos',
      items: [
        { id: 'connections', label: 'Conexiones', icon: Database, description: 'Gestionar conexiones de BD' },
        { id: 'history', label: 'Historial', icon: History, description: 'Análisis anteriores' }
      ]
    },
    {
      title: 'Herramientas',
      items: [
        { id: 'terminal', label: 'Terminal', icon: Terminal, description: 'Terminal integrado' },
        { id: 'downloads', label: 'Descargas', icon: Download, description: 'Gestionar descargas' }
      ]
    },
    {
      title: 'Sistema',
      items: [
        { id: 'metrics', label: 'Métricas', icon: Activity, description: 'Monitoreo del sistema' },
        { id: 'settings', label: 'Configuración', icon: Settings, description: 'Configuración general' }
      ]
    }
  ];

  // Core Functions
  const analyzeSQL = useCallback(async () => {
    if (!sqlContent.trim()) {
      notify.warning('Contenido vacío', 'No hay contenido SQL para analizar');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisProgress(0);
    notify.info('Análisis iniciado', 'Analizando consulta SQL...');

    try {
      // Progress simulation
      const progressInterval = setInterval(() => {
        setAnalysisProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Create FormData for API call
      const formData = new FormData();
      const blob = new Blob([sqlContent], { type: 'text/plain' });
      formData.append('file', blob, 'query.sql');
      formData.append('database_engine', 'mysql');

      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        body: formData
      });

      clearInterval(progressInterval);
      setAnalysisProgress(100);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setAnalysisResults(result);

      // Add to history
      const historyItem = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        content: sqlContent.substring(0, 100) + '...',
        summary: result.summary,
        results: result
      };

      setAnalysisHistory(prev => {
        const updated = [historyItem, ...prev.slice(0, 19)];
        localStorage.setItem('sql_analyzer_history', JSON.stringify(updated));
        return updated;
      });

      const errorCount = result.summary?.total_errors || 0;
      if (errorCount === 0) {
        notify.success('Análisis completado', 'SQL analizado sin errores');
      } else {
        notify.warning('Análisis completado', `Se encontraron ${errorCount} errores`);
      }

    } catch (error) {
      console.error('Analysis error:', error);
      notify.error('Error en análisis', error.message || 'Error desconocido');
    } finally {
      setIsAnalyzing(false);
      setAnalysisProgress(0);
    }
  }, [sqlContent]);

  // File Handling Functions
  const handleFileUpload = useCallback((file) => {
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      setSqlContent(e.target.result);
      setUploadedFile(file);
      notify.success('Archivo cargado', `${file.name} cargado correctamente`);
    };
    reader.readAsText(file);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type === 'text/plain' || file.name.endsWith('.sql')) {
        handleFileUpload(file);
      } else {
        notify.error('Tipo de archivo no válido', 'Solo se permiten archivos .sql');
      }
    }
  }, [handleFileUpload]);

  // Terminal Functions
  const executeTerminalCommand = useCallback((command) => {
    const timestamp = new Date().toLocaleTimeString();
    const newOutput = {
      id: Date.now(),
      timestamp,
      command,
      output: `Ejecutando: ${command}`,
      type: 'command'
    };

    setTerminalOutput(prev => [...prev, newOutput]);

    // Simulate command execution
    setTimeout(() => {
      const result = {
        id: Date.now() + 1,
        timestamp: new Date().toLocaleTimeString(),
        output: `Resultado de: ${command}`,
        type: 'result'
      };
      setTerminalOutput(prev => [...prev, result]);
    }, 500);

    setTerminalInput('');
  }, []);

  // Modal Functions
  const openModal = useCallback((modalType) => {
    setActiveModal(modalType);
  }, []);

  const closeModal = useCallback(() => {
    setActiveModal(null);
  }, []);

  // Load initial data
  useEffect(() => {
    const savedHistory = localStorage.getItem('sql_analyzer_history');
    if (savedHistory) {
      try {
        setAnalysisHistory(JSON.parse(savedHistory));
      } catch (error) {
        console.error('Error loading history:', error);
      }
    }

    const savedConnections = localStorage.getItem('sql_analyzer_connections');
    if (savedConnections) {
      try {
        setConnections(JSON.parse(savedConnections));
      } catch (error) {
        console.error('Error loading connections:', error);
      }
    }
  }, []);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onAnalyze: analyzeSQL,
    onNewTab: () => {
      setSqlContent('-- Nueva consulta SQL\nSELECT * FROM tabla;');
      setAnalysisResults(null);
      notify.info('Nueva consulta', 'Editor limpiado para nueva consulta');
    },
    onOpenMetrics: () => setActiveView('metrics'),
    onOpenConnection: () => openModal('connections'),
    onExport: () => {
      if (analysisResults) {
        openModal('export');
      } else {
        notify.warning('Exportación no disponible', 'No hay análisis para exportar');
      }
    },
    onSave: () => {
      localStorage.setItem('sql_analyzer_current_query', sqlContent);
      notify.info('Guardado', 'Consulta guardada localmente');
    },
    onShowHelp: () => openModal('help')
  });

  // Render Functions
  const renderSidebar = () => (
    <div className={`sidebar ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Database className="logo-icon" />
          {sidebarOpen && <span className="logo-text">SQL Analyzer</span>}
        </div>
        <button
          className="sidebar-toggle"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle sidebar"
        >
          <Menu size={20} />
        </button>
      </div>

      <nav className="sidebar-nav">
        {menuSections.map((section, sectionIndex) => (
          <div key={sectionIndex} className="nav-section">
            {sidebarOpen && <h3 className="nav-section-title">{section.title}</h3>}
            <ul className="nav-items">
              {section.items.map((item) => (
                <li key={item.id} className="nav-item">
                  <button
                    className={`nav-link ${activeView === item.id ? 'nav-link-active' : ''}`}
                    onClick={() => setActiveView(item.id)}
                    title={item.description}
                  >
                    <item.icon size={20} className="nav-icon" />
                    {sidebarOpen && <span className="nav-text">{item.label}</span>}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
    </div>
  );

  const renderMainContent = () => {
    switch (activeView) {
      case 'dashboard':
        return renderDashboard();
      case 'sql-analysis':
        return renderSQLAnalysis();
      case 'connections':
        return renderConnections();
      case 'history':
        return renderHistory();
      case 'terminal':
        return renderTerminal();
      case 'downloads':
        return renderDownloads();
      case 'metrics':
        return renderMetrics();
      case 'settings':
        return renderSettings();
      default:
        return renderDashboard();
    }
  };

  // Terminal Functions
  const executeTerminalCommand = useCallback((command) => {
    const timestamp = new Date().toLocaleTimeString();
    const newOutput = {
      id: Date.now(),
      timestamp,
      type: 'command',
      content: `$ ${command}`
    };

    setTerminalOutput(prev => [...prev, newOutput]);

    // Simulate command execution
    setTimeout(() => {
      let result = '';
      switch (command.toLowerCase()) {
        case 'help':
          result = 'Comandos disponibles:\n- status: Estado del sistema\n- clear: Limpiar terminal\n- analyze: Ejecutar análisis SQL\n- connections: Listar conexiones';
          break;
        case 'status':
          result = `Sistema: Activo\nCPU: ${systemMetrics.cpu}%\nMemoria: ${systemMetrics.memory}%\nDisco: ${systemMetrics.disk}%`;
          break;
        case 'clear':
          setTerminalOutput([]);
          return;
        case 'analyze':
          result = 'Iniciando análisis SQL...';
          analyzeSQL();
          break;
        case 'connections':
          result = connections.length > 0
            ? connections.map(c => `- ${c.name} (${c.engine})`).join('\n')
            : 'No hay conexiones configuradas';
          break;
        default:
          result = `Comando no reconocido: ${command}. Escribe 'help' para ver comandos disponibles.`;
      }

      const resultOutput = {
        id: Date.now() + 1,
        timestamp: new Date().toLocaleTimeString(),
        type: 'result',
        content: result
      };
      setTerminalOutput(prev => [...prev, resultOutput]);
    }, 500);

    setTerminalInput('');
  }, [systemMetrics, connections, analyzeSQL]);

  // Modal Functions
  const openModal = useCallback((modalType) => {
    setActiveModal(modalType);
  }, []);

  const closeModal = useCallback(() => {
    setActiveModal(null);
  }, []);

  // Responsive handling
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Load initial data
  useEffect(() => {
    const savedHistory = localStorage.getItem('sql_analyzer_history');
    if (savedHistory) {
      try {
        setAnalysisHistory(JSON.parse(savedHistory));
      } catch (error) {
        console.error('Error loading history:', error);
      }
    }

    const savedConnections = localStorage.getItem('sql_analyzer_connections');
    if (savedConnections) {
      try {
        setConnections(JSON.parse(savedConnections));
      } catch (error) {
        console.error('Error loading connections:', error);
      }
    }

    // Simulate system metrics updates
    const metricsInterval = setInterval(() => {
      setSystemMetrics(prev => ({
        cpu: Math.max(10, Math.min(90, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(20, Math.min(95, prev.memory + (Math.random() - 0.5) * 5)),
        disk: Math.max(10, Math.min(80, prev.disk + (Math.random() - 0.5) * 2)),
        network: Math.max(0, Math.min(100, prev.network + (Math.random() - 0.5) * 20))
      }));
    }, 5000);

    return () => clearInterval(metricsInterval);
  }, []);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onAnalyze: analyzeSQL,
    onNewTab: () => {
      setSqlContent('-- Nueva consulta SQL\nSELECT * FROM tabla;');
      setAnalysisResults(null);
      notify.info('Nueva consulta', 'Editor limpiado para nueva consulta');
    },
    onOpenMetrics: () => setActiveView('metrics'),
    onOpenConnection: () => setActiveView('connections'),
    onExport: () => {
      if (analysisResults) {
        setActiveView('downloads');
      } else {
        notify.warning('Exportación no disponible', 'No hay análisis para exportar');
      }
    },
    onSave: () => {
      localStorage.setItem('sql_analyzer_current_query', sqlContent);
      notify.info('Guardado', 'Consulta guardada localmente');
    },
    onShowHelp: () => setActiveView('help')
  });

  // Render Functions
  const renderSidebar = () => (
    <div className={`enterprise-sidebar ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'} ${isMobile ? 'sidebar-mobile' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Database className="logo-icon" size={24} />
          {sidebarOpen && <span className="logo-text">SQL Analyzer Enterprise</span>}
        </div>
        <button
          className="sidebar-toggle"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle sidebar"
        >
          <Menu size={20} />
        </button>
      </div>

      <nav className="sidebar-nav">
        {menuSections.map((section, sectionIndex) => (
          <div key={sectionIndex} className="nav-section">
            {sidebarOpen && (
              <div className="nav-section-header">
                <section.icon size={16} className="section-icon" />
                <h3 className="nav-section-title">{section.title}</h3>
              </div>
            )}
            <ul className="nav-items">
              {section.items.map((item) => (
                <li key={item.id} className="nav-item">
                  <button
                    className={`nav-link ${activeView === item.id ? 'nav-link-active' : ''}`}
                    onClick={() => setActiveView(item.id)}
                    title={item.description}
                  >
                    <item.icon size={20} className="nav-icon" />
                    {sidebarOpen && (
                      <div className="nav-content">
                        <span className="nav-text">{item.label}</span>
                        {item.badge && <span className="nav-badge">{item.badge}</span>}
                      </div>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
    </div>
  );

  const renderMainContent = () => {
    switch (activeView) {
      case 'dashboard':
        return renderDashboard();
      case 'sql-analysis':
        return renderSQLAnalysis();
      case 'file-manager':
        return renderFileManager();
      case 'connections':
        return renderConnections();
      case 'history':
        return renderHistory();
      case 'terminal':
        return renderTerminal();
      case 'downloads':
        return renderDownloads();
      case 'metrics':
        return renderMetrics();
      case 'settings':
        return renderSettings();
      case 'help':
        return renderHelp();
      default:
        return renderDashboard();
    }
  };

  const renderDashboard = () => (
    <div className="view-container dashboard-view">
      <div className="view-header">
        <h1 className="view-title">
          <Home size={24} className="title-icon" />
          Dashboard
        </h1>
        <p className="view-description">Vista general del sistema SQL Analyzer Enterprise</p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card metric-card">
          <div className="card-header">
            <BarChart3 className="card-icon" />
            <h3>Análisis Realizados</h3>
          </div>
          <div className="card-content">
            <div className="metric-value">{analysisHistory.length}</div>
            <div className="metric-label">Total de análisis</div>
            <div className="metric-trend positive">+12% este mes</div>
          </div>
        </div>

        <div className="dashboard-card metric-card">
          <div className="card-header">
            <Database className="card-icon" />
            <h3>Conexiones</h3>
          </div>
          <div className="card-content">
            <div className="metric-value">{connections.length}</div>
            <div className="metric-label">Conexiones configuradas</div>
            <div className="metric-status">
              {currentConnection ? `Activa: ${currentConnection.name}` : 'Sin conexión activa'}
            </div>
          </div>
        </div>

        <div className="dashboard-card metric-card">
          <div className="card-header">
            <CheckCircle className="card-icon" />
            <h3>Estado del Sistema</h3>
          </div>
          <div className="card-content">
            <div className="metric-value status-healthy">Activo</div>
            <div className="metric-label">Sistema operativo</div>
            <div className="system-indicators">
              <span className="indicator cpu">CPU: {systemMetrics.cpu}%</span>
              <span className="indicator memory">RAM: {systemMetrics.memory}%</span>
            </div>
          </div>
        </div>

        <div className="dashboard-card metric-card">
          <div className="card-header">
            <FolderOpen className="card-icon" />
            <h3>Archivos SQL</h3>
          </div>
          <div className="card-content">
            <div className="metric-value">{uploadedFiles.length}</div>
            <div className="metric-label">Archivos cargados</div>
            <div className="metric-info">
              {uploadedFiles.reduce((total, file) => total + file.size, 0) > 0
                ? `${(uploadedFiles.reduce((total, file) => total + file.size, 0) / 1024).toFixed(1)} KB total`
                : 'Sin archivos'
              }
            </div>
          </div>
        </div>
      </div>

      <div className="quick-actions">
        <h2>Acciones Rápidas</h2>
        <div className="action-buttons">
          <button
            className="action-btn primary"
            onClick={() => setActiveView('sql-analysis')}
          >
            <Code size={20} />
            Nuevo Análisis SQL
          </button>
          <button
            className="action-btn secondary"
            onClick={() => setActiveView('file-manager')}
          >
            <Upload size={20} />
            Cargar Archivo SQL
          </button>
          <button
            className="action-btn secondary"
            onClick={() => setActiveView('connections')}
          >
            <Database size={20} />
            Gestionar Conexiones
          </button>
          <button
            className="action-btn secondary"
            onClick={() => setActiveView('history')}
          >
            <History size={20} />
            Ver Historial
          </button>
        </div>
      </div>

      {analysisHistory.length > 0 && (
        <div className="recent-activity">
          <h2>Actividad Reciente</h2>
          <div className="activity-list">
            {analysisHistory.slice(0, 5).map((item) => (
              <div key={item.id} className="activity-item">
                <div className="activity-icon">
                  <Code size={16} />
                </div>
                <div className="activity-content">
                  <div className="activity-title">{item.title}</div>
                  <div className="activity-meta">
                    {new Date(item.timestamp).toLocaleString()} • {item.lineCount} líneas
                  </div>
                </div>
                <button
                  className="activity-action"
                  onClick={() => {
                    setSqlContent(item.content);
                    setActiveView('sql-analysis');
                  }}
                >
                  <Eye size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderSQLAnalysis = () => (
    <div className="view-container sql-analysis-view">
      <div className="view-header">
        <h1 className="view-title">
          <Code size={24} className="title-icon" />
          Análisis SQL
        </h1>
        <div className="view-actions">
          <button
            className="btn-secondary"
            onClick={() => {
              setSqlContent('-- Nueva consulta SQL\nSELECT * FROM tabla;');
              setAnalysisResults(null);
            }}
          >
            <Plus size={16} />
            Nueva Consulta
          </button>
          <button
            className="btn-primary"
            onClick={analyzeSQL}
            disabled={isAnalyzing || !sqlContent.trim()}
          >
            {isAnalyzing ? <RefreshCw size={16} className="spinning" /> : <Play size={16} />}
            {isAnalyzing ? 'Analizando...' : 'Analizar SQL'}
          </button>
        </div>
      </div>

      <div className="sql-analysis-layout">
        <div className="sql-editor-section">
          <div className="editor-header">
            <h3>Editor SQL</h3>
            <div className="editor-info">
              <span>{sqlContent.split('\n').length} líneas</span>
              <span>{new Blob([sqlContent]).size} bytes</span>
              {currentConnection && (
                <span className="connection-info">
                  <Database size={14} />
                  {currentConnection.name}
                </span>
              )}
            </div>
          </div>

          <div
            className={`sql-editor ${dragActive ? 'drag-active' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <textarea
              value={sqlContent}
              onChange={(e) => setSqlContent(e.target.value)}
              placeholder="-- Escribe tu consulta SQL aquí..."
              className="sql-textarea"
              spellCheck={false}
            />
            {dragActive && (
              <div className="drag-overlay">
                <Upload size={48} />
                <p>Suelta el archivo SQL aquí</p>
              </div>
            )}
          </div>

          {isAnalyzing && (
            <div className="analysis-progress">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${analysisProgress}%` }}
                ></div>
              </div>
              <span className="progress-text">{Math.round(analysisProgress)}% completado</span>
            </div>
          )}
        </div>

        <div className="analysis-results-section">
          <div className="results-header">
            <h3>Resultados del Análisis</h3>
            {analysisResults && (
              <button
                className="btn-secondary"
                onClick={() => setActiveView('downloads')}
              >
                <Download size={16} />
                Exportar
              </button>
            )}
          </div>

          {analysisResults ? (
            <div className="analysis-results">
              <div className="results-summary">
                <div className="summary-card">
                  <div className="summary-icon error">
                    <AlertTriangle size={20} />
                  </div>
                  <div className="summary-content">
                    <div className="summary-value">{analysisResults.summary?.total_errors || 0}</div>
                    <div className="summary-label">Errores</div>
                  </div>
                </div>

                <div className="summary-card">
                  <div className="summary-icon warning">
                    <AlertTriangle size={20} />
                  </div>
                  <div className="summary-content">
                    <div className="summary-value">{analysisResults.summary?.total_warnings || 0}</div>
                    <div className="summary-label">Advertencias</div>
                  </div>
                </div>

                <div className="summary-card">
                  <div className="summary-icon success">
                    <CheckCircle size={20} />
                  </div>
                  <div className="summary-content">
                    <div className="summary-value">{analysisResults.summary?.performance_score || 100}%</div>
                    <div className="summary-label">Rendimiento</div>
                  </div>
                </div>
              </div>

              <div className="results-details">
                {analysisResults.analysis?.errors?.length > 0 && (
                  <div className="results-section">
                    <h4 className="section-title error">
                      <AlertTriangle size={16} />
                      Errores Encontrados
                    </h4>
                    <div className="issues-list">
                      {analysisResults.analysis.errors.map((error, index) => (
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

                {analysisResults.analysis?.warnings?.length > 0 && (
                  <div className="results-section">
                    <h4 className="section-title warning">
                      <AlertTriangle size={16} />
                      Advertencias
                    </h4>
                    <div className="issues-list">
                      {analysisResults.analysis.warnings.map((warning, index) => (
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

                {analysisResults.analysis?.suggestions?.length > 0 && (
                  <div className="results-section">
                    <h4 className="section-title info">
                      <CheckCircle size={16} />
                      Sugerencias de Mejora
                    </h4>
                    <div className="suggestions-list">
                      {analysisResults.analysis.suggestions.map((suggestion, index) => (
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
              </div>
            </div>
          ) : (
            <div className="no-results">
              <Code size={48} className="no-results-icon" />
              <h3>Sin Resultados</h3>
              <p>Ejecuta un análisis SQL para ver los resultados aquí</p>
              <button
                className="btn-primary"
                onClick={analyzeSQL}
                disabled={!sqlContent.trim()}
              >
                <Play size={16} />
                Analizar SQL
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderFileManager = () => (
    <div className="view-container file-manager-view">
      <div className="view-header">
        <h1 className="view-title">
          <FolderOpen size={24} className="title-icon" />
          Gestión de Archivos SQL
        </h1>
        <div className="view-actions">
          <input
            type="file"
            id="file-upload"
            multiple
            accept=".sql,.txt"
            onChange={(e) => handleFileUpload(e.target.files)}
            style={{ display: 'none' }}
          />
          <button
            className="btn-secondary"
            onClick={() => document.getElementById('file-upload').click()}
          >
            <Upload size={16} />
            Cargar Archivos
          </button>
          {selectedFiles.length > 0 && (
            <button
              className="btn-danger"
              onClick={() => {
                setUploadedFiles(prev => prev.filter(file => !selectedFiles.includes(file.id)));
                setSelectedFiles([]);
                notify.success('Archivos eliminados', `${selectedFiles.length} archivos eliminados`);
              }}
            >
              <Trash2 size={16} />
              Eliminar Seleccionados
            </button>
          )}
        </div>
      </div>

      <div
        className={`file-drop-zone ${dragActive ? 'drag-active' : ''} ${uploadedFiles.length === 0 ? 'empty' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {uploadedFiles.length === 0 ? (
          <div className="empty-state">
            <Upload size={64} className="empty-icon" />
            <h3>No hay archivos cargados</h3>
            <p>Arrastra archivos SQL aquí o usa el botón "Cargar Archivos"</p>
            <button
              className="btn-primary"
              onClick={() => document.getElementById('file-upload').click()}
            >
              <Upload size={16} />
              Seleccionar Archivos
            </button>
          </div>
        ) : (
          <div className="files-grid">
            {uploadedFiles.map((file) => (
              <div
                key={file.id}
                className={`file-card ${selectedFiles.includes(file.id) ? 'selected' : ''}`}
                onClick={() => {
                  if (selectedFiles.includes(file.id)) {
                    setSelectedFiles(prev => prev.filter(id => id !== file.id));
                  } else {
                    setSelectedFiles(prev => [...prev, file.id]);
                  }
                }}
              >
                <div className="file-icon">
                  <FileText size={32} />
                </div>
                <div className="file-info">
                  <div className="file-name" title={file.name}>{file.name}</div>
                  <div className="file-meta">
                    <span>{(file.size / 1024).toFixed(1)} KB</span>
                    <span>{file.uploadDate.toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="file-actions">
                  <button
                    className="file-action-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSqlContent(file.content);
                      setActiveView('sql-analysis');
                      notify.info('Archivo cargado', `${file.name} cargado en el editor`);
                    }}
                    title="Abrir en editor"
                  >
                    <Edit size={16} />
                  </button>
                  <button
                    className="file-action-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setUploadedFiles(prev => prev.filter(f => f.id !== file.id));
                      notify.success('Archivo eliminado', `${file.name} eliminado`);
                    }}
                    title="Eliminar archivo"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {dragActive && (
          <div className="drag-overlay">
            <Upload size={48} />
            <p>Suelta los archivos SQL aquí</p>
          </div>
        )}
      </div>

      {uploadedFiles.length > 0 && (
        <div className="file-stats">
          <div className="stat-item">
            <span className="stat-label">Total de archivos:</span>
            <span className="stat-value">{uploadedFiles.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Tamaño total:</span>
            <span className="stat-value">
              {(uploadedFiles.reduce((total, file) => total + file.size, 0) / 1024).toFixed(1)} KB
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Seleccionados:</span>
            <span className="stat-value">{selectedFiles.length}</span>
          </div>
        </div>
      )}
    </div>
  );

  const renderTerminal = () => (
    <div className="view-container terminal-view">
      <div className="view-header">
        <h1 className="view-title">
          <Terminal size={24} className="title-icon" />
          Terminal Integrado
        </h1>
        <div className="view-actions">
          <button
            className="btn-secondary"
            onClick={() => setTerminalOutput([])}
          >
            <X size={16} />
            Limpiar Terminal
          </button>
        </div>
      </div>

      <div className="terminal-container">
        <div className="terminal-output">
          {terminalOutput.map((line) => (
            <div key={line.id} className={`terminal-line ${line.type}`}>
              <span className="terminal-timestamp">[{line.timestamp}]</span>
              <span className="terminal-content">{line.content}</span>
            </div>
          ))}
        </div>

        <div className="terminal-input-container">
          <span className="terminal-prompt">$</span>
          <input
            type="text"
            value={terminalInput}
            onChange={(e) => setTerminalInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && terminalInput.trim()) {
                executeTerminalCommand(terminalInput.trim());
              }
            }}
            placeholder="Escribe un comando..."
            className="terminal-input"
            autoFocus
          />
        </div>
      </div>

      <div className="terminal-help">
        <h3>Comandos Disponibles</h3>
        <div className="commands-grid">
          <div className="command-item">
            <code>help</code>
            <span>Mostrar ayuda de comandos</span>
          </div>
          <div className="command-item">
            <code>status</code>
            <span>Estado del sistema</span>
          </div>
          <div className="command-item">
            <code>analyze</code>
            <span>Ejecutar análisis SQL</span>
          </div>
          <div className="command-item">
            <code>connections</code>
            <span>Listar conexiones</span>
          </div>
          <div className="command-item">
            <code>clear</code>
            <span>Limpiar terminal</span>
          </div>
        </div>
      </div>
    </div>
  );

  // Placeholder views for remaining sections
  const renderConnections = () => (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">
          <Database size={24} className="title-icon" />
          Conexiones de Base de Datos
        </h1>
      </div>
      <div className="placeholder-content">
        <Database size={64} />
        <h3>Gestión de Conexiones</h3>
        <p>Configura y gestiona tus conexiones de base de datos</p>
      </div>
    </div>
  );

  const renderHistory = () => (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">
          <History size={24} className="title-icon" />
          Historial de Análisis
        </h1>
      </div>
      <div className="placeholder-content">
        <History size={64} />
        <h3>Historial de Análisis</h3>
        <p>Revisa tus análisis anteriores y resultados</p>
      </div>
    </div>
  );

  const renderDownloads = () => (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">
          <Download size={24} className="title-icon" />
          Gestión de Descargas
        </h1>
      </div>
      <div className="placeholder-content">
        <Download size={64} />
        <h3>Centro de Descargas</h3>
        <p>Exporta y descarga tus análisis en múltiples formatos</p>
      </div>
    </div>
  );

  const renderMetrics = () => (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">
          <Activity size={24} className="title-icon" />
          Métricas del Sistema
        </h1>
      </div>
      <div className="placeholder-content">
        <Activity size={64} />
        <h3>Monitoreo del Sistema</h3>
        <p>Métricas en tiempo real del rendimiento del sistema</p>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">
          <Settings size={24} className="title-icon" />
          Configuración
        </h1>
      </div>
      <div className="placeholder-content">
        <Settings size={64} />
        <h3>Configuración del Sistema</h3>
        <p>Personaliza la configuración de SQL Analyzer Enterprise</p>
      </div>
    </div>
  );

  const renderHelp = () => (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">
          <HelpCircle size={24} className="title-icon" />
          Ayuda y Documentación
        </h1>
      </div>
      <div className="placeholder-content">
        <HelpCircle size={64} />
        <h3>Centro de Ayuda</h3>
        <p>Documentación, tutoriales y soporte técnico</p>
      </div>
    </div>
  );

  return (
    <div className="enterprise-app">
      {renderSidebar()}

      <main className={`main-content ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        {renderMainContent()}
      </main>

      <NotificationSystem />
    </div>
  );
};

export default EnterpriseApp;
