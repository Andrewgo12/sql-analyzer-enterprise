import React, { useState, useEffect } from 'react';
import {
  Database,
  TestTube,
  Save,
  X,
  CheckCircle,
  AlertCircle,
  Loader2,
  Eye,
  EyeOff,
  Info
} from 'lucide-react';
import { Modal, Button, Input, Dropdown, Card } from '../ui';

const ConnectionModal = ({ isOpen, onClose, onSave, connection = null }) => {
  const [formData, setFormData] = useState({
    name: '',
    type: 'mysql',
    host: 'localhost',
    port: '3306',
    database: '',
    username: '',
    password: '',
    ssl: false,
    timeout: 30,
    description: ''
  });

  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});

  const databaseTypes = [
    { value: 'mysql', label: 'MySQL' },
    { value: 'postgresql', label: 'PostgreSQL' },
    { value: 'oracle', label: 'Oracle Database' },
    { value: 'sqlserver', label: 'Microsoft SQL Server' },
    { value: 'sqlite', label: 'SQLite' },
    { value: 'mongodb', label: 'MongoDB' },
    { value: 'redis', label: 'Redis' },
    { value: 'cassandra', label: 'Apache Cassandra' },
    { value: 'mariadb', label: 'MariaDB' }
  ];

  const defaultPorts = {
    mysql: '3306',
    postgresql: '5432',
    oracle: '1521',
    sqlserver: '1433',
    sqlite: '',
    mongodb: '27017',
    redis: '6379',
    cassandra: '9042',
    mariadb: '3306'
  };

  // Initialize form data when connection prop changes
  useEffect(() => {
    if (connection) {
      setFormData({
        name: connection.name || '',
        type: connection.type || 'mysql',
        host: connection.host || 'localhost',
        port: connection.port || defaultPorts[connection.type] || '3306',
        database: connection.database || '',
        username: connection.username || '',
        password: connection.password || '',
        ssl: connection.ssl || false,
        timeout: connection.timeout || 30,
        description: connection.description || ''
      });
    } else {
      setFormData({
        name: '',
        type: 'mysql',
        host: 'localhost',
        port: '3306',
        database: '',
        username: '',
        password: '',
        ssl: false,
        timeout: 30,
        description: ''
      });
    }
    setTestResult(null);
    setErrors({});
  }, [connection, isOpen]);

  // Update port when database type changes
  useEffect(() => {
    if (formData.type && defaultPorts[formData.type]) {
      setFormData(prev => ({
        ...prev,
        port: defaultPorts[prev.type] || '3306'
      }));
    }
  }, [formData.type]);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'El nombre de la conexión es requerido';
    }

    if (!formData.host.trim()) {
      newErrors.host = 'El host es requerido';
    }

    if (formData.type !== 'sqlite' && !formData.database.trim()) {
      newErrors.database = 'El nombre de la base de datos es requerido';
    }

    if (!formData.username.trim()) {
      newErrors.username = 'El usuario es requerido';
    }

    if (formData.port && isNaN(parseInt(formData.port))) {
      newErrors.port = 'El puerto debe ser un número válido';
    }

    if (formData.timeout && (isNaN(parseInt(formData.timeout)) || parseInt(formData.timeout) < 1)) {
      newErrors.timeout = 'El timeout debe ser un número mayor a 0';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear specific error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }

    // Clear test result when form changes
    setTestResult(null);
  };

  const handleTest = async () => {
    if (!validateForm()) {
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      // If we have a connection ID, test existing connection
      const endpoint = connection?.id
        ? `/api/connections/${connection.id}/test`
        : '/api/connections/test';

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();

      if (response.ok && result.test_result) {
        setTestResult({
          success: result.test_result.success,
          message: result.test_result.message,
          details: result.test_result.success ? {
            server_version: result.test_result.server_version,
            connection_time: `${result.test_result.connection_time}s`,
            database_size: result.test_result.database_size,
            tables_count: result.test_result.tables_count
          } : null,
          error: result.test_result.success ? null : result.test_result.message
        });
      } else {
        throw new Error(result.message || 'Test de conexión falló');
      }
    } catch (error) {
      console.error('Connection test failed:', error);
      setTestResult({
        success: false,
        message: 'Error al probar la conexión',
        error: error.message || 'Error desconocido'
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    setSaving(true);

    try {
      const connectionData = {
        ...formData,
        port: formData.port ? parseInt(formData.port) : null,
        timeout: parseInt(formData.timeout)
      };

      await onSave?.(connectionData);
      onClose?.();
    } catch (error) {
      console.error('Save connection failed:', error);
      setErrors({ general: 'Error al guardar la conexión' });
    } finally {
      setSaving(false);
    }
  };

  const getConnectionInfo = () => {
    const dbType = databaseTypes.find(type => type.value === formData.type);
    return {
      name: dbType?.label || formData.type,
      requiresDatabase: formData.type !== 'sqlite',
      supportsSSL: ['mysql', 'postgresql', 'oracle', 'sqlserver', 'mongodb'].includes(formData.type)
    };
  };

  const connectionInfo = getConnectionInfo();

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
