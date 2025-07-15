import React, { useState, useEffect, useRef } from 'react';
import { 
  ChevronUp, 
  ChevronDown, 
  Terminal, 
  Trash2, 
  Filter,
  Search,
  Info,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Activity
} from 'lucide-react';

const BottomPanel = ({ 
  collapsed, 
  onToggle, 
  logs, 
  onClearLogs, 
  isAnalyzing, 
  analysisProgress 
}) => {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const logsEndRef = useRef(null);

  // Auto-scroll to bottom when new logs are added
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const getLogIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="log-icon success" size={14} />;
      case 'warning':
        return <AlertTriangle className="log-icon warning" size={14} />;
      case 'error':
        return <XCircle className="log-icon error" size={14} />;
      default:
        return <Info className="log-icon info" size={14} />;
    }
  };

  const filteredLogs = logs.filter(log => {
    const matchesFilter = filter === 'all' || log.type === filter;
    const matchesSearch = searchTerm === '' || 
      log.message.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const logCounts = {
    all: logs.length,
    info: logs.filter(log => log.type === 'info').length,
    success: logs.filter(log => log.type === 'success').length,
    warning: logs.filter(log => log.type === 'warning').length,
    error: logs.filter(log => log.type === 'error').length
  };

  return (
    <div className={`bottom-panel ${collapsed ? 'collapsed' : ''}`}>
      {/* Panel Header */}
      <div className="panel-header">
        <div className="panel-title">
          <Terminal className="panel-icon" />
          <span>Consola</span>
          {isAnalyzing && (
            <div className="analysis-indicator">
              <Activity className="activity-icon" size={14} />
              <span>Analizando...</span>
            </div>
          )}
        </div>
        
        <div className="panel-controls">
          {!collapsed && (
            <>
              {/* Log Filters */}
              <div className="log-filters">
                <button 
                  className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                  onClick={() => setFilter('all')}
                  title="Todos los logs"
                >
                  Todos ({logCounts.all})
                </button>
                <button 
                  className={`filter-btn ${filter === 'info' ? 'active' : ''}`}
                  onClick={() => setFilter('info')}
                  title="Logs informativos"
                >
                  <Info size={12} />
                  {logCounts.info > 0 && <span>({logCounts.info})</span>}
                </button>
                <button 
                  className={`filter-btn ${filter === 'success' ? 'active' : ''}`}
                  onClick={() => setFilter('success')}
                  title="Logs de éxito"
                >
                  <CheckCircle size={12} />
                  {logCounts.success > 0 && <span>({logCounts.success})</span>}
                </button>
                <button 
                  className={`filter-btn ${filter === 'warning' ? 'active' : ''}`}
                  onClick={() => setFilter('warning')}
                  title="Logs de advertencia"
                >
                  <AlertTriangle size={12} />
                  {logCounts.warning > 0 && <span>({logCounts.warning})</span>}
                </button>
                <button 
                  className={`filter-btn ${filter === 'error' ? 'active' : ''}`}
                  onClick={() => setFilter('error')}
                  title="Logs de error"
                >
                  <XCircle size={12} />
                  {logCounts.error > 0 && <span>({logCounts.error})</span>}
                </button>
              </div>

              {/* Search */}
              <div className="search-box">
                <Search size={14} />
                <input
                  type="text"
                  placeholder="Buscar en logs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              {/* Clear Logs */}
              <button 
                className="btn-icon"
                onClick={onClearLogs}
                title="Limpiar logs"
                disabled={logs.length === 0}
              >
                <Trash2 size={14} />
              </button>
            </>
          )}

          {/* Toggle Button */}
          <button 
            className="panel-toggle"
            onClick={onToggle}
            title={collapsed ? 'Expandir consola' : 'Contraer consola'}
          >
            {collapsed ? <ChevronUp /> : <ChevronDown />}
          </button>
        </div>
      </div>

      {/* Progress Bar (when analyzing) */}
      {isAnalyzing && !collapsed && (
        <div className="analysis-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${analysisProgress}%` }}
            />
          </div>
          <span className="progress-text">
            {analysisProgress}% completado
          </span>
        </div>
      )}

      {/* Panel Content */}
      {!collapsed && (
        <div className="panel-content">
          <div className="logs-container">
            {filteredLogs.length === 0 ? (
              <div className="no-logs">
                <Terminal className="no-logs-icon" />
                <span>
                  {logs.length === 0 
                    ? 'No hay logs disponibles' 
                    : 'No se encontraron logs con los filtros aplicados'
                  }
                </span>
              </div>
            ) : (
              <div className="logs-list">
                {filteredLogs.map(log => (
                  <div key={log.id} className={`log-entry ${log.type}`}>
                    <div className="log-timestamp">
                      <Clock size={12} />
                      {log.timestamp}
                    </div>
                    <div className="log-content">
                      {getLogIcon(log.type)}
                      <span className="log-message">{log.message}</span>
                    </div>
                  </div>
                ))}
                <div ref={logsEndRef} />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Collapsed State */}
      {collapsed && (
        <div className="panel-collapsed-content">
          <div className="collapsed-stats">
            <span className="stat-item">
              <Terminal size={14} />
              {logs.length} logs
            </span>
            {logCounts.error > 0 && (
              <span className="stat-item error">
                <XCircle size={14} />
                {logCounts.error} errores
              </span>
            )}
            {logCounts.warning > 0 && (
              <span className="stat-item warning">
                <AlertTriangle size={14} />
                {logCounts.warning} advertencias
              </span>
            )}
            {isAnalyzing && (
              <span className="stat-item analyzing">
                <Activity size={14} />
                Analizando {analysisProgress}%
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default BottomPanel;
