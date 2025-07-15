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

  const renderDashboard = () => (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">Dashboard</h1>
        <p className="view-description">Vista general del sistema SQL Analyzer Enterprise</p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-header">
            <BarChart3 className="card-icon" />
            <h3>Análisis Realizados</h3>
          </div>
          <div className="card-content">
            <div className="metric-value">{analysisHistory.length}</div>
            <div className="metric-label">Total de análisis</div>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <Database className="card-icon" />
            <h3>Conexiones</h3>
          </div>
          <div className="card-content">
            <div className="metric-value">{connections.length}</div>
            <div className="metric-label">Conexiones configuradas</div>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <CheckCircle className="card-icon" />
            <h3>Estado del Sistema</h3>
          </div>
          <div className="card-content">
            <div className="metric-value status-healthy">Activo</div>
            <div className="metric-label">Sistema operativo</div>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <Clock className="card-icon" />
            <h3>Último Análisis</h3>
          </div>
          <div className="card-content">
            <div className="metric-value">
              {analysisHistory.length > 0
                ? new Date(analysisHistory[0].timestamp).toLocaleDateString()
                : 'Ninguno'
              }
            </div>
            <div className="metric-label">Fecha del último análisis</div>
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
            onClick={() => openModal('connections')}
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
    </div>
  );
