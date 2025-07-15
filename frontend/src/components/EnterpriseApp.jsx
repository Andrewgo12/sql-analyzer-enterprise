import React, { useState, useEffect } from 'react';
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
  X
} from 'lucide-react';

import Sidebar from './Sidebar';
import MainWorkspace from './MainWorkspace';
import RightPanel from './RightPanel';
import BottomPanel from './BottomPanel';
import ConnectionModal from './modals/ConnectionModal';
import AnalysisModal from './modals/AnalysisModal';
import ExportModal from './modals/ExportModal';
import HelpModal from './modals/HelpModal';
import MetricsDashboard from './MetricsDashboard';
import NotificationSystem, { notify } from './NotificationSystem';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';

const EnterpriseApp = () => {
  // Application state
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rightPanelCollapsed, setRightPanelCollapsed] = useState(false);
  const [bottomPanelCollapsed, setBottomPanelCollapsed] = useState(false);

  // Modal states
  const [connectionModalOpen, setConnectionModalOpen] = useState(false);
  const [analysisModalOpen, setAnalysisModalOpen] = useState(false);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [metricsDashboardOpen, setMetricsDashboardOpen] = useState(false);
  const [helpModalOpen, setHelpModalOpen] = useState(false);

  // Data states
  const [connections, setConnections] = useState([]);
  const [currentConnection, setCurrentConnection] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [activeTabs, setActiveTabs] = useState([]);
  const [activeTabId, setActiveTabId] = useState(null);

  // Analysis states
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [logs, setLogs] = useState([]);

  // Load initial data
  useEffect(() => {
    loadAnalysisHistory();
    loadConnections();
  }, []);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onAnalyze: analyzeCurrentTab,
    onNewTab: () => createNewTab(),
    onCloseTab: () => {
      if (activeTabId) {
        closeTab(activeTabId);
      }
    },
    onSelectTab: (index) => {
      if (activeTabs[index]) {
        setActiveTabId(activeTabs[index].id);
      }
    },
    onOpenMetrics: () => setMetricsDashboardOpen(true),
    onOpenConnection: () => setConnectionModalOpen(true),
    onExport: () => {
      if (currentAnalysis) {
        setExportModalOpen(true);
      } else {
        notify.warning('Exportación no disponible', 'No hay análisis para exportar');
      }
    },
    onSave: () => {
      const currentTab = activeTabs.find(tab => tab.id === activeTabId);
      if (currentTab) {
        notify.info('Guardado', `Contenido de ${currentTab.title} guardado localmente`);
      }
    },
    onShowHelp: () => setHelpModalOpen(true)
  });

  const loadAnalysisHistory = async () => {
    try {
      // Load from localStorage or API
      const saved = localStorage.getItem('sql_analyzer_history');
      if (saved) {
        setAnalysisHistory(JSON.parse(saved));
      }
    } catch (error) {
      console.error('Error loading analysis history:', error);
    }
  };

  const loadConnections = async () => {
    try {
      // Load from localStorage or API
      const saved = localStorage.getItem('sql_analyzer_connections');
      if (saved) {
        setConnections(JSON.parse(saved));
      }
    } catch (error) {
      console.error('Error loading connections:', error);
    }
  };

  const addLog = (message, type = 'info') => {
    const newLog = {
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      message,
      type
    };
    setLogs(prev => [...prev, newLog]);
  };

  const createNewTab = (file = null) => {
    const newTab = {
      id: Date.now(),
      title: file ? file.name : 'Nueva Consulta',
      content: '',
      file: file,
      analysis: null,
      isDirty: false,
      type: 'sql'
    };

    setActiveTabs(prev => [...prev, newTab]);
    setActiveTabId(newTab.id);

    if (file) {
      addLog(`Archivo cargado: ${file.name}`, 'success');
    }
  };

  const closeTab = (tabId) => {
    setActiveTabs(prev => prev.filter(tab => tab.id !== tabId));

    if (activeTabId === tabId) {
      const remainingTabs = activeTabs.filter(tab => tab.id !== tabId);
      setActiveTabId(remainingTabs.length > 0 ? remainingTabs[0].id : null);
    }
  };

  const updateTabContent = (tabId, content) => {
    setActiveTabs(prev => prev.map(tab =>
      tab.id === tabId
        ? { ...tab, content, isDirty: true }
        : tab
    ));
  };

  const analyzeCurrentTab = async () => {
    const currentTab = activeTabs.find(tab => tab.id === activeTabId);
    if (!currentTab || !currentTab.content.trim()) {
      addLog('No hay contenido para analizar', 'warning');
      notify.warning('Análisis no disponible', 'No hay contenido SQL para analizar');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisProgress(0);
    addLog('Iniciando análisis...', 'info');
    notify.info('Análisis iniciado', `Analizando ${currentTab.title}...`);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setAnalysisProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Create FormData for file upload
      const formData = new FormData();
      const blob = new Blob([currentTab.content], { type: 'text/plain' });
      formData.append('file', blob, currentTab.title);

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData
      });

      clearInterval(progressInterval);
      setAnalysisProgress(100);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      // Update tab with analysis results
      setActiveTabs(prev => prev.map(tab =>
        tab.id === activeTabId
          ? { ...tab, analysis: result, isDirty: false }
          : tab
      ));

      setCurrentAnalysis(result);

      // Add to history
      const historyItem = {
        id: Date.now(),
        filename: currentTab.title,
        timestamp: new Date().toISOString(),
        summary: result.summary,
        analysis: result.analysis
      };

      setAnalysisHistory(prev => {
        const updated = [historyItem, ...prev.slice(0, 19)]; // Keep last 20
        localStorage.setItem('sql_analyzer_history', JSON.stringify(updated));
        return updated;
      });

      addLog(`Análisis completado: ${result.summary?.total_errors || 0} errores encontrados`, 'success');

      // Show success notification
      const errorCount = result.summary?.total_errors || 0;
      const performanceScore = result.summary?.performance_score || 100;

      if (errorCount === 0 && performanceScore >= 90) {
        notify.success('Análisis completado', 'SQL analizado sin errores críticos');
      } else if (errorCount > 0) {
        notify.warning('Análisis completado', `Se encontraron ${errorCount} errores`);
      } else {
        notify.info('Análisis completado', 'Revisa los resultados para más detalles');
      }

    } catch (error) {
      console.error('Analysis error:', error);
      addLog(`Error en análisis: ${error.message}`, 'error');
      notify.error('Error en análisis', error.message || 'Error desconocido durante el análisis');
    } finally {
      setIsAnalyzing(false);
      setAnalysisProgress(0);
    }
  };

  const exportAnalysis = async (format) => {
    if (!currentAnalysis) {
      addLog('No hay análisis para exportar', 'warning');
      notify.warning('Exportación no disponible', 'No hay análisis para exportar');
      return;
    }

    try {
      addLog(`Exportando en formato ${format}...`, 'info');
      notify.info('Exportación iniciada', `Generando archivo en formato ${format.toUpperCase()}...`);

      const response = await fetch(`/api/download?format=${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(currentAnalysis)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `analysis_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      addLog(`Exportación completada: ${format}`, 'success');
      notify.success('Exportación completada', `Archivo ${format.toUpperCase()} descargado exitosamente`);

    } catch (error) {
      console.error('Export error:', error);
      addLog(`Error en exportación: ${error.message}`, 'error');
      notify.error('Error en exportación', error.message || 'Error desconocido durante la exportación');
    }
  };

  const handleFileUpload = (files) => {
    Array.from(files).forEach(file => {
      if (file.type === 'text/plain' || file.name.endsWith('.sql')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const newTab = {
            id: Date.now() + Math.random(),
            title: file.name,
            content: e.target.result,
            file: file,
            analysis: null,
            isDirty: false,
            type: 'sql'
          };

          setActiveTabs(prev => [...prev, newTab]);
          setActiveTabId(newTab.id);
          addLog(`Archivo cargado: ${file.name}`, 'success');
        };
        reader.readAsText(file);
      } else {
        addLog(`Formato de archivo no soportado: ${file.name}`, 'warning');
      }
    });
  };

  return (
    <div className="enterprise-app">
      {/* Main Layout */}
      <div className="app-layout">
        {/* Sidebar */}
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          connections={connections}
          currentConnection={currentConnection}
          onConnectionSelect={setCurrentConnection}
          onNewConnection={() => setConnectionModalOpen(true)}
          analysisHistory={analysisHistory}
          onHistorySelect={(item) => {
            setCurrentAnalysis(item.analysis);
            addLog(`Cargado análisis: ${item.filename}`, 'info');
          }}
          onFileUpload={handleFileUpload}
        />

        {/* Main Workspace */}
        <MainWorkspace
          activeTabs={activeTabs}
          activeTabId={activeTabId}
          onTabSelect={setActiveTabId}
          onTabClose={closeTab}
          onTabContentChange={updateTabContent}
          onNewTab={() => createNewTab()}
          onAnalyze={analyzeCurrentTab}
          onOpenMetrics={() => setMetricsDashboardOpen(true)}
          isAnalyzing={isAnalyzing}
          analysisProgress={analysisProgress}
          currentAnalysis={currentAnalysis}
        />

        {/* Right Panel */}
        <RightPanel
          collapsed={rightPanelCollapsed}
          onToggle={() => setRightPanelCollapsed(!rightPanelCollapsed)}
          currentAnalysis={currentAnalysis}
          onExport={() => setExportModalOpen(true)}
          onAnalysisSettings={() => setAnalysisModalOpen(true)}
        />
      </div>

      {/* Bottom Panel */}
      <BottomPanel
        collapsed={bottomPanelCollapsed}
        onToggle={() => setBottomPanelCollapsed(!bottomPanelCollapsed)}
        logs={logs}
        onClearLogs={() => setLogs([])}
        isAnalyzing={isAnalyzing}
        analysisProgress={analysisProgress}
      />

      {/* Modals */}
      <ConnectionModal
        isOpen={connectionModalOpen}
        onClose={() => setConnectionModalOpen(false)}
        onSave={(connection) => {
          setConnections(prev => {
            const updated = [...prev, { ...connection, id: Date.now() }];
            localStorage.setItem('sql_analyzer_connections', JSON.stringify(updated));
            return updated;
          });
          setConnectionModalOpen(false);
          addLog(`Conexión guardada: ${connection.name}`, 'success');
        }}
      />

      <AnalysisModal
        isOpen={analysisModalOpen}
        onClose={() => setAnalysisModalOpen(false)}
        onAnalyze={(settings) => {
          // Apply analysis settings and run analysis
          setAnalysisModalOpen(false);
          analyzeCurrentTab();
        }}
      />

      <ExportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        onExport={(format, options) => {
          setExportModalOpen(false);
          exportAnalysis(format);
        }}
        currentAnalysis={currentAnalysis}
      />

      <MetricsDashboard
        isVisible={metricsDashboardOpen}
        onClose={() => setMetricsDashboardOpen(false)}
      />

      <HelpModal
        isOpen={helpModalOpen}
        onClose={() => setHelpModalOpen(false)}
      />

      <NotificationSystem />
    </div>
  );
};

export default EnterpriseApp;
