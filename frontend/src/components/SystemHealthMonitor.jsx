import React, { useState, useEffect, useRef } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Cpu,
  Database,
  HardDrive,
  Memory,
  Monitor,
  RefreshCw,
  Server,
  Shield,
  Wifi,
  XCircle,
  Zap,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import { checkHealth, getSystemMetrics } from '../utils/api';

const SystemHealthMonitor = ({ 
  isVisible = true, 
  refreshInterval = 3000,
  showDetailed = false 
}) => {
  const [healthData, setHealthData] = useState(null);
  const [systemMetrics, setSystemMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connected');
  const [healthHistory, setHealthHistory] = useState([]);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (isVisible) {
      loadHealthData();
      startHealthMonitoring();
    } else {
      stopHealthMonitoring();
    }

    return () => stopHealthMonitoring();
  }, [isVisible, refreshInterval]);

  const loadHealthData = async () => {
    try {
      setLoading(true);
      setError(null);
      setConnectionStatus('connecting');

      const [health, metrics] = await Promise.all([
        checkHealth(),
        getSystemMetrics()
      ]);

      setHealthData(health);
      setSystemMetrics(metrics);
      setConnectionStatus('connected');
      setLastUpdate(new Date());

      // Add to health history
      setHealthHistory(prev => [
        {
          timestamp: new Date(),
          status: health.status,
          responseTime: health.performance?.avg_response_time || 0,
          memoryUsage: health.performance?.memory_usage || 0
        },
        ...prev.slice(0, 19) // Keep last 20 entries
      ]);

    } catch (err) {
      console.error('Health monitoring failed:', err);
      setError('Error de conexión con el servidor');
      setConnectionStatus('disconnected');
    } finally {
      setLoading(false);
    }
  };

  const startHealthMonitoring = () => {
    stopHealthMonitoring();
    intervalRef.current = setInterval(loadHealthData, refreshInterval);
  };

  const stopHealthMonitoring = () => {
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

  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Wifi size={16} color="#10b981" />;
      case 'connecting':
        return <RefreshCw size={16} color="#f59e0b" className="animate-spin" />;
      case 'disconnected':
        return <Wifi size={16} color="#ef4444" />;
      default:
        return <Monitor size={16} color="#6b7280" />;
    }
  };

  const formatUptime = (seconds) => {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getHealthTrend = () => {
    if (healthHistory.length < 2) return null;
    const recent = healthHistory[0];
    const previous = healthHistory[1];
    
    if (recent.responseTime < previous.responseTime) {
      return { direction: 'up', icon: TrendingUp, color: '#10b981' };
    } else if (recent.responseTime > previous.responseTime) {
      return { direction: 'down', icon: TrendingDown, color: '#ef4444' };
    }
    return null;
  };

  if (!isVisible) return null;

  if (loading && !healthData) {
    return (
      <div className="health-monitor loading">
        <div className="loading-content">
          <RefreshCw className="animate-spin" size={20} />
          <span>Verificando estado del sistema...</span>
        </div>
      </div>
    );
  }

  const StatusIcon = healthData ? getStatusIcon(healthData.status) : Monitor;
  const statusColor = healthData ? getStatusColor(healthData.status) : '#6b7280';
  const trend = getHealthTrend();

  return (
    <div className={`health-monitor ${showDetailed ? 'detailed' : 'compact'}`}>
      <div className="health-header">
        <div className="health-status">
          <StatusIcon size={20} color={statusColor} />
          <span 
            className="status-text"
            style={{ color: statusColor }}
          >
            {healthData?.status?.toUpperCase() || 'UNKNOWN'}
          </span>
          {trend && (
            <trend.icon size={16} color={trend.color} />
          )}
        </div>
        
        <div className="health-connection">
          {getConnectionIcon()}
          <span className="connection-text">
            {connectionStatus === 'connected' ? 'Conectado' : 
             connectionStatus === 'connecting' ? 'Conectando...' : 'Desconectado'}
          </span>
        </div>

        <div className="health-update">
          <Clock size={14} />
          <span>
            {lastUpdate ? lastUpdate.toLocaleTimeString() : '--:--'}
          </span>
        </div>
      </div>

      {error && (
        <div className="health-error">
          <AlertTriangle size={16} />
          <span>{error}</span>
          <button onClick={loadHealthData} className="retry-btn">
            <RefreshCw size={14} />
          </button>
        </div>
      )}

      {showDetailed && healthData && (
        <div className="health-details">
          <div className="health-metrics">
            {healthData.performance && (
              <>
                <div className="metric-item">
                  <Zap size={16} />
                  <span className="metric-label">Tiempo Respuesta:</span>
                  <span className="metric-value">
                    {(healthData.performance.avg_response_time * 1000).toFixed(0)}ms
                  </span>
                </div>
                
                <div className="metric-item">
                  <Memory size={16} />
                  <span className="metric-label">Memoria:</span>
                  <span className="metric-value">
                    {Math.round(healthData.performance.memory_usage)}%
                  </span>
                </div>
                
                <div className="metric-item">
                  <Activity size={16} />
                  <span className="metric-label">Solicitudes:</span>
                  <span className="metric-value">
                    {healthData.performance.requests_processed}
                  </span>
                </div>
              </>
            )}

            {healthData.system && (
              <>
                <div className="metric-item">
                  <Server size={16} />
                  <span className="metric-label">Uptime:</span>
                  <span className="metric-value">
                    {formatUptime(healthData.system.uptime)}
                  </span>
                </div>
                
                <div className="metric-item">
                  <HardDrive size={16} />
                  <span className="metric-label">Disco:</span>
                  <span className="metric-value">
                    {formatBytes(healthData.system.disk_free)} libre
                  </span>
                </div>
              </>
            )}

            {systemMetrics?.cache && (
              <div className="metric-item">
                <Database size={16} />
                <span className="metric-label">Cache:</span>
                <span className="metric-value">
                  {Math.round(systemMetrics.cache.hit_rate || 0)}% hits
                </span>
              </div>
            )}
          </div>

          {healthData.components && (
            <div className="component-status">
              <h4>Estado de Componentes</h4>
              <div className="components-grid">
                {Object.entries(healthData.components).map(([component, status]) => {
                  const ComponentIcon = getStatusIcon(status);
                  const componentColor = getStatusColor(status);
                  
                  return (
                    <div key={component} className="component-item">
                      <ComponentIcon size={14} color={componentColor} />
                      <span className="component-name">{component}</span>
                      <span 
                        className="component-status"
                        style={{ color: componentColor }}
                      >
                        {status}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SystemHealthMonitor;
