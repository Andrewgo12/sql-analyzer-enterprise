import React, { useState, useEffect, useRef } from 'react';
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
  Target
} from 'lucide-react';
import MetricsSystem from '../MetricsSystem';
import SystemHealthMonitor from '../SystemHealthMonitor';
import { getSystemMetrics, checkHealth } from '../utils/api';

const MetricsView = ({
  systemMetrics = {},
  connections = [],
  analysisHistory = []
}) => {
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
  const [thresholds, setThresholds] = useState({
    cpu: { warning: 70, critical: 90 },
    memory: { warning: 80, critical: 95 },
    disk: { warning: 85, critical: 95 },
    responseTime: { warning: 1000, critical: 2000 }
  });
  const intervalRef = useRef(null);

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

  const getMetricStatus = (value, thresholds) => {
    if (value >= thresholds.critical) return 'critical';
    if (value >= thresholds.warning) return 'warning';
    return 'good';
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
      <div className="metrics-header">
        <div className="header-title">
          <BarChart3 size={24} />
          <h2>Métricas del Sistema</h2>
        </div>

        <div className="header-controls">
          <div className="time-range-selector">
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
            >
              <option value="5m">Últimos 5 minutos</option>
              <option value="15m">Últimos 15 minutos</option>
              <option value="1h">Última hora</option>
              <option value="6h">Últimas 6 horas</option>
              <option value="24h">Últimas 24 horas</option>
            </select>
          </div>

          <div className="refresh-controls">
            <button
              className={`auto-refresh-btn ${autoRefresh ? 'active' : ''}`}
              onClick={() => setAutoRefresh(!autoRefresh)}
            >
              <RefreshCw size={16} />
              Auto
            </button>

            <button
              className="manual-refresh-btn"
              onClick={loadMetricsData}
              disabled={loading}
            >
              <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            </button>
          </div>

          <button
            className="settings-btn"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings size={16} />
          </button>
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
                  getMetricStatus(metricsData.system.cpu_usage, thresholds.cpu),
                  { direction: 'down', value: 2.3 }
                )}

                {renderMetricCard(
                  'Memoria',
                  Math.round(metricsData.system.memory_usage || 0),
                  '%',
                  <MemoryStick size={16} />,
                  getMetricStatus(metricsData.system.memory_usage, thresholds.memory),
                  { direction: 'up', value: 1.8 }
                )}

                {renderMetricCard(
                  'Disco',
                  Math.round(metricsData.system.disk_usage || 0),
                  '%',
                  <HardDrive size={16} />,
                  getMetricStatus(metricsData.system.disk_usage, thresholds.disk),
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
