import React, { memo, useCallback, useMemo, useReducer, useEffect } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import { AnalysisProvider } from '../../contexts/AnalysisContext';
import { UIProvider } from '../../contexts/UIContext';
import { PerformanceProvider } from '../../contexts/PerformanceContext';
import Layout from './Layout';
import './OptimizedEnterpriseApp.css';

// Optimized state management with useReducer instead of multiple useState
const initialState = {
  // Core analysis state
  analysisResults: null,
  isAnalyzing: false,
  analysisError: null,

  // File management
  selectedFile: null,
  fileContent: '',

  // UI state
  activePanel: 'analysis',
  sidebarCollapsed: false,
  theme: 'light',

  // Performance metrics
  performanceMetrics: {
    responseTime: 0,
    memoryUsage: 0,
    cacheHitRate: 0
  },

  // Export state
  exportFormat: 'json',
  isExporting: false,

  // Database engine
  selectedEngine: 'mysql'
};

// Optimized reducer for state management
function appReducer(state, action) {
  switch (action.type) {
    case 'SET_ANALYSIS_LOADING':
      return {
        ...state,
        isAnalyzing: action.payload,
        analysisError: action.payload ? null : state.analysisError
      };

    case 'SET_ANALYSIS_RESULTS':
      return {
        ...state,
        analysisResults: action.payload,
        isAnalyzing: false,
        analysisError: null
      };

    case 'SET_ANALYSIS_ERROR':
      return {
        ...state,
        analysisError: action.payload,
        isAnalyzing: false
      };

    case 'SET_FILE':
      return {
        ...state,
        selectedFile: action.payload.file,
        fileContent: action.payload.content
      };

    case 'SET_ACTIVE_PANEL':
      return {
        ...state,
        activePanel: action.payload
      };

    case 'TOGGLE_SIDEBAR':
      return {
        ...state,
        sidebarCollapsed: !state.sidebarCollapsed
      };

    case 'SET_THEME':
      return {
        ...state,
        theme: action.payload
      };

    case 'UPDATE_PERFORMANCE_METRICS':
      return {
        ...state,
        performanceMetrics: {
          ...state.performanceMetrics,
          ...action.payload
        }
      };

    case 'SET_EXPORT_FORMAT':
      return {
        ...state,
        exportFormat: action.payload
      };

    case 'SET_EXPORT_LOADING':
      return {
        ...state,
        isExporting: action.payload
      };

    case 'SET_DATABASE_ENGINE':
      return {
        ...state,
        selectedEngine: action.payload
      };

    default:
      return state;
  }
}

// Error fallback component
const ErrorFallback = memo(({ error, resetErrorBoundary }) => (
  <div className="error-fallback" role="alert">
    <h2>Something went wrong:</h2>
    <pre>{error.message}</pre>
    <button onClick={resetErrorBoundary}>Try again</button>
  </div>
));

// Main optimized component
const OptimizedEnterpriseApp = memo(() => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Memoized action creators
  const actions = useMemo(() => ({
    setAnalysisLoading: (loading) => dispatch({ type: 'SET_ANALYSIS_LOADING', payload: loading }),
    setAnalysisResults: (results) => dispatch({ type: 'SET_ANALYSIS_RESULTS', payload: results }),
    setAnalysisError: (error) => dispatch({ type: 'SET_ANALYSIS_ERROR', payload: error }),
    setFile: (file, content) => dispatch({ type: 'SET_FILE', payload: { file, content } }),
    setActivePanel: (panel) => dispatch({ type: 'SET_ACTIVE_PANEL', payload: panel }),
    toggleSidebar: () => dispatch({ type: 'TOGGLE_SIDEBAR' }),
    setTheme: (theme) => dispatch({ type: 'SET_THEME', payload: theme }),
    updatePerformanceMetrics: (metrics) => dispatch({ type: 'UPDATE_PERFORMANCE_METRICS', payload: metrics }),
    setExportFormat: (format) => dispatch({ type: 'SET_EXPORT_FORMAT', payload: format }),
    setExportLoading: (loading) => dispatch({ type: 'SET_EXPORT_LOADING', payload: loading }),
    setDatabaseEngine: (engine) => dispatch({ type: 'SET_DATABASE_ENGINE', payload: engine })
  }), []);

  // Optimized API calls with error handling
  const analyzeSQL = useCallback(async (file, content) => {
    actions.setAnalysisLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('database_engine', state.selectedEngine);

      const startTime = performance.now();

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData
      });

      const endTime = performance.now();
      const responseTime = endTime - startTime;

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const results = await response.json();

      // Update performance metrics
      actions.updatePerformanceMetrics({
        responseTime: responseTime,
        lastAnalysis: new Date().toISOString()
      });

      actions.setAnalysisResults(results);

    } catch (error) {
      console.error('Analysis error:', error);
      actions.setAnalysisError(error.message);
    }
  }, [state.selectedEngine, actions]);

  // Optimized export function
  const exportResults = useCallback(async (format) => {
    if (!state.analysisResults) return;

    actions.setExportLoading(true);

    try {
      const response = await fetch(`/api/export/${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(state.analysisResults)
      });

      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis_results.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error('Export error:', error);
      actions.setAnalysisError(error.message);
    } finally {
      actions.setExportLoading(false);
    }
  }, [state.analysisResults, actions]);

  // Performance monitoring
  useEffect(() => {
    const updateMetrics = async () => {
      try {
        const response = await fetch('/api/health');
        if (response.ok) {
          const health = await response.json();
          actions.updatePerformanceMetrics({
            memoryUsage: health.performance?.memory_usage || 0,
            cacheHitRate: health.cache_stats?.lru_cache?.hit_rate || 0
          });
        }
      } catch (error) {
        console.warn('Failed to update performance metrics:', error);
      }
    };

    // Update metrics every 30 seconds
    const interval = setInterval(updateMetrics, 30000);
    updateMetrics(); // Initial update

    return () => clearInterval(interval);
  }, [actions]);

  // Memoized context values
  const analysisContextValue = useMemo(() => ({
    ...state,
    actions: {
      analyzeSQL,
      exportResults,
      setFile: actions.setFile,
      setDatabaseEngine: actions.setDatabaseEngine
    }
  }), [state, analyzeSQL, exportResults, actions]);

  const uiContextValue = useMemo(() => ({
    activePanel: state.activePanel,
    sidebarCollapsed: state.sidebarCollapsed,
    theme: state.theme,
    actions: {
      setActivePanel: actions.setActivePanel,
      toggleSidebar: actions.toggleSidebar,
      setTheme: actions.setTheme
    }
  }), [state.activePanel, state.sidebarCollapsed, state.theme, actions]);

  const performanceContextValue = useMemo(() => ({
    metrics: state.performanceMetrics,
    updateMetrics: actions.updatePerformanceMetrics
  }), [state.performanceMetrics, actions]);

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={() => window.location.reload()}
    >
      <div className={`optimized-enterprise-app theme-${state.theme}`}>
        <PerformanceProvider value={performanceContextValue}>
          <UIProvider value={uiContextValue}>
            <AnalysisProvider value={analysisContextValue}>
              <Layout />
            </AnalysisProvider>
          </UIProvider>
        </PerformanceProvider>
      </div>
    </ErrorBoundary>
  );
});

OptimizedEnterpriseApp.displayName = 'OptimizedEnterpriseApp';

export default OptimizedEnterpriseApp;
