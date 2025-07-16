import React, { useState, useEffect, useMemo } from 'react';
import {
  Home,
  BarChart3,
  Database,
  FileText,
  Clock,
  TrendingUp,
  TrendingDown,
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
  Wifi,
  RefreshCw,
  Eye,
  Download,
  Upload,
  Settings,
  AlertCircle,
  Info,
  Star,
  Target,
  Layers,
  Globe,
  Lock,
  Unlock,
  PlayCircle,
  PauseCircle,
  StopCircle,
  MoreHorizontal,
  Filter,
  Search,
  Bell,
  BellOff
} from 'lucide-react';
import MetricsSystem from '../MetricsSystem';
import { Card, Button, Input, Dropdown } from '../ui';

const DashboardView = ({
  analysisHistory = [],
  connections = [],
  systemMetrics = {},
  onNavigate,
  uploadedFiles = [],
  recentActivity = []
}) => {
  const [timeRange, setTimeRange] = useState('7d');
  const [refreshing, setRefreshing] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState('overview');
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [viewMode, setViewMode] = useState('grid'); // grid, list, compact
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const [dashboardStats, setDashboardStats] = useState({
    totalAnalyses: 0,
    successfulAnalyses: 0,
    errorsFound: 0,
    performanceScore: 0,
    avgResponseTime: 0,
    totalConnections: 0,
    activeConnections: 0,
    totalFiles: 0,
    recentActivities: 0
  });

  // Utility function for trend calculation
  const calculateTrend = (data, type) => {
    if (data.length < 2) return { direction: 'stable', percentage: 0 };

    const midpoint = Math.floor(data.length / 2);
    const firstHalf = data.slice(0, midpoint);
    const secondHalf = data.slice(midpoint);

    let firstValue, secondValue;

    switch (type) {
      case 'count':
        firstValue = firstHalf.length;
        secondValue = secondHalf.length;
        break;
      case 'performance':
        firstValue = firstHalf.reduce((sum, a) => sum + (a.summary?.performance_score || 100), 0) / firstHalf.length;
        secondValue = secondHalf.reduce((sum, a) => sum + (a.summary?.performance_score || 100), 0) / secondHalf.length;
        break;
      case 'errors':
        firstValue = firstHalf.reduce((sum, a) => sum + (a.summary?.total_errors || 0), 0) / firstHalf.length;
        secondValue = secondHalf.reduce((sum, a) => sum + (a.summary?.total_errors || 0), 0) / secondHalf.length;
        break;
      default:
        return { direction: 'stable', percentage: 0 };
    }

    const change = ((secondValue - firstValue) / firstValue) * 100;
    const direction = Math.abs(change) < 5 ? 'stable' : change > 0 ? 'up' : 'down';

    return { direction, percentage: Math.abs(Math.round(change)) };
  };

  // Advanced statistics calculation with memoization
  const advancedStats = useMemo(() => {
    const now = new Date();
    const timeRangeMs = {
      '1d': 24 * 60 * 60 * 1000,
      '7d': 7 * 24 * 60 * 60 * 1000,
      '30d': 30 * 24 * 60 * 60 * 1000,
      '90d': 90 * 24 * 60 * 60 * 1000
    };

    const filteredHistory = analysisHistory.filter(analysis => {
      const analysisDate = new Date(analysis.timestamp || analysis.created_at);
      return now - analysisDate <= timeRangeMs[timeRange];
    });

    const totalAnalyses = filteredHistory.length;
    const successfulAnalyses = filteredHistory.filter(a => (a.summary?.total_errors || 0) === 0).length;
    const errorsFound = filteredHistory.reduce((total, a) => total + (a.summary?.total_errors || 0), 0);
    const avgResponseTime = filteredHistory.length > 0
      ? filteredHistory.reduce((total, a) => total + (a.processing_time || 0), 0) / filteredHistory.length
      : 0;

    const performanceScore = totalAnalyses > 0
      ? Math.round(filteredHistory.reduce((total, a) => total + (a.summary?.performance_score || 100), 0) / totalAnalyses)
      : 100;

    const activeConnections = connections.filter(c => c.status === 'active' || c.status === 'connected').length;
    const recentActivitiesCount = recentActivity.filter(activity => {
      const activityDate = new Date(activity.timestamp);
      return now - activityDate <= 24 * 60 * 60 * 1000; // Last 24 hours
    }).length;

    return {
      totalAnalyses,
      successfulAnalyses,
      errorsFound,
      performanceScore,
      avgResponseTime,
      totalConnections: connections.length,
      activeConnections,
      totalFiles: uploadedFiles.length,
      recentActivities: recentActivitiesCount,
      successRate: totalAnalyses > 0 ? Math.round((successfulAnalyses / totalAnalyses) * 100) : 100,
      errorRate: totalAnalyses > 0 ? Math.round((errorsFound / totalAnalyses) * 100) : 0,
      trend: {
        analyses: calculateTrend(filteredHistory, 'count'),
        performance: calculateTrend(filteredHistory, 'performance'),
        errors: calculateTrend(filteredHistory, 'errors')
      }
    };
  }, [analysisHistory, connections, uploadedFiles, recentActivity, timeRange]);

  useEffect(() => {
    setDashboardStats(advancedStats);
  }, [advancedStats]);

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      handleRefresh();
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [autoRefresh]);

  // Utility functions
  const getTimeRangeLabel = (range) => {
    const labels = {
      '1d': 'Últimas 24 horas',
      '7d': 'Últimos 7 días',
      '30d': 'Últimos 30 días',
      '90d': 'Últimos 90 días'
    };
    return labels[range] || labels['7d'];
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const formatTime = (ms) => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const getStatusColor = (status) => {
    const colors = {
      active: 'var(--success)',
      connected: 'var(--success)',
      inactive: 'var(--text-tertiary)',
      disconnected: 'var(--error)',
      error: 'var(--error)',
      warning: 'var(--warning)',
      success: 'var(--success)'
    };
    return colors[status] || 'var(--text-secondary)';
  };

  const getTrendIcon = (trend) => {
    switch (trend.direction) {
      case 'up': return <TrendingUp size={16} color="var(--success)" />;
      case 'down': return <TrendingDown size={16} color="var(--error)" />;
      default: return <Activity size={16} color="var(--text-secondary)" />;
    }
  };

  // Event handlers
  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      // Simulate refresh delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      // In real implementation, this would trigger data refresh
      console.log('Dashboard refreshed');
    } finally {
      setRefreshing(false);
    }
  };

  const handleQuickAction = (action) => {
    switch (action) {
      case 'new-analysis':
        onNavigate?.('sql-analysis');
        break;
      case 'view-metrics':
        onNavigate?.('metrics');
        break;
      case 'manage-connections':
        onNavigate?.('connections');
        break;
      case 'view-history':
        onNavigate?.('history');
        break;
      default:
        console.log(`Quick action: ${action}`);
    }
  };

  const filteredRecentActivity = useMemo(() => {
    return recentActivity
      .filter(activity => {
        if (filterStatus === 'all') return true;
        return activity.status === filterStatus;
      })
      .filter(activity => {
        if (!searchQuery) return true;
        return activity.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          activity.description?.toLowerCase().includes(searchQuery.toLowerCase());
      })
      .slice(0, 10); // Show only latest 10
  }, [recentActivity, filterStatus, searchQuery]);

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
      {/* Enhanced Header Section */}
      <div className="dashboard-header">
        <div className="header-main">
          <div className="header-title-section">
            <div className="title-icon-wrapper">
              <Home className="header-icon" size={28} />
            </div>
            <div className="title-content">
              <h1 className="dashboard-title">Dashboard Ejecutivo</h1>
              <p className="dashboard-subtitle">
                Vista general del sistema SQL Analyzer Enterprise - {getTimeRangeLabel(timeRange)}
              </p>
            </div>
          </div>

          <div className="header-controls">
            <div className="control-group">
              <Button
                variant="outline"
                size="small"
                onClick={handleRefresh}
                loading={refreshing}
                icon={RefreshCw}
                className="refresh-btn"
              >
                {refreshing ? 'Actualizando...' : 'Actualizar'}
              </Button>

              <Button
                variant={autoRefresh ? 'primary' : 'outline'}
                size="small"
                onClick={() => setAutoRefresh(!autoRefresh)}
                icon={autoRefresh ? PauseCircle : PlayCircle}
                className="auto-refresh-btn"
              >
                Auto-refresh
              </Button>

              <Button
                variant="outline"
                size="small"
                onClick={() => setNotificationsEnabled(!notificationsEnabled)}
                icon={notificationsEnabled ? Bell : BellOff}
                className="notifications-btn"
              >
                Notificaciones
              </Button>
            </div>

            <div className="time-range-controls">
              <Dropdown
                options={[
                  { value: '1d', label: 'Últimas 24 horas' },
                  { value: '7d', label: 'Últimos 7 días' },
                  { value: '30d', label: 'Últimos 30 días' },
                  { value: '90d', label: 'Últimos 90 días' }
                ]}
                value={timeRange}
                onChange={setTimeRange}
                className="time-range-dropdown"
              />

              <div className="view-mode-toggle">
                <Button
                  variant={viewMode === 'grid' ? 'primary' : 'outline'}
                  size="small"
                  onClick={() => setViewMode('grid')}
                  icon={Layers}
                />
                <Button
                  variant={viewMode === 'list' ? 'primary' : 'outline'}
                  size="small"
                  onClick={() => setViewMode('list')}
                  icon={Activity}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="status-indicators">
          <div className="status-item">
            <div className="status-dot success"></div>
            <span>Sistema Operativo</span>
          </div>
          <div className="status-item">
            <div className="status-dot success"></div>
            <span>Base de Datos</span>
          </div>
          <div className="status-item">
            <div className="status-dot warning"></div>
            <span>Cache</span>
          </div>
          <div className="status-item">
            <div className="status-dot success"></div>
            <span>API</span>
          </div>
        </div>
      </div>

      {/* Enhanced Metrics Overview */}
      <div className="metrics-overview">
        <div className="metrics-grid">
          {/* Primary Metrics */}
          <Card className="metric-card primary">
            <Card.Header>
              <div className="metric-header">
                <div className="metric-icon-wrapper primary">
                  <BarChart3 size={24} />
                </div>
                <div className="metric-info">
                  <h3>Análisis Totales</h3>
                  <div className="metric-trend">
                    {getTrendIcon(advancedStats.trend.analyses)}
                    <span>{advancedStats.trend.analyses.percentage}%</span>
                  </div>
                </div>
              </div>
            </Card.Header>
            <Card.Body>
              <div className="metric-value-display">
                <span className="metric-value">{formatNumber(dashboardStats.totalAnalyses)}</span>
                <span className="metric-period">{getTimeRangeLabel(timeRange)}</span>
              </div>
              <div className="metric-details">
                <div className="detail-item">
                  <CheckCircle size={14} />
                  <span>Exitosos: {dashboardStats.successfulAnalyses}</span>
                </div>
                <div className="detail-item">
                  <AlertTriangle size={14} />
                  <span>Con errores: {dashboardStats.totalAnalyses - dashboardStats.successfulAnalyses}</span>
                </div>
              </div>
            </Card.Body>
          </Card>

          <Card className="metric-card success">
            <Card.Header>
              <div className="metric-header">
                <div className="metric-icon-wrapper success">
                  <Target size={24} />
                </div>
                <div className="metric-info">
                  <h3>Tasa de Éxito</h3>
                  <div className="metric-trend">
                    {getTrendIcon(advancedStats.trend.performance)}
                    <span>{advancedStats.trend.performance.percentage}%</span>
                  </div>
                </div>
              </div>
            </Card.Header>
            <Card.Body>
              <div className="metric-value-display">
                <span className="metric-value">{dashboardStats.successRate}%</span>
                <span className="metric-period">Promedio</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill success"
                  style={{ width: `${dashboardStats.successRate}%` }}
                ></div>
              </div>
            </Card.Body>
          </Card>

          <Card className="metric-card warning">
            <Card.Header>
              <div className="metric-header">
                <div className="metric-icon-wrapper warning">
                  <AlertCircle size={24} />
                </div>
                <div className="metric-info">
                  <h3>Errores Detectados</h3>
                  <div className="metric-trend">
                    {getTrendIcon(advancedStats.trend.errors)}
                    <span>{advancedStats.trend.errors.percentage}%</span>
                  </div>
                </div>
              </div>
            </Card.Header>
            <Card.Body>
              <div className="metric-value-display">
                <span className="metric-value">{formatNumber(dashboardStats.errorsFound)}</span>
                <span className="metric-period">Total</span>
              </div>
              <div className="metric-details">
                <div className="detail-item">
                  <span>Promedio por análisis: {dashboardStats.totalAnalyses > 0 ? (dashboardStats.errorsFound / dashboardStats.totalAnalyses).toFixed(1) : '0'}</span>
                </div>
              </div>
            </Card.Body>
          </Card>

          <Card className="metric-card info">
            <Card.Header>
              <div className="metric-header">
                <div className="metric-icon-wrapper info">
                  <Zap size={24} />
                </div>
                <div className="metric-info">
                  <h3>Rendimiento</h3>
                  <div className="metric-status good">
                    <span>Óptimo</span>
                  </div>
                </div>
              </div>
            </Card.Header>
            <Card.Body>
              <div className="metric-value-display">
                <span className="metric-value">{formatTime(dashboardStats.avgResponseTime)}</span>
                <span className="metric-period">Tiempo promedio</span>
              </div>
              <div className="performance-indicator">
                <div className="performance-bar">
                  <div
                    className="performance-fill"
                    style={{
                      width: `${Math.min(100, (2000 - dashboardStats.avgResponseTime) / 20)}%`,
                      backgroundColor: dashboardStats.avgResponseTime < 1000 ? 'var(--success)' :
                        dashboardStats.avgResponseTime < 2000 ? 'var(--warning)' : 'var(--error)'
                    }}
                  ></div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </div>
      </div>

      {/* Enhanced Quick Actions */}
      <div className="quick-actions-section">
        <div className="section-header">
          <h2 className="section-title">
            <Zap size={20} />
            Acciones Rápidas
          </h2>
          <div className="section-controls">
            <Button
              variant="outline"
              size="small"
              icon={Settings}
              onClick={() => console.log('Customize actions')}
            >
              Personalizar
            </Button>
          </div>
        </div>

        <div className="quick-actions-grid">
          {quickActions.map((action) => (
            <Card key={action.id} className="quick-action-card" hover>
              <Card.Body>
                <div className="action-content">
                  <div className={`action-icon-wrapper ${action.color}`}>
                    <action.icon size={24} />
                  </div>
                  <div className="action-details">
                    <h3 className="action-title">{action.title}</h3>
                    <p className="action-description">{action.description}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="small"
                    icon={ArrowRight}
                    onClick={action.action}
                    className="action-button"
                  />
                </div>
              </Card.Body>
            </Card>
          ))}
        </div>
      </div>

      {/* Enhanced System Status */}
      <div className="system-status-section">
        <div className="section-header">
          <h2 className="section-title">
            <Activity size={20} />
            Estado del Sistema
          </h2>
          <div className="section-controls">
            <Button
              variant="outline"
              size="small"
              icon={Eye}
              onClick={() => onNavigate?.('metrics')}
            >
              Ver Detalles
            </Button>
          </div>
        </div>

        <div className="system-status-grid">
          {systemStatus.map((item, index) => (
            <Card key={index} className="status-card">
              <Card.Body>
                <div className="status-content">
                  <div className="status-header">
                    <div className="status-icon-wrapper">
                      <item.icon size={20} />
                    </div>
                    <div className="status-info">
                      <h4 className="status-name">{item.name}</h4>
                      <span className={`status-badge ${item.status}`}>
                        {item.status === 'good' ? 'Óptimo' :
                          item.status === 'warning' ? 'Advertencia' : 'Crítico'}
                      </span>
                    </div>
                  </div>

                  <div className="status-metrics">
                    <div className="status-value">{item.value}%</div>
                    <div className="status-progress">
                      <div className="progress-track">
                        <div
                          className={`progress-fill ${item.status}`}
                          style={{ width: `${item.value}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card.Body>
            </Card>
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

      {/* Enhanced Connection Status */}
      <div className="connections-overview">
        <div className="section-header">
          <h2 className="section-title">
            <Database size={20} />
            Conexiones de Base de Datos
          </h2>
          <div className="section-controls">
            <Button
              variant="outline"
              size="small"
              icon={Plus}
              onClick={() => onNavigate?.('connections')}
            >
              Nueva Conexión
            </Button>
            <Button
              variant="primary"
              size="small"
              icon={Settings}
              onClick={() => onNavigate?.('connections')}
            >
              Gestionar
            </Button>
          </div>
        </div>

        <div className="connections-grid">
          <Card className="connection-summary-card">
            <Card.Body>
              <div className="connection-summary">
                <div className="summary-item">
                  <div className="summary-icon-wrapper primary">
                    <Database size={24} />
                  </div>
                  <div className="summary-details">
                    <div className="summary-value">{dashboardStats.totalConnections}</div>
                    <div className="summary-label">Total Configuradas</div>
                  </div>
                </div>

                <div className="summary-item">
                  <div className="summary-icon-wrapper success">
                    <Wifi size={24} />
                  </div>
                  <div className="summary-details">
                    <div className="summary-value">{dashboardStats.activeConnections}</div>
                    <div className="summary-label">Activas</div>
                  </div>
                </div>

                <div className="summary-item">
                  <div className="summary-icon-wrapper warning">
                    <Shield size={24} />
                  </div>
                  <div className="summary-details">
                    <div className="summary-value">
                      {dashboardStats.totalConnections - dashboardStats.activeConnections}
                    </div>
                    <div className="summary-label">Inactivas</div>
                  </div>
                </div>
              </div>
            </Card.Body>
          </Card>

          {connections.slice(0, 3).map((connection, index) => (
            <Card key={index} className="connection-card" hover>
              <Card.Body>
                <div className="connection-info">
                  <div className="connection-header">
                    <div className="connection-icon-wrapper">
                      <Database size={20} />
                    </div>
                    <div className="connection-details">
                      <h4 className="connection-name">{connection.name || `Conexión ${index + 1}`}</h4>
                      <p className="connection-type">{connection.type || 'MySQL'}</p>
                    </div>
                    <div className={`connection-status-dot ${connection.status || 'inactive'}`}></div>
                  </div>

                  <div className="connection-meta">
                    <span className="connection-host">
                      <Globe size={12} />
                      {connection.host || 'localhost'}
                    </span>
                    <span className={`connection-status-text ${connection.status || 'inactive'}`}>
                      {connection.status === 'active' ? 'Conectado' : 'Desconectado'}
                    </span>
                  </div>
                </div>
              </Card.Body>
            </Card>
          ))}
        </div>
      </div>

      {/* Enhanced Real-time Metrics System */}
      <div className="metrics-system-section">
        <div className="section-header">
          <h2 className="section-title">
            <Activity size={20} />
            Monitoreo en Tiempo Real
          </h2>
          <div className="section-controls">
            <Button
              variant="outline"
              size="small"
              icon={RefreshCw}
              onClick={handleRefresh}
              loading={refreshing}
            >
              Actualizar
            </Button>
          </div>
        </div>

        <Card className="metrics-system-card">
          <Card.Body>
            <MetricsSystem
              isVisible={true}
              refreshInterval={autoRefresh ? 5000 : 0}
              showDetailed={true}
            />
          </Card.Body>
        </Card>
      </div>
    </div>
  );
};

export default DashboardView;
