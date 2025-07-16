import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle,
  Clock,
  Cpu,
  Database,
  HardDrive,
  MemoryStick,
  Monitor,
  RefreshCw,
  Server,
  TrendingDown,
  TrendingUp,
  Wifi,
  Zap,
  Bell,
  Settings,
  Download,
  Maximize2,
  Minimize2,
  Filter,
  Calendar,
  Target,
  PieChart,
  LineChart,
  AreaChart,
  Gauge,
  Shield,
  Globe,
  Users,
  FileText,
  Search,
  Eye,
  EyeOff,
  Play,
  Pause,
  Square,
  RotateCcw,
  Save,
  Upload,
  Info,
  AlertCircle,
  XCircle,
  Plus,
  Minus,
  MoreHorizontal,
  Grid,
  List,
  Layers,
  Sliders,
  BarChart,
  TrendingDown as TrendDown,
  TrendingUp as TrendUp,
  ArrowUp,
  ArrowDown,
  ArrowRight,
  Thermometer,
  Battery,
  Signal,
  Smartphone,
  Tablet,
  Laptop
} from 'lucide-react';
import MetricsSystem from '../MetricsSystem';
import SystemHealthMonitor from '../SystemHealthMonitor';
import { getSystemMetrics, checkHealth } from '../utils/api';
import { Card, Button, Input, Dropdown } from '../ui';

