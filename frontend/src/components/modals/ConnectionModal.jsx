import React, { useState } from 'react';
import { 
  X, 
  Database, 
  Server, 
  Key, 
  User, 
  Globe,
  TestTube,
  Save,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

const ConnectionModal = ({ isOpen, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: '',
    type: 'mysql',
    host: 'localhost',
    port: '3306',
    database: '',
    username: '',
    password: '',
    ssl: false,
    timeout: 30
  });

  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const databaseTypes = [
    { value: 'mysql', label: 'MySQL', defaultPort: '3306' },
    { value: 'postgresql', label: 'PostgreSQL', defaultPort: '5432' },
    { value: 'sql_server', label: 'SQL Server', defaultPort: '1433' },
    { value: 'oracle', label: 'Oracle', defaultPort: '1521' },
    { value: 'sqlite', label: 'SQLite', defaultPort: '' },
    { value: 'mongodb', label: 'MongoDB', defaultPort: '27017' },
    { value: 'redis', label: 'Redis', defaultPort: '6379' },
    { value: 'bigquery', label: 'BigQuery', defaultPort: '' },
    { value: 'snowflake', label: 'Snowflake', defaultPort: '' },
    { value: 'clickhouse', label: 'ClickHouse', defaultPort: '9000' }
  ];

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleTypeChange = (e) => {
    const selectedType = e.target.value;
    const dbType = databaseTypes.find(db => db.value === selectedType);
    
    setFormData(prev => ({
      ...prev,
      type: selectedType,
      port: dbType?.defaultPort || prev.port
    }));
  };

  const testConnection = async () => {
    setIsTestingConnection(true);
    setTestResult(null);

    try {
      // Simulate connection test
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // For demo purposes, randomly succeed or fail
      const success = Math.random() > 0.3;
      
      setTestResult({
        success,
        message: success 
          ? 'Conexión exitosa' 
          : 'Error de conexión: No se pudo conectar al servidor'
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: `Error: ${error.message}`
      });
    } finally {
      setIsTestingConnection(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      alert('Por favor ingresa un nombre para la conexión');
      return;
    }

    onSave({
      ...formData,
      id: Date.now(),
      status: 'disconnected',
      createdAt: new Date().toISOString()
    });

    // Reset form
    setFormData({
      name: '',
      type: 'mysql',
      host: 'localhost',
      port: '3306',
      database: '',
      username: '',
      password: '',
      ssl: false,
      timeout: 30
    });
    setTestResult(null);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container large">
        <div className="modal-header">
          <div className="modal-title">
            <Database size={20} />
            <span>Nueva Conexión de Base de Datos</span>
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-content">
          <div className="form-grid">
            {/* Connection Name */}
            <div className="form-group full-width">
              <label htmlFor="name">
                <User size={16} />
                Nombre de la Conexión
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Mi Base de Datos"
                required
              />
            </div>

            {/* Database Type */}
            <div className="form-group">
              <label htmlFor="type">
                <Database size={16} />
                Tipo de Base de Datos
              </label>
              <select
                id="type"
                name="type"
                value={formData.type}
                onChange={handleTypeChange}
              >
                {databaseTypes.map(db => (
                  <option key={db.value} value={db.value}>
                    {db.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Host */}
            <div className="form-group">
              <label htmlFor="host">
                <Server size={16} />
                Servidor
              </label>
              <input
                type="text"
                id="host"
                name="host"
                value={formData.host}
                onChange={handleInputChange}
                placeholder="localhost"
                required
              />
            </div>

            {/* Port */}
            <div className="form-group">
              <label htmlFor="port">
                <Globe size={16} />
                Puerto
              </label>
              <input
                type="number"
                id="port"
                name="port"
                value={formData.port}
                onChange={handleInputChange}
                placeholder="3306"
              />
            </div>

            {/* Database Name */}
            <div className="form-group">
              <label htmlFor="database">
                <Database size={16} />
                Base de Datos
              </label>
              <input
                type="text"
                id="database"
                name="database"
                value={formData.database}
                onChange={handleInputChange}
                placeholder="nombre_bd"
              />
            </div>

            {/* Username */}
            <div className="form-group">
              <label htmlFor="username">
                <User size={16} />
                Usuario
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                placeholder="usuario"
              />
            </div>

            {/* Password */}
            <div className="form-group">
              <label htmlFor="password">
                <Key size={16} />
                Contraseña
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="••••••••"
              />
            </div>

            {/* Timeout */}
            <div className="form-group">
              <label htmlFor="timeout">
                Timeout (segundos)
              </label>
              <input
                type="number"
                id="timeout"
                name="timeout"
                value={formData.timeout}
                onChange={handleInputChange}
                min="5"
                max="300"
              />
            </div>

            {/* SSL */}
            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="ssl"
                  checked={formData.ssl}
                  onChange={handleInputChange}
                />
                <span className="checkbox-custom"></span>
                Usar SSL/TLS
              </label>
            </div>
          </div>

          {/* Connection Test */}
          <div className="connection-test">
            <button
              type="button"
              className="btn-secondary"
              onClick={testConnection}
              disabled={isTestingConnection}
            >
              <TestTube size={16} />
              {isTestingConnection ? 'Probando...' : 'Probar Conexión'}
            </button>

            {testResult && (
              <div className={`test-result ${testResult.success ? 'success' : 'error'}`}>
                {testResult.success ? (
                  <CheckCircle size={16} />
                ) : (
                  <AlertCircle size={16} />
                )}
                <span>{testResult.message}</span>
              </div>
            )}
          </div>

          {/* Connection String Preview */}
          <div className="connection-preview">
            <h4>Cadena de Conexión:</h4>
            <code>
              {formData.type}://{formData.username && `${formData.username}:***@`}
              {formData.host}:{formData.port}/{formData.database}
              {formData.ssl ? '?ssl=true' : ''}
            </code>
          </div>
        </form>

        <div className="modal-footer">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Cancelar
          </button>
          <button 
            type="submit" 
            className="btn-primary"
            onClick={handleSubmit}
            disabled={!formData.name.trim()}
          >
            <Save size={16} />
            Guardar Conexión
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConnectionModal;
