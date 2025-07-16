import React, { useState, useEffect } from 'react';
import {
  Settings,
  User,
  Database,
  Shield,
  Bell,
  Palette,
  Globe,
  Download,
  Trash2,
  Save,
  RefreshCw,
  Eye,
  EyeOff,
  Check,
  X
} from 'lucide-react';
import { Card, Button, Input, Dropdown } from '../ui';

const SettingsView = () => {
  const [settings, setSettings] = useState({
    // General settings
    theme: 'light',
    language: 'es',
    autoSave: true,
    autoAnalyze: false,
    
    // Database settings
    defaultEngine: 'mysql',
    connectionTimeout: 30,
    queryTimeout: 300,
    maxConnections: 10,
    
    // Security settings
    enableEncryption: true,
    sessionTimeout: 60,
    requireAuth: false,
    
    // Notification settings
    enableNotifications: true,
    soundEnabled: true,
    emailNotifications: false,
    
    // Export settings
    defaultFormat: 'json',
    includeMetadata: true,
    compressExports: false,
    
    // Performance settings
    cacheEnabled: true,
    maxCacheSize: 100,
    enableMetrics: true
  });

  const [isDirty, setIsDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('general');

  const tabs = [
    { id: 'general', label: 'General', icon: Settings },
    { id: 'database', label: 'Base de Datos', icon: Database },
    { id: 'security', label: 'Seguridad', icon: Shield },
    { id: 'notifications', label: 'Notificaciones', icon: Bell },
    { id: 'export', label: 'Exportación', icon: Download },
    { id: 'performance', label: 'Rendimiento', icon: RefreshCw }
  ];

  const themeOptions = [
    { value: 'light', label: 'Claro' },
    { value: 'dark', label: 'Oscuro' },
    { value: 'auto', label: 'Automático' }
  ];

  const languageOptions = [
    { value: 'es', label: 'Español' },
    { value: 'en', label: 'English' },
    { value: 'fr', label: 'Français' }
  ];

  const databaseEngineOptions = [
    { value: 'mysql', label: 'MySQL' },
    { value: 'postgresql', label: 'PostgreSQL' },
    { value: 'oracle', label: 'Oracle' },
    { value: 'sqlserver', label: 'SQL Server' },
    { value: 'sqlite', label: 'SQLite' }
  ];

  const exportFormatOptions = [
    { value: 'json', label: 'JSON' },
    { value: 'csv', label: 'CSV' },
    { value: 'xml', label: 'XML' },
    { value: 'html', label: 'HTML' },
    { value: 'pdf', label: 'PDF' }
  ];

  // Load settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('sql_analyzer_settings');
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings));
      } catch (error) {
        console.error('Error loading settings:', error);
      }
    }
  }, []);

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
    setIsDirty(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      localStorage.setItem('sql_analyzer_settings', JSON.stringify(settings));
      setIsDirty(false);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (window.confirm('¿Restablecer todas las configuraciones a los valores por defecto?')) {
      const defaultSettings = {
        theme: 'light',
        language: 'es',
        autoSave: true,
        autoAnalyze: false,
        defaultEngine: 'mysql',
        connectionTimeout: 30,
        queryTimeout: 300,
        maxConnections: 10,
        enableEncryption: true,
        sessionTimeout: 60,
        requireAuth: false,
        enableNotifications: true,
        soundEnabled: true,
        emailNotifications: false,
        defaultFormat: 'json',
        includeMetadata: true,
        compressExports: false,
        cacheEnabled: true,
        maxCacheSize: 100,
        enableMetrics: true
      };
      setSettings(defaultSettings);
      setIsDirty(true);
    }
  };

  const renderGeneralSettings = () => (
    <div className="settings-section">
      <Card>
        <Card.Header>
          <Card.Title>Configuración General</Card.Title>
          <Card.Description>
            Personaliza la apariencia y comportamiento general de la aplicación
          </Card.Description>
        </Card.Header>
        <Card.Body>
          <div className="settings-grid">
            <div className="setting-item">
              <label className="setting-label">Tema</label>
              <Dropdown
                options={themeOptions}
                value={settings.theme}
                onChange={(value) => handleSettingChange('theme', value)}
              />
            </div>

            <div className="setting-item">
              <label className="setting-label">Idioma</label>
              <Dropdown
                options={languageOptions}
                value={settings.language}
                onChange={(value) => handleSettingChange('language', value)}
              />
            </div>

            <div className="setting-item">
              <label className="setting-checkbox">
                <input
                  type="checkbox"
                  checked={settings.autoSave}
                  onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
                />
                <span>Guardado automático</span>
              </label>
              <p className="setting-description">
                Guarda automáticamente los cambios en las consultas
              </p>
            </div>

            <div className="setting-item">
              <label className="setting-checkbox">
                <input
                  type="checkbox"
                  checked={settings.autoAnalyze}
                  onChange={(e) => handleSettingChange('autoAnalyze', e.target.checked)}
                />
                <span>Análisis automático</span>
              </label>
              <p className="setting-description">
                Ejecuta el análisis automáticamente al escribir
              </p>
            </div>
          </div>
        </Card.Body>
      </Card>
    </div>
  );

  const renderDatabaseSettings = () => (
    <div className="settings-section">
      <Card>
        <Card.Header>
          <Card.Title>Configuración de Base de Datos</Card.Title>
          <Card.Description>
            Configura las opciones de conexión y análisis de base de datos
          </Card.Description>
        </Card.Header>
        <Card.Body>
          <div className="settings-grid">
            <div className="setting-item">
              <label className="setting-label">Motor por defecto</label>
              <Dropdown
                options={databaseEngineOptions}
                value={settings.defaultEngine}
                onChange={(value) => handleSettingChange('defaultEngine', value)}
              />
            </div>

            <div className="setting-item">
              <Input
                label="Timeout de conexión (segundos)"
                type="number"
                value={settings.connectionTimeout}
                onChange={(e) => handleSettingChange('connectionTimeout', parseInt(e.target.value))}
                min="5"
                max="300"
              />
            </div>

            <div className="setting-item">
              <Input
                label="Timeout de consulta (segundos)"
                type="number"
                value={settings.queryTimeout}
                onChange={(e) => handleSettingChange('queryTimeout', parseInt(e.target.value))}
                min="30"
                max="3600"
              />
            </div>

            <div className="setting-item">
              <Input
                label="Máximo de conexiones"
                type="number"
                value={settings.maxConnections}
                onChange={(e) => handleSettingChange('maxConnections', parseInt(e.target.value))}
                min="1"
                max="50"
              />
            </div>
          </div>
        </Card.Body>
      </Card>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="settings-section">
      <Card>
        <Card.Header>
          <Card.Title>Configuración de Seguridad</Card.Title>
          <Card.Description>
            Configura las opciones de seguridad y autenticación
          </Card.Description>
        </Card.Header>
        <Card.Body>
          <div className="settings-grid">
            <div className="setting-item">
              <label className="setting-checkbox">
                <input
                  type="checkbox"
                  checked={settings.enableEncryption}
                  onChange={(e) => handleSettingChange('enableEncryption', e.target.checked)}
                />
                <span>Habilitar encriptación</span>
              </label>
              <p className="setting-description">
                Encripta las conexiones y datos sensibles
              </p>
            </div>

            <div className="setting-item">
              <Input
                label="Timeout de sesión (minutos)"
                type="number"
                value={settings.sessionTimeout}
                onChange={(e) => handleSettingChange('sessionTimeout', parseInt(e.target.value))}
                min="5"
                max="480"
              />
            </div>

            <div className="setting-item">
              <label className="setting-checkbox">
                <input
                  type="checkbox"
                  checked={settings.requireAuth}
                  onChange={(e) => handleSettingChange('requireAuth', e.target.checked)}
                />
                <span>Requerir autenticación</span>
              </label>
              <p className="setting-description">
                Requiere autenticación para acceder a la aplicación
              </p>
            </div>
          </div>
        </Card.Body>
      </Card>
    </div>
  );

  return (
    <div className="settings-view">
      <div className="settings-header">
        <h1 className="settings-title">
          <Settings size={24} className="title-icon" />
          Configuración
        </h1>
        <div className="settings-actions">
          <Button variant="outline" onClick={handleReset}>
            <RefreshCw size={16} />
            Restablecer
          </Button>
          <Button 
            onClick={handleSave} 
            loading={saving}
            disabled={!isDirty}
          >
            <Save size={16} />
            Guardar cambios
          </Button>
        </div>
      </div>

      <div className="settings-content">
        <div className="settings-sidebar">
          <nav className="settings-nav">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`settings-nav-item ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <tab.icon size={16} />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="settings-main">
          {activeTab === 'general' && renderGeneralSettings()}
          {activeTab === 'database' && renderDatabaseSettings()}
          {activeTab === 'security' && renderSecuritySettings()}
          {/* Add other tab content as needed */}
        </div>
      </div>
    </div>
  );
};

export default SettingsView;
