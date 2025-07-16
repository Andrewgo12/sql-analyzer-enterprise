import React, { memo } from 'react';
import {
  Bell,
  Search,
  User,
  Settings,
  LogOut,
  Shield,
  Zap,
  Clock
} from 'lucide-react';
import { usePerformanceMetrics } from '../../contexts/PerformanceContext';

const Header = memo(() => {
  const { metrics } = usePerformanceMetrics();

  const getStatusColor = (value, thresholds) => {
    if (value <= thresholds.good) return 'text-green-500';
    if (value <= thresholds.warning) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <header className="header">
      <div className="header-content">
        {/* Left Section - Search */}
        <div className="header-left">
          <div className="search-container">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              placeholder="Buscar análisis, conexiones..."
              className="search-input"
            />
          </div>
        </div>

        {/* Center Section - Performance Metrics */}
        <div className="header-center">
          <div className="performance-indicators">
            <div className="metric-item">
              <Zap size={14} className="metric-icon" />
              <span className="metric-label">CPU:</span>
              <span className={`metric-value ${getStatusColor(metrics.cpuUsage, { good: 70, warning: 85 })}`}>
                {metrics.cpuUsage?.toFixed(1)}%
              </span>
            </div>
            
            <div className="metric-item">
              <Shield size={14} className="metric-icon" />
              <span className="metric-label">Memoria:</span>
              <span className={`metric-value ${getStatusColor(metrics.memoryUsage, { good: 70, warning: 85 })}`}>
                {metrics.memoryUsage?.toFixed(1)}%
              </span>
            </div>
            
            <div className="metric-item">
              <Clock size={14} className="metric-icon" />
              <span className="metric-label">Respuesta:</span>
              <span className={`metric-value ${getStatusColor(metrics.responseTime, { good: 500, warning: 1000 })}`}>
                {metrics.responseTime?.toFixed(0)}ms
              </span>
            </div>
          </div>
        </div>

        {/* Right Section - User Actions */}
        <div className="header-right">
          {/* Notifications */}
          <button className="header-button" title="Notificaciones">
            <Bell size={18} />
            <span className="notification-badge">3</span>
          </button>

          {/* Settings */}
          <button className="header-button" title="Configuración">
            <Settings size={18} />
          </button>

          {/* User Menu */}
          <div className="user-menu">
            <button className="user-button">
              <User size={18} />
              <span className="user-name">Admin</span>
            </button>
            
            <div className="user-dropdown">
              <div className="dropdown-item">
                <User size={16} />
                <span>Perfil</span>
              </div>
              <div className="dropdown-item">
                <Settings size={16} />
                <span>Configuración</span>
              </div>
              <div className="dropdown-divider" />
              <div className="dropdown-item logout">
                <LogOut size={16} />
                <span>Cerrar Sesión</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
});

Header.displayName = 'Header';

export default Header;
