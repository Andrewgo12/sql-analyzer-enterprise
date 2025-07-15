import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  BarChart3, 
  Clock, 
  Database, 
  Download, 
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Users,
  FileText,
  Zap,
  Shield
} from 'lucide-react';

const MetricsDashboard = ({ isVisible, onClose }) => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isVisible) {
      fetchMetrics();
      const interval = setInterval(fetchMetrics, 5000); // Update every 5 seconds
      return () => clearInterval(interval);
    }
  }, [isVisible]);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/metrics/dashboard');
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
        setError(null);
      } else {
        throw new Error('Failed to fetch metrics');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-500';
      case 'warning': return 'text-yellow-500';
      case 'critical': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-5 h-5" />;
      case 'warning': return <AlertTriangle className="w-5 h-5" />;
      case 'critical': return <AlertTriangle className="w-5 h-5" />;
      default: return <Activity className="w-5 h-5" />;
    }
  };

  if (!isVisible) return null;

  return (
    <div className="metrics-dashboard-overlay">
      <div className="metrics-dashboard">
        <div className="dashboard-header">
          <div className="dashboard-title">
            <BarChart3 size={24} />
            <h2>Métricas del Sistema</h2>
          </div>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="dashboard-content">
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Cargando métricas...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <AlertTriangle size={48} />
              <p>Error al cargar métricas: {error}</p>
              <button onClick={fetchMetrics} className="retry-button">
                Reintentar
              </button>
            </div>
          ) : metrics ? (
            <>
              {/* Overview Cards */}
              <div className="metrics-overview">
                <div className="metric-card">
                  <div className="metric-icon">
                    <FileText className="w-6 h-6" />
                  </div>
                  <div className="metric-content">
                    <div className="metric-value">{metrics.overview.total_analyses}</div>
                    <div className="metric-label">Análisis Totales</div>
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">
                    <TrendingUp className="w-6 h-6" />
                  </div>
                  <div className="metric-content">
                    <div className="metric-value">{metrics.overview.success_rate.toFixed(1)}%</div>
                    <div className="metric-label">Tasa de Éxito</div>
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">
                    <Clock className="w-6 h-6" />
                  </div>
                  <div className="metric-content">
                    <div className="metric-value">{metrics.overview.avg_processing_time.toFixed(2)}s</div>
                    <div className="metric-label">Tiempo Promedio</div>
                  </div>
                </div>

                <div className="metric-card">
                  <div className={`metric-icon ${getStatusColor(metrics.overview.system_status)}`}>
                    {getStatusIcon(metrics.overview.system_status)}
                  </div>
                  <div className="metric-content">
                    <div className="metric-value">{metrics.overview.system_status}</div>
                    <div className="metric-label">Estado del Sistema</div>
                  </div>
                </div>
              </div>

              {/* Real-time Metrics */}
              <div className="real-time-section">
                <h3>Métricas en Tiempo Real</h3>
                <div className="real-time-grid">
                  <div className="real-time-card">
                    <div className="real-time-header">
                      <Activity className="w-5 h-5" />
                      <span>Análisis Activos</span>
                    </div>
                    <div className="real-time-value">{metrics.real_time.active_analyses}</div>
                  </div>

                  <div className="real-time-card">
                    <div className="real-time-header">
                      <Zap className="w-5 h-5" />
                      <span>CPU</span>
                    </div>
                    <div className="real-time-value">{metrics.real_time.cpu_usage.toFixed(1)}%</div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${metrics.real_time.cpu_usage}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="real-time-card">
                    <div className="real-time-header">
                      <Database className="w-5 h-5" />
                      <span>Memoria</span>
                    </div>
                    <div className="real-time-value">{metrics.real_time.memory_usage.toFixed(1)}%</div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${metrics.real_time.memory_usage}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="real-time-card">
                    <div className="real-time-header">
                      <Shield className="w-5 h-5" />
                      <span>Tasa de Error</span>
                    </div>
                    <div className="real-time-value">{metrics.real_time.error_rate.toFixed(1)}%</div>
                  </div>
                </div>
              </div>

              {/* Trends Section */}
              <div className="trends-section">
                <h3>Tendencias de Uso</h3>
                <div className="trends-grid">
                  <div className="trend-card">
                    <h4>Motores de Base de Datos</h4>
                    <div className="trend-list">
                      {Object.entries(metrics.trends.database_engines)
                        .sort(([,a], [,b]) => b - a)
                        .slice(0, 5)
                        .map(([engine, count]) => (
                          <div key={engine} className="trend-item">
                            <span className="trend-name">{engine}</span>
                            <span className="trend-count">{count}</span>
                          </div>
                        ))}
                    </div>
                  </div>

                  <div className="trend-card">
                    <h4>Formatos de Exportación</h4>
                    <div className="trend-list">
                      {Object.entries(metrics.trends.export_formats)
                        .sort(([,a], [,b]) => b - a)
                        .slice(0, 5)
                        .map(([format, count]) => (
                          <div key={format} className="trend-item">
                            <span className="trend-name">{format}</span>
                            <span className="trend-count">{count}</span>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Performance Chart */}
              {metrics.trends.recent_performance && metrics.trends.recent_performance.length > 0 && (
                <div className="performance-section">
                  <h3>Rendimiento Reciente</h3>
                  <div className="performance-chart">
                    <div className="chart-container">
                      {metrics.trends.recent_performance.map((point, index) => (
                        <div 
                          key={index}
                          className="chart-bar"
                          style={{ 
                            height: `${Math.min(point.value * 10, 100)}%`,
                            left: `${(index / metrics.trends.recent_performance.length) * 100}%`
                          }}
                          title={`${point.value.toFixed(2)}s - ${new Date(point.timestamp).toLocaleTimeString()}`}
                        ></div>
                      ))}
                    </div>
                    <div className="chart-labels">
                      <span>Tiempo de Procesamiento (segundos)</span>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default MetricsDashboard;
