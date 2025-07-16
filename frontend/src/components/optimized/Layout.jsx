import React, { memo, Suspense, lazy } from 'react';
import { useSidebar, useActivePanel } from '../../contexts/UIContext';
import { usePerformanceMetrics } from '../../contexts/PerformanceContext';
import Sidebar from './Sidebar';
import Header from './Header';
import LoadingSpinner from './LoadingSpinner';
import './Layout.css';

// Lazy load components for better performance
const AnalysisWorkspace = lazy(() => import('./AnalysisWorkspace'));
const ResultsPanel = lazy(() => import('./ResultsPanel'));
const MetricsPanel = lazy(() => import('./MetricsPanel'));
const ExportPanel = lazy(() => import('./ExportPanel'));
const SettingsPanel = lazy(() => import('./SettingsPanel'));

// Component mapping for dynamic rendering
const PANEL_COMPONENTS = {
  analysis: AnalysisWorkspace,
  results: ResultsPanel,
  metrics: MetricsPanel,
  export: ExportPanel,
  settings: SettingsPanel
};

// Performance indicator component
const PerformanceIndicator = memo(() => {
  const metrics = usePerformanceMetrics();

  const getStatusColor = (value, thresholds) => {
    if (value < thresholds.good) return 'green';
    if (value < thresholds.warning) return 'yellow';
    return 'red';
  };

  const memoryColor = getStatusColor(metrics.memoryUsage, { good: 70, warning: 85 });
  const responseColor = getStatusColor(metrics.responseTime, { good: 500, warning: 1000 });

  return (
    <div className="performance-indicator">
      <div className="metric">
        <span className="label">Memory:</span>
        <span className={`value ${memoryColor}`}>{metrics.memoryUsage?.toFixed(1)}%</span>
      </div>
      <div className="metric">
        <span className="label">Response:</span>
        <span className={`value ${responseColor}`}>{metrics.responseTime?.toFixed(0)}ms</span>
      </div>
      <div className="metric">
        <span className="label">Cache:</span>
        <span className="value green">{metrics.cacheHitRate?.toFixed(1)}%</span>
      </div>
    </div>
  );
});

// Main content area component
const MainContent = memo(() => {
  const { activePanel } = useActivePanel();

  const ActiveComponent = PANEL_COMPONENTS[activePanel] || AnalysisWorkspace;

  return (
    <main className="main-content" role="main">
      <Suspense fallback={<LoadingSpinner />}>
        <ActiveComponent />
      </Suspense>
    </main>
  );
});

// Layout component with optimized structure
const Layout = memo(() => {
  const { sidebarCollapsed } = useSidebar();

  return (
    <div className={`layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      {/* Header */}
      <Header />

      {/* Main layout container */}
      <div className="layout-container">
        {/* Sidebar */}
        <Sidebar />

        {/* Main content area */}
        <div className="content-area">
          <MainContent />

          {/* Performance indicator */}
          <PerformanceIndicator />
        </div>
      </div>
    </div>
  );
});

Layout.displayName = 'Layout';

export default Layout;
