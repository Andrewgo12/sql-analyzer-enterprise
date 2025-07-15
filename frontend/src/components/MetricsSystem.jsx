import React, { useState, useEffect, useRef } from 'react';
import {
  Activity,
  BarChart3,
  Clock,
  Cpu,
  Database,
  HardDrive,
  Memory,
  Monitor,
  RefreshCw,
  Server,
  TrendingUp,
  Zap,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Gauge
} from 'lucide-react';
import { getDashboardMetrics, getSystemMetrics, checkHealth } from '../utils/api';

const MetricsSystem = ({ isVisible = true, refreshInterval = 5000 }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [systemMetrics, setSystemMetrics] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (isVisible) {
      loadAllMetrics();
      startAutoRefresh();
    } else {
      stopAutoRefresh();
    }

    return () => stopAutoRefresh();
  }, [isVisible, refreshInterval]);

  const loadAllMetrics = async () => {
    try {
      setLoading(true);
      setError(null);

      const [dashboard, system, health] = await Promise.all([
        getDashboardMetrics(),
        getSystemMetrics(),
        checkHealth()
      ]);

      setDashboardData(dashboard);
      setSystemMetrics(system);
      setHealthData(health);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to load metrics:', err);
      setError('Error cargando métricas del sistema');
    } finally {
      setLoading(false);
    }
  };

  const startAutoRefresh = () => {
    stopAutoRefresh();
    intervalRef.current = setInterval(loadAllMetrics, refreshInterval);
  };

  const stopAutoRefresh = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'good':
      case 'optimal':
        return '#10b981';
      case 'warning':
      case 'moderate':
        return '#f59e0b';
      case 'critical':
      case 'error':
      case 'high':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'good':
      case 'optimal':
        return CheckCircle;
      case 'warning':
      case 'moderate':
        return AlertTriangle;
      case 'critical':
      case 'error':
      case 'high':
        return XCircle;
      default:
        return Monitor;
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatPercentage = (value) => {
    return `${Math.round(value)}%`;
  };

  const formatDuration = (ms) => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  if (!isVisible) return null;

  if (loading) {
    return (
      <div className="metrics-system loading">
        <div className="loading-content">
          <RefreshCw className="animate-spin" size={24} />
          <p>Cargando métricas del sistema...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="metrics-system error">
        <div className="error-content">
          <AlertTriangle size={24} />
          <p>{error}</p>
          <button onClick={loadAllMetrics} className="retry-button">
            <RefreshCw size={16} />
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="metrics-system">
      <div className="metrics-header">
        <div className="header-title">
          <Activity size={20} />
          <h2>Métricas del Sistema</h2>
        </div>
        <div className="header-controls">
          <div className="last-update">
            <Clock size={14} />
            <span>
              {lastUpdate ? `Actualizado: ${lastUpdate.toLocaleTimeString()}` : 'Sin actualizar'}
            </span>
          </div>
          <button onClick={loadAllMetrics} className="refresh-button">
            <RefreshCw size={16} />
            Actualizar
          </button>
        </div>
      </div>

      <div className="metrics-grid">
        {/* System Health Overview */}
        {healthData && (
          <div className="metric-card health-overview">
            <div className="card-header">
              <Server size={18} />
              <h3>Estado del Sistema</h3>
            </div>
            <div className="health-status">
              <div className="status-indicator">
                {React.createElement(getStatusIcon(healthData.status), {
                  size: 24,
                  color: getStatusColor(healthData.status)
                })}
                <span 
                  className="status-text"
                  style={{ color: getStatusColor(healthData.status) }}
                >
                  {healthData.status?.toUpperCase() || 'UNKNOWN'}
                </span>
              </div>
              {healthData.performance && (
                <div className="performance-metrics">
                  <div className="perf-item">
                    <Zap size={14} />
                    <span>Tiempo respuesta: {formatDuration(healthData.performance.avg_response_time * 1000)}</span>
                  </div>
                  <div className="perf-item">
                    <Memory size={14} />
                    <span>Memoria: {formatPercentage(healthData.performance.memory_usage)}</span>
                  </div>
                  <div className="perf-item">
                    <BarChart3 size={14} />
                    <span>Solicitudes: {healthData.performance.requests_processed}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* System Metrics */}
        {systemMetrics && (
          <>
            <div className="metric-card">
              <div className="card-header">
                <Cpu size={18} />
                <h3>Rendimiento</h3>
              </div>
              <div className="metric-value">
                <span className="value">{formatDuration(systemMetrics.avg_response_time * 1000)}</span>
                <span className="label">Tiempo Promedio</span>
              </div>
              <div className="metric-details">
                <div className="detail-item">
                  <span>Solicitudes procesadas:</span>
                  <span>{systemMetrics.requests_processed}</span>
                </div>
              </div>
            </div>

            <div className="metric-card">
              <div className="card-header">
                <Memory size={18} />
                <h3>Memoria</h3>
              </div>
              <div className="metric-value">
                <span className="value">{formatPercentage(systemMetrics.memory?.usage || 0)}</span>
                <span className="label">Uso de Memoria</span>
              </div>
              {systemMetrics.memory && (
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ 
                      width: `${systemMetrics.memory.usage}%`,
                      backgroundColor: systemMetrics.memory.usage > 80 ? '#ef4444' : 
                                     systemMetrics.memory.usage > 60 ? '#f59e0b' : '#10b981'
                    }}
                  />
                </div>
              )}
            </div>

            <div className="metric-card">
              <div className="card-header">
                <Database size={18} />
                <h3>Cache</h3>
              </div>
              <div className="metric-value">
                <span className="value">{systemMetrics.cache?.hit_rate ? formatPercentage(systemMetrics.cache.hit_rate) : 'N/A'}</span>
                <span className="label">Tasa de Aciertos</span>
              </div>
              {systemMetrics.cache && (
                <div className="metric-details">
                  <div className="detail-item">
                    <span>Entradas:</span>
                    <span>{systemMetrics.cache.entries || 0}</span>
                  </div>
                  <div className="detail-item">
                    <span>Tamaño:</span>
                    <span>{formatBytes(systemMetrics.cache.size || 0)}</span>
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {/* Dashboard Overview */}
        {dashboardData?.overview && (
          <div className="metric-card overview-card">
            <div className="card-header">
              <Monitor size={18} />
              <h3>Resumen General</h3>
            </div>
            <div className="overview-grid">
              <div className="overview-item">
                <div className="overview-value">{dashboardData.overview.total_analyses || 0}</div>
                <div className="overview-label">Análisis Totales</div>
              </div>
              <div className="overview-item">
                <div className="overview-value">{dashboardData.overview.active_connections || 0}</div>
                <div className="overview-label">Conexiones Activas</div>
              </div>
              <div className="overview-item">
                <div className="overview-value">{dashboardData.overview.avg_processing_time || 0}s</div>
                <div className="overview-label">Tiempo Promedio</div>
              </div>
              <div className="overview-item">
                <div className="overview-value">{formatPercentage(dashboardData.overview.success_rate || 0)}</div>
                <div className="overview-label">Tasa de Éxito</div>
              </div>
            </div>
          </div>
        )}

        {/* Real-time Trends */}
        {dashboardData?.trends && (
          <div className="metric-card trends-card">
            <div className="card-header">
              <TrendingUp size={18} />
              <h3>Tendencias</h3>
            </div>
            <div className="trends-list">
              {dashboardData.trends.map((trend, index) => (
                <div key={index} className="trend-item">
                  <div className="trend-metric">{trend.metric}</div>
                  <div className="trend-change" style={{ 
                    color: trend.change > 0 ? '#10b981' : trend.change < 0 ? '#ef4444' : '#6b7280' 
                  }}>
                    {trend.change > 0 ? '+' : ''}{trend.change}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricsSystem;