const MetricsView = ({
  systemMetrics = {},
  connections = [],
  analysisHistory = []
}) => {
  // Enhanced state management
  const [metricsData, setMetricsData] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(5000);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  const [alerts, setAlerts] = useState([]);
  const [expandedCard, setExpandedCard] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // grid, list, detailed
  const [selectedMetrics, setSelectedMetrics] = useState(['cpu', 'memory', 'disk', 'network']);
  const [chartType, setChartType] = useState('line'); // line, area, bar
  const [showPredictions, setShowPredictions] = useState(true);
  const [alertsEnabled, setAlertsEnabled] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [exportFormat, setExportFormat] = useState('json');
  const [filterQuery, setFilterQuery] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [historicalData, setHistoricalData] = useState([]);
  const [performanceBaseline, setPerformanceBaseline] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [customDashboard, setCustomDashboard] = useState([]);
  const [realTimeUpdates, setRealTimeUpdates] = useState(true);
  const [dataRetention, setDataRetention] = useState('7d');
  const [compressionEnabled, setCompressionEnabled] = useState(true);
  const [thresholds, setThresholds] = useState({
    cpu: { warning: 70, critical: 90, optimal: 50 },
    memory: { warning: 80, critical: 95, optimal: 60 },
    disk: { warning: 85, critical: 95, optimal: 70 },
    responseTime: { warning: 1000, critical: 2000, optimal: 500 },
    network: { warning: 80, critical: 95, optimal: 60 },
    error_rate: { warning: 5, critical: 10, optimal: 1 },
    throughput: { warning: 100, critical: 50, optimal: 200 },
    connections: { warning: 80, critical: 95, optimal: 60 }
  });

  // Enhanced refs
  const intervalRef = useRef(null);
  const chartRef = useRef(null);
  const alertSoundRef = useRef(null);
  const exportRef = useRef(null);
  const websocketRef = useRef(null);

  // Enhanced utility functions
  const calculateTrend = useCallback((data, timeframe = '1h') => {
    if (!data || data.length < 2) return { direction: 'stable', percentage: 0 };

    const recent = data.slice(-10);
    const older = data.slice(-20, -10);

    if (recent.length === 0 || older.length === 0) return { direction: 'stable', percentage: 0 };

    const recentAvg = recent.reduce((sum, val) => sum + val, 0) / recent.length;
    const olderAvg = older.reduce((sum, val) => sum + val, 0) / older.length;

    const change = ((recentAvg - olderAvg) / olderAvg) * 100;
    const direction = Math.abs(change) < 2 ? 'stable' : change > 0 ? 'up' : 'down';

    return { direction, percentage: Math.abs(Math.round(change)) };
  }, []);

  const detectAnomalies = useCallback((data, metric) => {
    if (!data || data.length < 10) return [];

    const anomalies = [];
    const threshold = thresholds[metric];

    if (!threshold) return anomalies;

    data.forEach((value, index) => {
      if (value > threshold.critical) {
        anomalies.push({
          timestamp: Date.now() - (data.length - index) * 60000,
          metric,
          value,
          severity: 'critical',
          message: `${metric.toUpperCase()} critical: ${value}%`
        });
      } else if (value > threshold.warning) {
        anomalies.push({
          timestamp: Date.now() - (data.length - index) * 60000,
          metric,
          value,
          severity: 'warning',
          message: `${metric.toUpperCase()} warning: ${value}%`
        });
      }
    });

    return anomalies;
  }, [thresholds]);

  const formatMetricValue = useCallback((value, metric) => {
    if (typeof value !== 'number') return 'N/A';

    switch (metric) {
      case 'responseTime':
        return value < 1000 ? `${Math.round(value)}ms` : `${(value / 1000).toFixed(2)}s`;
      case 'throughput':
        return `${value.toFixed(1)} req/s`;
      case 'error_rate':
        return `${value.toFixed(2)}%`;
      case 'connections':
        return Math.round(value).toString();
      default:
        return `${Math.round(value)}%`;
    }
  }, []);

  const getMetricStatus = useCallback((value, metric) => {
    const threshold = thresholds[metric];
    if (!threshold) return 'unknown';

    if (value >= threshold.critical) return 'critical';
    if (value >= threshold.warning) return 'warning';
    if (value <= threshold.optimal) return 'optimal';
    return 'normal';
  }, [thresholds]);

  const getStatusColor = useCallback((status) => {
    const colors = {
      optimal: 'var(--success)',
      normal: 'var(--info)',
      warning: 'var(--warning)',
      critical: 'var(--error)',
      unknown: 'var(--text-tertiary)'
    };
    return colors[status] || colors.unknown;
  }, []);

  const getStatusIcon = useCallback((status) => {
    switch (status) {
      case 'optimal': return CheckCircle;
      case 'normal': return Activity;
      case 'warning': return AlertTriangle;
      case 'critical': return XCircle;
      default: return Info;
    }
  }, []);

  useEffect(() => {
    loadMetricsData();
    if (autoRefresh) {
      startAutoRefresh();
    }
    return () => stopAutoRefresh();
  }, [autoRefresh, refreshInterval]);

  const loadMetricsData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [metrics, health] = await Promise.all([
        getSystemMetrics(),
        checkHealth()
      ]);

      setMetricsData(metrics);
      setHealthData(health);

      // Check for alerts
      checkAlerts(metrics, health);

    } catch (err) {
      console.error('Failed to load metrics:', err);
      setError('Error al cargar métricas del sistema');
    } finally {
      setLoading(false);
    }
  };

  const startAutoRefresh = () => {
    stopAutoRefresh();
    intervalRef.current = setInterval(loadMetricsData, refreshInterval);
  };

  const stopAutoRefresh = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const checkAlerts = (metrics, health) => {
    const newAlerts = [];
    const now = new Date();

    // CPU Alert
    if (metrics.system?.cpu_usage > thresholds.cpu.critical) {
      newAlerts.push({
        id: 'cpu-critical',
        type: 'critical',
        title: 'CPU Crítico',
        message: `Uso de CPU: ${metrics.system.cpu_usage}%`,
        timestamp: now
      });
    } else if (metrics.system?.cpu_usage > thresholds.cpu.warning) {
      newAlerts.push({
        id: 'cpu-warning',
        type: 'warning',
        title: 'CPU Alto',
        message: `Uso de CPU: ${metrics.system.cpu_usage}%`,
        timestamp: now
      });
    }

    // Memoria Alert
    if (metrics.system?.memory_usage > thresholds.memory.critical) {
      newAlerts.push({
        id: 'memory-critical',
        type: 'critical',
        title: 'Memoria Crítica',
        message: `Uso de memoria: ${metrics.system.memory_usage}%`,
        timestamp: now
      });
    }

    // Response Time Alert
    if (health.performance?.avg_response_time > thresholds.responseTime.critical / 1000) {
      newAlerts.push({
        id: 'response-critical',
        type: 'critical',
        title: 'Tiempo de Respuesta Alto',
        message: `Tiempo promedio: ${(health.performance.avg_response_time * 1000).toFixed(0)}ms`,
        timestamp: now
      });
    }

    setAlerts(newAlerts);
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatUptime = (seconds) => {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const renderMetricCard = (title, value, unit, icon, status, trend) => (
    <div className={`metric-card ${status} ${expandedCard === title ? 'expanded' : ''}`}>
      <div className="metric-header">
        <div className="metric-title">
          {icon}
          <span>{title}</span>
        </div>
        <div className="metric-actions">
          {trend && (
            <div className={`metric-trend ${trend.direction}`}>
              {trend.direction === 'up' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
              <span>{trend.value}%</span>
            </div>
          )}
          <button
            className="expand-btn"
            onClick={() => setExpandedCard(expandedCard === title ? null : title)}
          >
            {expandedCard === title ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
        </div>
      </div>

      <div className="metric-value">
        <span className="value">{value}</span>
        <span className="unit">{unit}</span>
      </div>

      <div className="metric-progress">
        <div
          className={`progress-bar ${status}`}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>

      {expandedCard === title && (
        <div className="metric-details">
          <div className="detail-item">
            <span>Estado:</span>
            <span className={`status-badge ${status}`}>
              {status === 'good' ? 'Normal' : status === 'warning' ? 'Advertencia' : 'Crítico'}
            </span>
          </div>
          <div className="detail-item">
            <span>Umbral Advertencia:</span>
            <span>{thresholds[title.toLowerCase()]?.warning || 'N/A'}%</span>
          </div>
          <div className="detail-item">
            <span>Umbral Crítico:</span>
            <span>{thresholds[title.toLowerCase()]?.critical || 'N/A'}%</span>
          </div>
        </div>
      )}
    </div>
  );

  const renderAlerts = () => (
    <div className="alerts-section">
      <div className="section-header">
        <h3>
          <Bell size={16} />
          Alertas del Sistema ({alerts.length})
        </h3>
        <button className="clear-alerts-btn" onClick={() => setAlerts([])}>
          Limpiar Todo
        </button>
      </div>

      {alerts.length === 0 ? (
        <div className="no-alerts">
          <CheckCircle size={24} />
          <span>No hay alertas activas</span>
        </div>
      ) : (
        <div className="alerts-list">
          {alerts.map(alert => (
            <div key={alert.id} className={`alert-item ${alert.type}`}>
              <div className="alert-icon">
                {alert.type === 'critical' ? (
                  <AlertTriangle size={16} />
                ) : (
                  <AlertTriangle size={16} />
                )}
              </div>
              <div className="alert-content">
                <div className="alert-title">{alert.title}</div>
                <div className="alert-message">{alert.message}</div>
                <div className="alert-time">
                  {alert.timestamp.toLocaleTimeString()}
                </div>
              </div>
              <button
                className="dismiss-btn"
                onClick={() => setAlerts(prev => prev.filter(a => a.id !== alert.id))}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  if (loading && !metricsData) {
    return (
      <div className="metrics-view loading">
        <div className="loading-content">
          <RefreshCw className="animate-spin" size={24} />
          <span>Cargando métricas del sistema...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="metrics-view">
      {/* Enhanced Header */}
      <div className="metrics-header">
        <div className="header-main">
          <div className="header-title-section">
            <div className="title-icon-wrapper">
              <BarChart3 size={28} />
            </div>
            <div className="title-content">
              <h1 className="metrics-title">Métricas del Sistema</h1>
              <p className="metrics-subtitle">
                Monitoreo en tiempo real del rendimiento y estado del sistema
              </p>
            </div>
          </div>

          <div className="header-controls">
            <div className="control-group">
              <Button
                variant={autoRefresh ? 'primary' : 'outline'}
                size="small"
                onClick={() => setAutoRefresh(!autoRefresh)}
                icon={autoRefresh ? Pause : Play}
                className="auto-refresh-btn"
              >
                {autoRefresh ? 'Pausar' : 'Iniciar'} Auto-refresh
              </Button>

              <Button
                variant="outline"
                size="small"
                onClick={loadMetricsData}
                loading={loading}
                icon={RefreshCw}
                className="manual-refresh-btn"
              >
                Actualizar
              </Button>

              <Button
                variant="outline"
                size="small"
                onClick={() => setShowSettings(!showSettings)}
                icon={Settings}
                className="settings-btn"
              >
                Configurar
              </Button>
            </div>

            <div className="view-controls">
              <Dropdown
                options={[
                  { value: '5m', label: 'Últimos 5 minutos' },
                  { value: '15m', label: 'Últimos 15 minutos' },
                  { value: '1h', label: 'Última hora' },
                  { value: '6h', label: 'Últimas 6 horas' },
                  { value: '24h', label: 'Últimas 24 horas' },
                  { value: '7d', label: 'Últimos 7 días' }
                ]}
                value={selectedTimeRange}
                onChange={setSelectedTimeRange}
                className="time-range-dropdown"
              />

              <div className="view-mode-toggle">
                <Button
                  variant={viewMode === 'grid' ? 'primary' : 'outline'}
                  size="small"
                  onClick={() => setViewMode('grid')}
                  icon={Grid}
                />
                <Button
                  variant={viewMode === 'list' ? 'primary' : 'outline'}
                  size="small"
                  onClick={() => setViewMode('list')}
                  icon={List}
                />
                <Button
                  variant={viewMode === 'detailed' ? 'primary' : 'outline'}
                  size="small"
                  onClick={() => setViewMode('detailed')}
                  icon={Layers}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div className="status-bar">
          <div className="status-indicators">
            <div className="status-item">
              <div className={`status-dot ${healthData?.overall === 'healthy' ? 'success' : 'warning'}`}></div>
              <span>Sistema: {healthData?.overall === 'healthy' ? 'Saludable' : 'Advertencia'}</span>
            </div>
            <div className="status-item">
              <div className="status-dot success"></div>
              <span>Conexiones: {connections.filter(c => c.status === 'active').length}/{connections.length}</span>
            </div>
            <div className="status-item">
              <div className="status-dot info"></div>
              <span>Última actualización: {new Date().toLocaleTimeString()}</span>
            </div>
            {anomalies.length > 0 && (
              <div className="status-item warning">
                <AlertTriangle size={14} />
                <span>{anomalies.length} anomalía{anomalies.length > 1 ? 's' : ''} detectada{anomalies.length > 1 ? 's' : ''}</span>
              </div>
            )}
          </div>

          <div className="status-actions">
            <Button
              variant="ghost"
              size="small"
              onClick={() => setAlertsEnabled(!alertsEnabled)}
              icon={alertsEnabled ? Bell : BellOff}
            >
              Alertas
            </Button>
            <Button
              variant="ghost"
              size="small"
              onClick={() => console.log('Export metrics')}
              icon={Download}
            >
              Exportar
            </Button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <AlertTriangle size={16} />
          <span>{error}</span>
          <button onClick={loadMetricsData}>Reintentar</button>
        </div>
      )}

      <div className="metrics-content">
        {/* System Health Monitor */}
        <div className="health-section">
          <SystemHealthMonitor
            isVisible={true}
            refreshInterval={refreshInterval}
            showDetailed={true}
          />
        </div>

        {/* Real-time Metrics */}
        <div className="realtime-metrics">
          <MetricsSystem
            isVisible={true}
            refreshInterval={refreshInterval}
          />
        </div>

        {/* Alerts Section */}
        {renderAlerts()}

        {/* Performance Overview */}
        <div className="performance-overview">
          <h3>Rendimiento del Sistema</h3>
          <div className="performance-grid">
            {metricsData?.system && (
              <>
                {renderMetricCard(
                  'CPU',
                  Math.round(metricsData.system.cpu_usage || 0),
                  '%',
                  <Cpu size={16} />,
                  getMetricStatus(metricsData.system.cpu_usage, 'cpu'),
                  { direction: 'down', value: 2.3 }
                )}

                {renderMetricCard(
                  'Memoria',
                  Math.round(metricsData.system.memory_usage || 0),
                  '%',
                  <MemoryStick size={16} />,
                  getMetricStatus(metricsData.system.memory_usage, 'memory'),
                  { direction: 'up', value: 1.8 }
                )}

                {renderMetricCard(
                  'Disco',
                  Math.round(metricsData.system.disk_usage || 0),
                  '%',
                  <HardDrive size={16} />,
                  getMetricStatus(metricsData.system.disk_usage, 'disk'),
                  { direction: 'up', value: 0.5 }
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsView;
