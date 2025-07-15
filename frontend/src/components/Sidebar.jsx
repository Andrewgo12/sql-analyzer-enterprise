import React, { useState, useRef } from 'react';
import { 
  Database, 
  FileText, 
  History, 
  Upload, 
  Plus, 
  ChevronLeft, 
  ChevronRight,
  Folder,
  File,
  Clock,
  Search,
  Filter
} from 'lucide-react';

const Sidebar = ({ 
  collapsed, 
  onToggle, 
  connections, 
  currentConnection, 
  onConnectionSelect, 
  onNewConnection,
  analysisHistory,
  onHistorySelect,
  onFileUpload 
}) => {
  const [activeSection, setActiveSection] = useState('files');
  const [searchTerm, setSearchTerm] = useState('');
  const fileInputRef = useRef(null);

  const filteredHistory = analysisHistory.filter(item =>
    item.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileUpload(files);
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      onFileUpload(files);
    }
    // Reset input
    e.target.value = '';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Sidebar Header */}
      <div className="sidebar-header">
        <div className="sidebar-title">
          {!collapsed && (
            <>
              <Database className="sidebar-icon" />
              <span>SQL Analyzer</span>
            </>
          )}
        </div>
        <button 
          className="sidebar-toggle"
          onClick={onToggle}
          title={collapsed ? 'Expandir sidebar' : 'Contraer sidebar'}
        >
          {collapsed ? <ChevronRight /> : <ChevronLeft />}
        </button>
      </div>

      {!collapsed && (
        <>
          {/* Navigation Tabs */}
          <div className="sidebar-nav">
            <button 
              className={`nav-tab ${activeSection === 'files' ? 'active' : ''}`}
              onClick={() => setActiveSection('files')}
              title="Explorador de archivos"
            >
              <Folder size={16} />
              <span>Archivos</span>
            </button>
            <button 
              className={`nav-tab ${activeSection === 'connections' ? 'active' : ''}`}
              onClick={() => setActiveSection('connections')}
              title="Conexiones de base de datos"
            >
              <Database size={16} />
              <span>Conexiones</span>
            </button>
            <button 
              className={`nav-tab ${activeSection === 'history' ? 'active' : ''}`}
              onClick={() => setActiveSection('history')}
              title="Historial de análisis"
            >
              <History size={16} />
              <span>Historial</span>
            </button>
          </div>

          {/* Files Section */}
          {activeSection === 'files' && (
            <div className="sidebar-section">
              <div className="section-header">
                <h3>Explorador de Archivos</h3>
                <button 
                  className="btn-icon"
                  onClick={() => fileInputRef.current?.click()}
                  title="Subir archivo"
                >
                  <Upload size={16} />
                </button>
              </div>

              <div 
                className="file-drop-zone"
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="drop-icon" />
                <p>Arrastra archivos SQL aquí</p>
                <p className="drop-hint">o haz clic para seleccionar</p>
                <div className="supported-formats">
                  <small>Formatos: .sql, .txt</small>
                </div>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".sql,.txt"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />

              <div className="file-list">
                <div className="file-item">
                  <File size={16} />
                  <span>sample.sql</span>
                  <small>2.3 KB</small>
                </div>
                <div className="file-item">
                  <File size={16} />
                  <span>queries.sql</span>
                  <small>15.7 KB</small>
                </div>
              </div>
            </div>
          )}

          {/* Connections Section */}
          {activeSection === 'connections' && (
            <div className="sidebar-section">
              <div className="section-header">
                <h3>Conexiones</h3>
                <button 
                  className="btn-icon"
                  onClick={onNewConnection}
                  title="Nueva conexión"
                >
                  <Plus size={16} />
                </button>
              </div>

              <div className="connections-list">
                {connections.length === 0 ? (
                  <div className="empty-state">
                    <Database className="empty-icon" />
                    <p>No hay conexiones configuradas</p>
                    <button 
                      className="btn-primary btn-sm"
                      onClick={onNewConnection}
                    >
                      <Plus size={16} />
                      Nueva Conexión
                    </button>
                  </div>
                ) : (
                  connections.map(connection => (
                    <div 
                      key={connection.id}
                      className={`connection-item ${currentConnection?.id === connection.id ? 'active' : ''}`}
                      onClick={() => onConnectionSelect(connection)}
                    >
                      <div className="connection-info">
                        <div className="connection-name">{connection.name}</div>
                        <div className="connection-details">
                          <span className="connection-type">{connection.type}</span>
                          <span className="connection-host">{connection.host}:{connection.port}</span>
                        </div>
                      </div>
                      <div className={`connection-status ${connection.status || 'disconnected'}`}>
                        <div className="status-dot"></div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* History Section */}
          {activeSection === 'history' && (
            <div className="sidebar-section">
              <div className="section-header">
                <h3>Historial</h3>
                <div className="search-box">
                  <Search size={14} />
                  <input
                    type="text"
                    placeholder="Buscar análisis..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>

              <div className="history-list">
                {filteredHistory.length === 0 ? (
                  <div className="empty-state">
                    <Clock className="empty-icon" />
                    <p>No hay análisis en el historial</p>
                  </div>
                ) : (
                  filteredHistory.map(item => (
                    <div 
                      key={item.id}
                      className="history-item"
                      onClick={() => onHistorySelect(item)}
                    >
                      <div className="history-info">
                        <div className="history-filename">
                          <FileText size={16} />
                          <span>{item.filename}</span>
                        </div>
                        <div className="history-summary">
                          <span className="error-count">
                            {item.summary?.total_errors || 0} errores
                          </span>
                          <span className="performance-score">
                            {item.summary?.performance_score || 100}% rendimiento
                          </span>
                        </div>
                        <div className="history-date">
                          {formatDate(item.timestamp)}
                        </div>
                      </div>
                      <div className="history-actions">
                        <button 
                          className="btn-icon btn-sm"
                          title="Cargar análisis"
                        >
                          <FileText size={14} />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </>
      )}

      {/* Collapsed State */}
      {collapsed && (
        <div className="sidebar-collapsed">
          <button 
            className="collapsed-btn"
            onClick={() => {
              setActiveSection('files');
              onToggle();
            }}
            title="Explorador de archivos"
          >
            <Folder size={20} />
          </button>
          <button 
            className="collapsed-btn"
            onClick={() => {
              setActiveSection('connections');
              onToggle();
            }}
            title="Conexiones"
          >
            <Database size={20} />
          </button>
          <button 
            className="collapsed-btn"
            onClick={() => {
              setActiveSection('history');
              onToggle();
            }}
            title="Historial"
          >
            <History size={20} />
          </button>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
