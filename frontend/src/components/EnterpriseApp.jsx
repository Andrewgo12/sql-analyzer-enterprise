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
import DatabaseEngineSelector from './DatabaseEngineSelector';
import ExportSystem from './ExportSystem';
import SystemHealthMonitor from './SystemHealthMonitor';

// Import all view components
import DashboardView from './views/DashboardView';
import SQLAnalysisView from './views/SQLAnalysisView';
import FileManagerView from './views/FileManagerView';
import ConnectionsView from './views/ConnectionsView';
import HistoryView from './views/HistoryView';
import TerminalView from './views/TerminalView';
import MetricsView from './views/MetricsView';

// Import styles
import './EnterpriseApp.css';

const EnterpriseApp = () => {
  // UI State
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeView, setActiveView] = useState('dashboard');
  const [activeModal, setActiveModal] = useState(null);
  const [showExportSystem, setShowExportSystem] = useState(false);

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
  const [selectedDatabaseEngine, setSelectedDatabaseEngine] = useState('mysql');
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0
  });

  // File Upload State
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
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

  // Load system metrics
  useEffect(() => {
    const loadSystemMetrics = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/metrics');
        if (response.ok) {
          const data = await response.json();
          setSystemMetrics({
            cpu: data.system?.cpu_usage || Math.floor(Math.random() * 30 + 10),
            memory: data.system?.memory_usage || Math.floor(Math.random() * 40 + 30),
            disk: data.system?.disk_usage || Math.floor(Math.random() * 20 + 40),
            network: data.system?.network_usage || Math.floor(Math.random() * 15 + 5)
          });
        } else {
          // Fallback to mock data
          setSystemMetrics({
            cpu: Math.floor(Math.random() * 30 + 10),
            memory: Math.floor(Math.random() * 40 + 30),
            disk: Math.floor(Math.random() * 20 + 40),
            network: Math.floor(Math.random() * 15 + 5)
          });
        }
      } catch (error) {
        console.warn('Failed to load system metrics, using mock data:', error);
        setSystemMetrics({
          cpu: Math.floor(Math.random() * 30 + 10),
          memory: Math.floor(Math.random() * 40 + 30),
          disk: Math.floor(Math.random() * 20 + 40),
          network: Math.floor(Math.random() * 15 + 5)
        });
      }
    };

    loadSystemMetrics();

    // Update metrics every 30 seconds
    const interval = setInterval(loadSystemMetrics, 30000);

    return () => clearInterval(interval);
  }, []);

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
      formData.append('database_engine', selectedDatabaseEngine);

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
  }, [sqlContent, selectedDatabaseEngine]);

  // File Handling Functions
  const handleFileUpload = useCallback((files) => {
    const fileArray = Array.isArray(files) ? files : Array.from(files);

    fileArray.forEach(file => {
      if (file.type === 'text/plain' || file.name.endsWith('.sql')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const fileData = {
            id: Date.now() + Math.random(),
            name: file.name,
            content: e.target.result,
            size: file.size,
            lastModified: new Date(file.lastModified),
            uploadDate: new Date(),
            type: 'sql'
          };

          setUploadedFiles(prev => [...prev, fileData]);
          notify.success('Archivo cargado', `${file.name} cargado correctamente`);
        };
        reader.readAsText(file);
      } else {
        notify.error('Tipo de archivo no válido', `${file.name}: Solo se permiten archivos .sql`);
      }
    });
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

  // Navigation and utility functions
  const handleNavigate = useCallback((viewId) => {
    setActiveView(viewId);
  }, []);

  const handleFileSelect = useCallback((file) => {
    setSqlContent(file.content);
    setActiveView('sql-analysis');
    notify.info('Archivo cargado', `${file.name} cargado en el editor`);
  }, []);

  const handleFileDelete = useCallback((fileId) => {
    if (window.confirm('¿Eliminar este archivo?')) {
      setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
      notify.success('Archivo eliminado', 'Archivo eliminado correctamente');
    }
  }, []);

  const handleFileEdit = useCallback((file) => {
    setSqlContent(file.content);
    setActiveView('sql-analysis');
    notify.info('Archivo abierto', `${file.name} abierto para edición`);
  }, []);

  const handleTestConnection = useCallback(async (connection) => {
    // Simulate connection test
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: Math.random() > 0.3 });
      }, 1000);
    });
  }, []);

  const handleSaveConnection = useCallback((connection) => {
    localStorage.setItem('sql_analyzer_connections', JSON.stringify(connections));
    notify.success('Conexión guardada', `${connection.name} guardada correctamente`);
  }, [connections]);

  const handleDeleteConnection = useCallback((connectionId) => {
    localStorage.setItem('sql_analyzer_connections', JSON.stringify(connections));
    notify.success('Conexión eliminada', 'Conexión eliminada correctamente');
  }, [connections]);

  const handleViewAnalysis = useCallback((analysis) => {
    setAnalysisResults(analysis.results);
    setSqlContent(analysis.content);
    setActiveView('sql-analysis');
  }, []);

  const handleDeleteAnalysis = useCallback((analysisId) => {
    if (window.confirm('¿Eliminar este análisis?')) {
      setAnalysisHistory(prev => prev.filter(a => a.id !== analysisId));
      notify.success('Análisis eliminado', 'Análisis eliminado del historial');
    }
  }, []);

  const handleExportAnalysis = useCallback((analysis) => {
    const exportData = JSON.stringify(analysis, null, 2);
    const blob = new Blob([exportData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis-${analysis.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
    notify.success('Análisis exportado', 'Análisis exportado correctamente');
  }, []);

  const handleRerunAnalysis = useCallback((analysis) => {
    setSqlContent(analysis.content);
    setActiveView('sql-analysis');
    setTimeout(() => {
      analyzeSQL();
    }, 500);
  }, [analyzeSQL]);

  const handleExecuteTerminalCommand = useCallback((command) => {
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

  const handleSave = useCallback(() => {
    localStorage.setItem('sql_analyzer_current_query', sqlContent);
    notify.info('Guardado', 'Consulta guardada localmente');
  }, [sqlContent]);

  const handleExport = useCallback(() => {
    if (analysisResults) {
      setShowExportSystem(true);
    } else {
      notify.warning('Exportación no disponible', 'No hay análisis para exportar');
    }
  }, [analysisResults]);

  const handleExportComplete = useCallback((exportRecord) => {
    notify.success('Exportado', `Archivo ${exportRecord.name} exportado correctamente`);
  }, []);

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
      case 'file-manager':
        return (
          <FileManagerView
            uploadedFiles={uploadedFiles}
            setUploadedFiles={setUploadedFiles}
            selectedFiles={selectedFiles}
            setSelectedFiles={setSelectedFiles}
            onFileSelect={handleFileSelect}
            onFileDelete={handleFileDelete}
            onFileEdit={handleFileEdit}
            dragActive={dragActive}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onFileUpload={handleFileUpload}
          />
        );
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
    <DashboardView
      analysisHistory={analysisHistory}
      connections={connections}
      systemMetrics={systemMetrics}
      onNavigate={handleNavigate}
      uploadedFiles={uploadedFiles}
      recentActivity={analysisHistory.slice(0, 5)}
    />
  );

  // Placeholder render functions for other views
  const renderSQLAnalysis = () => (
    <SQLAnalysisView
      sqlContent={sqlContent}
      setSqlContent={setSqlContent}
      analysisResults={analysisResults}
      isAnalyzing={isAnalyzing}
      analysisProgress={analysisProgress}
      onAnalyze={analyzeSQL}
      currentConnection={currentConnection}
      selectedDatabaseEngine={selectedDatabaseEngine}
      onDatabaseEngineChange={setSelectedDatabaseEngine}
      onSave={handleSave}
      onExport={handleExport}
      dragActive={dragActive}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    />
  );

  const renderConnections = () => (
    <ConnectionsView
      connections={connections}
      setConnections={setConnections}
      currentConnection={currentConnection}
      setCurrentConnection={setCurrentConnection}
      onTestConnection={handleTestConnection}
      onSaveConnection={handleSaveConnection}
      onDeleteConnection={handleDeleteConnection}
    />
  );

  const renderHistory = () => (
    <HistoryView
      analysisHistory={analysisHistory}
      setAnalysisHistory={setAnalysisHistory}
      onViewAnalysis={handleViewAnalysis}
      onDeleteAnalysis={handleDeleteAnalysis}
      onExportAnalysis={handleExportAnalysis}
      onRerunAnalysis={handleRerunAnalysis}
    />
  );

  const renderTerminal = () => (
    <TerminalView
      terminalOutput={terminalOutput}
      setTerminalOutput={setTerminalOutput}
      terminalInput={terminalInput}
      setTerminalInput={setTerminalInput}
      onExecuteCommand={handleExecuteTerminalCommand}
      systemMetrics={systemMetrics}
      connections={connections}
      onAnalyze={analyzeSQL}
    />
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
    <MetricsView
      systemMetrics={systemMetrics}
      connections={connections}
      analysisHistory={analysisHistory}
    />
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

  return (
    <div className="enterprise-app">
      {renderSidebar()}

      <main className={`main-content ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <SystemHealthMonitor
          isVisible={true}
          refreshInterval={5000}
          showDetailed={false}
        />
        {renderMainContent()}
      </main>

      <NotificationSystem />

      <ExportSystem
        analysisData={analysisResults}
        isOpen={showExportSystem}
        onClose={() => setShowExportSystem(false)}
        onExportComplete={handleExportComplete}
      />
    </div>
  );
};

export default EnterpriseApp;
