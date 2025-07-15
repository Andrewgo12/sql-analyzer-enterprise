import React, { useState, useEffect } from 'react';
import {
  Database,
  Plus,
  Edit,
  Trash2,
  TestTube,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Eye,
  EyeOff,
  Copy,
  Settings,
  Wifi,
  WifiOff,
  Server,
  Key,
  Globe,
  Lock,
  Unlock,
  RefreshCw,
  Save,
  X,
  Clock,
  Zap,
  Shield,
  Activity
} from 'lucide-react';
import DatabaseEngineSelector from '../DatabaseEngineSelector';
import { getSupportedDatabases } from '../utils/api';

const ConnectionsView = ({
  connections,
  setConnections,
  currentConnection,
  setCurrentConnection,
  onTestConnection,
  onSaveConnection,
  onDeleteConnection
}) => {
  const [showForm, setShowForm] = useState(false);
  const [editingConnection, setEditingConnection] = useState(null);
  const [showPassword, setShowPassword] = useState({});
  const [testingConnection, setTestingConnection] = useState(null);
  const [connectionResults, setConnectionResults] = useState({});
  const [availableEngines, setAvailableEngines] = useState([]);
  const [loadingEngines, setLoadingEngines] = useState(true);
  const [filterEngine, setFilterEngine] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    engine: 'mysql',
    host: 'localhost',
    port: '3306',
    database: '',
    username: '',
    password: '',
    ssl: false,
    timeout: 30,
    description: '',
    tags: []
  });

  useEffect(() => {
    loadDatabaseEngines();
  }, []);

  const loadDatabaseEngines = async () => {
    try {
      setLoadingEngines(true);
      const response = await getSupportedDatabases();
      setAvailableEngines(response.engines || []);
    } catch (error) {
      console.error('Failed to load database engines:', error);
      // Fallback engines
      setAvailableEngines([
        { engine: 'mysql', name: 'MySQL', category: 'relational' },
        { engine: 'postgresql', name: 'PostgreSQL', category: 'relational' },
        { engine: 'sqlite', name: 'SQLite', category: 'embedded' },
        { engine: 'mongodb', name: 'MongoDB', category: 'document' },
        { engine: 'oracle', name: 'Oracle', category: 'relational' }
      ]);
    } finally {
      setLoadingEngines(false);
    }
  };

  const testConnection = async (connection) => {
    setTestingConnection(connection.id);
    try {
      // Simulate connection test - in real app, this would call backend
      await new Promise(resolve => setTimeout(resolve, 2000));

      const testResult = {
        success: Math.random() > 0.3, // 70% success rate for demo
        responseTime: Math.floor(Math.random() * 500) + 50,
        timestamp: new Date(),
        message: Math.random() > 0.3 ? 'Conexión exitosa' : 'Error de conexión: Timeout'
      };

      setConnectionResults(prev => ({
        ...prev,
        [connection.id]: testResult
      }));

      if (onTestConnection) {
        onTestConnection(connection, testResult);
      }
    } catch (error) {
      setConnectionResults(prev => ({
        ...prev,
        [connection.id]: {
          success: false,
          responseTime: 0,
          timestamp: new Date(),
          message: 'Error de prueba de conexión'
        }
      }));
    } finally {
      setTestingConnection(null);
    }
  };

  const databaseEngines = [
    { value: 'mysql', label: 'MySQL', icon: '🐬', defaultPort: 3306 },
    { value: 'postgresql', label: 'PostgreSQL', icon: '🐘', defaultPort: 5432 },
    { value: 'sqlite', label: 'SQLite', icon: '📁', defaultPort: null },
    { value: 'mssql', label: 'SQL Server', icon: '🏢', defaultPort: 1433 },
    { value: 'oracle', label: 'Oracle', icon: '🔴', defaultPort: 1521 },
    { value: 'mongodb', label: 'MongoDB', icon: '🍃', defaultPort: 27017 },
    { value: 'redis', label: 'Redis', icon: '🔴', defaultPort: 6379 },
    { value: 'cassandra', label: 'Cassandra', icon: '💎', defaultPort: 9042 }
  ];

  const handleEngineChange = (engine) => {
    const engineInfo = databaseEngines.find(e => e.value === engine);
    setFormData(prev => ({
      ...prev,
      engine,
      port: engineInfo?.defaultPort?.toString() || ''
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const connectionData = {
        ...formData,
        id: editingConnection?.id || Date.now(),
        createdAt: editingConnection?.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        status: 'inactive'
      };

      if (editingConnection) {
        setConnections(prev => prev.map(conn =>
          conn.id === editingConnection.id ? connectionData : conn
        ));
      } else {
        setConnections(prev => [...prev, connectionData]);
      }

      onSaveConnection(connectionData);
      resetForm();
    } catch (error) {
      console.error('Error saving connection:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      engine: 'mysql',
      host: 'localhost',
      port: '3306',
      database: '',
      username: '',
      password: '',
      ssl: false,
      timeout: 30
    });
    setEditingConnection(null);
    setShowForm(false);
  };

  const handleEdit = (connection) => {
    setFormData(connection);
    setEditingConnection(connection);
    setShowForm(true);
  };

  const handleDelete = (connectionId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta conexión?')) {
      setConnections(prev => prev.filter(conn => conn.id !== connectionId));
      if (currentConnection?.id === connectionId) {
        setCurrentConnection(null);
      }
      onDeleteConnection(connectionId);
    }
  };

  const handleTest = async (connection) => {
    setTestingConnection(connection.id);
    try {
      const result = await onTestConnection(connection);
      setConnections(prev => prev.map(conn =>
        conn.id === connection.id
          ? { ...conn, status: result.success ? 'active' : 'error', lastTested: new Date().toISOString() }
          : conn
      ));
    } catch (error) {
      setConnections(prev => prev.map(conn =>
        conn.id === connection.id
          ? { ...conn, status: 'error', lastTested: new Date().toISOString() }
          : conn
      ));
    } finally {
      setTestingConnection(null);
    }
  };

  const togglePasswordVisibility = (connectionId) => {
    setShowPassword(prev => ({
      ...prev,
      [connectionId]: !prev[connectionId]
    }));
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="status-icon success" size={16} />;
      case 'error':
        return <XCircle className="status-icon error" size={16} />;
      default:
        return <AlertTriangle className="status-icon warning" size={16} />;
    }
  };

  const getFilteredConnections = () => {
    return connections.filter(connection => {
      const matchesSearch = connection.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        connection.host.toLowerCase().includes(searchTerm.toLowerCase()) ||
        connection.database.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesEngine = filterEngine === 'all' || connection.engine === filterEngine;

      return matchesSearch && matchesEngine;
    });
  };

  const getActiveConnections = () => {
    return connections.filter(connection => {
      const result = connectionResults[connection.id];
      return result && result.success;
    });
  };

  const getEngineInfo = (engine) => {
    return databaseEngines.find(e => e.value === engine) || databaseEngines[0];
  };

  const renderConnectionForm = () => (
    <div className="connection-form-modal">
      <div className="modal-backdrop" onClick={resetForm}></div>
      <div className="modal-content">
        <div className="modal-header">
          <h3>
            {editingConnection ? 'Editar Conexión' : 'Nueva Conexión'}
          </h3>
          <button className="modal-close" onClick={resetForm}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="connection-form">
          <div className="form-row">
            <div className="form-group">
              <label>Nombre de la Conexión</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Mi Base de Datos"
                required
              />
            </div>
            <div className="form-group">
              <DatabaseEngineSelector
                selectedEngine={formData.engine}
                onEngineChange={(engine) => handleEngineChange(engine)}
                disabled={false}
                showLabel={true}
                compact={false}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Host</label>
              <input
                type="text"
                value={formData.host}
                onChange={(e) => setFormData(prev => ({ ...prev, host: e.target.value }))}
                placeholder="localhost"
                required
              />
            </div>
            <div className="form-group">
              <label>Puerto</label>
              <input
                type="number"
                value={formData.port}
                onChange={(e) => setFormData(prev => ({ ...prev, port: e.target.value }))}
                placeholder="3306"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Base de Datos</label>
            <input
              type="text"
              value={formData.database}
              onChange={(e) => setFormData(prev => ({ ...prev, database: e.target.value }))}
              placeholder="nombre_base_datos"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Usuario</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                placeholder="usuario"
                required
              />
            </div>
            <div className="form-group">
              <label>Contraseña</label>
              <div className="password-input">
                <input
                  type={showPassword.form ? "text" : "password"}
                  value={formData.password}
                  onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                  placeholder="contraseña"
                  required
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => togglePasswordVisibility('form')}
                >
                  {showPassword.form ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.ssl}
                  onChange={(e) => setFormData(prev => ({ ...prev, ssl: e.target.checked }))}
                />
                Usar SSL
              </label>
            </div>
            <div className="form-group">
              <label>Timeout (segundos)</label>
              <input
                type="number"
                value={formData.timeout}
                onChange={(e) => setFormData(prev => ({ ...prev, timeout: parseInt(e.target.value) }))}
                min="5"
                max="300"
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={resetForm}>
              Cancelar
            </button>
            <button type="submit" className="btn-primary">
              <Save size={16} />
              {editingConnection ? 'Actualizar' : 'Crear'} Conexión
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  const renderConnectionCard = (connection) => {
    const engineInfo = getEngineInfo(connection.engine);

    return (
      <div
        key={connection.id}
        className={`connection-card ${currentConnection?.id === connection.id ? 'active' : ''}`}
      >
        <div className="connection-header">
          <div className="connection-info">
            <div className="connection-icon">
              <span className="engine-icon">{engineInfo.icon}</span>
              {getStatusIcon(connection.status)}
            </div>
            <div className="connection-details">
              <h3 className="connection-name">{connection.name}</h3>
              <p className="connection-engine">{engineInfo.label}</p>
            </div>
          </div>
          <div className="connection-actions">
            <button
              className="action-btn"
              onClick={() => handleTest(connection)}
              disabled={testingConnection === connection.id}
              title="Probar conexión"
            >
              {testingConnection === connection.id ? (
                <RefreshCw size={16} className="spinning" />
              ) : (
                <TestTube size={16} />
              )}
            </button>
            <button
              className="action-btn"
              onClick={() => handleEdit(connection)}
              title="Editar conexión"
            >
              <Edit size={16} />
            </button>
            <button
              className="action-btn danger"
              onClick={() => handleDelete(connection.id)}
              title="Eliminar conexión"
            >
              <Trash2 size={16} />
            </button>
          </div>
        </div>

        <div className="connection-body">
          <div className="connection-meta">
            <div className="meta-item">
              <Server size={14} />
              <span>{connection.host}:{connection.port}</span>
            </div>
            <div className="meta-item">
              <Database size={14} />
              <span>{connection.database}</span>
            </div>
            <div className="meta-item">
              <Key size={14} />
              <span>{connection.username}</span>
            </div>
            {connection.ssl && (
              <div className="meta-item">
                <Lock size={14} />
                <span>SSL</span>
              </div>
            )}
          </div>

          {connection.lastTested && (
            <div className="connection-status">
              <span className="status-text">
                Última prueba: {new Date(connection.lastTested).toLocaleString()}
              </span>
            </div>
          )}
        </div>

        <div className="connection-footer">
          <button
            className={`use-connection-btn ${currentConnection?.id === connection.id ? 'active' : ''}`}
            onClick={() => setCurrentConnection(connection)}
          >
            {currentConnection?.id === connection.id ? (
              <>
                <CheckCircle size={16} />
                Conexión Activa
              </>
            ) : (
              <>
                <Wifi size={16} />
                Usar Conexión
              </>
            )}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="connections-view">
      <div className="view-header">
        <div className="header-title">
          <Database size={24} />
          <div>
            <h1>Conexiones de Base de Datos</h1>
            <p>{connections.length} conexiones configuradas</p>
          </div>
        </div>
        <div className="header-actions">
          <button
            className="btn-primary"
            onClick={() => setShowForm(true)}
          >
            <Plus size={16} />
            Nueva Conexión
          </button>
        </div>
      </div>

      {currentConnection && (
        <div className="current-connection-banner">
          <div className="banner-content">
            <div className="banner-icon">
              <Wifi size={20} />
            </div>
            <div className="banner-text">
              <strong>Conexión Activa:</strong> {currentConnection.name}
              ({getEngineInfo(currentConnection.engine).label})
            </div>
            <button
              className="banner-action"
              onClick={() => setCurrentConnection(null)}
            >
              <WifiOff size={16} />
              Desconectar
            </button>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="connections-filters">
        <div className="filter-group">
          <div className="search-box">
            <input
              type="text"
              placeholder="Buscar conexiones..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="filter-select">
            <select
              value={filterEngine}
              onChange={(e) => setFilterEngine(e.target.value)}
              className="engine-filter"
            >
              <option value="all">Todos los motores</option>
              {availableEngines.map(engine => (
                <option key={engine.engine} value={engine.engine}>
                  {engine.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="connections-stats">
          <span className="stat-item">
            <Activity size={14} />
            Total: {getFilteredConnections().length}
          </span>
          <span className="stat-item">
            <CheckCircle size={14} />
            Activas: {getActiveConnections().length}
          </span>
        </div>
      </div>

      <div className="connections-content">
        {connections.length === 0 ? (
          <div className="empty-state">
            <Database size={64} className="empty-icon" />
            <h3>No hay conexiones configuradas</h3>
            <p>Crea tu primera conexión de base de datos para comenzar</p>
            <button
              className="btn-primary"
              onClick={() => setShowForm(true)}
            >
              <Plus size={16} />
              Crear Primera Conexión
            </button>
          </div>
        ) : (
          <div className="connections-grid">
            {getFilteredConnections().map(renderConnectionCard)}
          </div>
        )}
      </div>

      {showForm && renderConnectionForm()}
    </div>
  );
};

export default ConnectionsView;
