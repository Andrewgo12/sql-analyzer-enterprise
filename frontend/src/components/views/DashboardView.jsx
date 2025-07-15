import React, { useState, useEffect } from 'react';
import {
  Home,
  BarChart3,
  Database,
  FileText,
  Clock,
  TrendingUp,
  Activity,
  Users,
  Shield,
  Zap,
  CheckCircle,
  AlertTriangle,
  Plus,
  ArrowRight,
  Calendar,
  Server,
  HardDrive,
  Cpu,
  Wifi
} from 'lucide-react';
import MetricsSystem from '../MetricsSystem';

const DashboardView = ({
  analysisHistory,
  connections,
  systemMetrics,
  onNavigate,
  uploadedFiles,
  recentActivity
}) => {
  const [timeRange, setTimeRange] = useState('7d');
  const [dashboardStats, setDashboardStats] = useState({
    totalAnalyses: 0,
    successfulAnalyses: 0,
    errorsFound: 0,
    performanceScore: 0
  });

  useEffect(() => {
    // Calculate dashboard statistics
    const stats = {
      totalAnalyses: analysisHistory.length,
      successfulAnalyses: analysisHistory.filter(a => a.summary?.total_errors === 0).length,
      errorsFound: analysisHistory.reduce((total, a) => total + (a.summary?.total_errors || 0), 0),
      performanceScore: analysisHistory.length > 0
        ? Math.round(analysisHistory.reduce((total, a) => total + (a.summary?.performance_score || 100), 0) / analysisHistory.length)
        : 100
    };
    setDashboardStats(stats);
  }, [analysisHistory]);

  const quickActions = [
    {
      id: 'new-analysis',
      title: 'Nuevo Análisis SQL',
      description: 'Crear un nuevo análisis de consulta SQL',
      icon: Plus,
      color: 'primary',
      action: () => onNavigate('sql-analysis')
    },
    {
      id: 'upload-file',
      title: 'Cargar Archivo SQL',
      description: 'Subir archivo SQL para análisis',
      icon: FileText,
      color: 'secondary',
      action: () => onNavigate('file-manager')
    },
    {
      id: 'manage-connections',
      title: 'Gestionar Conexiones',
      description: 'Configurar conexiones de base de datos',
      icon: Database,
      color: 'tertiary',
      action: () => onNavigate('connections')
    },
    {
      id: 'view-history',
      title: 'Ver Historial',
      description: 'Revisar análisis anteriores',
      icon: Clock,
      color: 'quaternary',
      action: () => onNavigate('history')
    }
  ];

  const metricCards = [
    {
      title: 'Análisis Totales',
      value: dashboardStats.totalAnalyses,
      change: '+12%',
      trend: 'up',
      icon: BarChart3,
      color: 'blue'
    },
    {
      title: 'Análisis Exitosos',
      value: dashboardStats.successfulAnalyses,
      change: '+8%',
      trend: 'up',
      icon: CheckCircle,
      color: 'green'
    },
    {
      title: 'Errores Detectados',
      value: dashboardStats.errorsFound,
      change: '-15%',
      trend: 'down',
      icon: AlertTriangle,
      color: 'orange'
    },
    {
      title: 'Puntuación Promedio',
      value: `${dashboardStats.performanceScore}%`,
      change: '+5%',
      trend: 'up',
      icon: TrendingUp,
      color: 'purple'
    }
  ];

  const systemStatus = [
    {
      name: 'CPU',
      value: systemMetrics.cpu,
      status: systemMetrics.cpu < 70 ? 'good' : systemMetrics.cpu < 85 ? 'warning' : 'critical',
      icon: Cpu
    },
    {
      name: 'Memoria',
      value: systemMetrics.memory,
      status: systemMetrics.memory < 70 ? 'good' : systemMetrics.memory < 85 ? 'warning' : 'critical',
      icon: HardDrive
    },
    {
      name: 'Disco',
      value: systemMetrics.disk,
      status: systemMetrics.disk < 70 ? 'good' : systemMetrics.disk < 85 ? 'warning' : 'critical',
      icon: Server
    },
    {
      name: 'Red',
      value: systemMetrics.network,
      status: 'good',
      icon: Wifi
    }
  ];

  return (
    <div className="dashboard-view">
      {/* Header Section */}
      <div className="dashboard-header">
        <div className="header-content">
          <div className="header-title">
            <Home className="header-icon" size={32} />
            <div>
              <h1>Dashboard</h1>
              <p>Vista general del sistema SQL Analyzer Enterprise</p>
            </div>
          </div>
          <div className="header-actions">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="time-range-selector"
            >
              <option value="24h">Últimas 24 horas</option>
              <option value="7d">Últimos 7 días</option>
              <option value="30d">Últimos 30 días</option>
              <option value="90d">Últimos 90 días</option>
            </select>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions-section">
        <h2>Acciones Rápidas</h2>
        <div className="quick-actions-grid">
          {quickActions.map((action) => (
            <button
              key={action.id}
              className={`quick-action-card ${action.color}`}
              onClick={action.action}
            >
              <div className="action-icon">
                <action.icon size={24} />
              </div>
              <div className="action-content">
                <h3>{action.title}</h3>
                <p>{action.description}</p>
              </div>
              <ArrowRight className="action-arrow" size={16} />
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Overview */}
      <div className="metrics-section">
        <h2>Métricas del Sistema</h2>
        <div className="metrics-grid">
          {metricCards.map((metric, index) => (
            <div key={index} className={`metric-card ${metric.color}`}>
              <div className="metric-header">
                <metric.icon className="metric-icon" size={20} />
                <span className={`metric-change ${metric.trend}`}>
                  {metric.change}
                </span>
              </div>
              <div className="metric-content">
                <div className="metric-value">{metric.value}</div>
                <div className="metric-title">{metric.title}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* System Status */}
      <div className="system-status-section">
        <h2>Estado del Sistema</h2>
        <div className="status-grid">
          {systemStatus.map((item, index) => (
            <div key={index} className="status-card">
              <div className="status-header">
                <item.icon className="status-icon" size={20} />
                <span className="status-name">{item.name}</span>
              </div>
              <div className="status-content">
                <div className="status-value">{item.value}%</div>
                <div className="status-bar">
                  <div
                    className={`status-fill ${item.status}`}
                    style={{ width: `${item.value}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      {recentActivity && recentActivity.length > 0 && (
        <div className="recent-activity-section">
          <div className="section-header">
            <h2>Actividad Reciente</h2>
            <button
              className="view-all-btn"
              onClick={() => onNavigate('history')}
            >
              Ver Todo
              <ArrowRight size={16} />
            </button>
          </div>
          <div className="activity-list">
            {recentActivity.slice(0, 5).map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">
                  <Activity size={16} />
                </div>
                <div className="activity-content">
                  <div className="activity-title">{activity.title}</div>
                  <div className="activity-meta">
                    <Calendar size={12} />
                    {new Date(activity.timestamp).toLocaleString()}
                  </div>
                </div>
                <div className="activity-status">
                  {activity.status === 'success' ? (
                    <CheckCircle className="status-success" size={16} />
                  ) : (
                    <AlertTriangle className="status-warning" size={16} />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Connection Status */}
      <div className="connections-overview">
        <div className="section-header">
          <h2>Conexiones de Base de Datos</h2>
          <button
            className="manage-btn"
            onClick={() => onNavigate('connections')}
          >
            Gestionar
            <ArrowRight size={16} />
          </button>
        </div>
        <div className="connections-summary">
          <div className="connection-stat">
            <Database className="connection-icon" size={20} />
            <div>
              <div className="stat-value">{connections.length}</div>
              <div className="stat-label">Conexiones Configuradas</div>
            </div>
          </div>
          <div className="connection-stat">
            <Shield className="connection-icon" size={20} />
            <div>
              <div className="stat-value">
                {connections.filter(c => c.status === 'active').length}
              </div>
              <div className="stat-label">Conexiones Activas</div>
            </div>
          </div>
        </div>
      </div>

      {/* Real-time Metrics System */}
      <div className="dashboard-section">
        <MetricsSystem isVisible={true} refreshInterval={5000} />
      </div>
    </div>
  );
};

export default DashboardView;
