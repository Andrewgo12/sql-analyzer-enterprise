import React, { useState, useEffect } from 'react';
import {
  Database,
  ChevronDown,
  Search,
  Check,
  Loader,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import { getSupportedDatabases } from '../utils/api';

const DatabaseEngineSelector = ({ 
  selectedEngine, 
  onEngineChange, 
  disabled = false,
  showLabel = true,
  compact = false 
}) => {
  const [engines, setEngines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    loadDatabaseEngines();
  }, []);

  const loadDatabaseEngines = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getSupportedDatabases();
      
      setEngines(response.engines || []);
      setCategories(response.categories || []);
      
      // Set default engine if none selected
      if (!selectedEngine && response.engines && response.engines.length > 0) {
        const defaultEngine = response.engines.find(e => e.engine === 'mysql') || response.engines[0];
        onEngineChange(defaultEngine.engine);
      }
    } catch (err) {
      console.error('Failed to load database engines:', err);
      setError('Error cargando motores de base de datos');
      
      // Fallback engines
      const fallbackEngines = [
        { engine: 'mysql', name: 'MySQL', category: 'relational' },
        { engine: 'postgresql', name: 'PostgreSQL', category: 'relational' },
        { engine: 'sqlite', name: 'SQLite', category: 'embedded' },
        { engine: 'mongodb', name: 'MongoDB', category: 'document' },
        { engine: 'oracle', name: 'Oracle', category: 'relational' }
      ];
      setEngines(fallbackEngines);
    } finally {
      setLoading(false);
    }
  };

  const filteredEngines = engines.filter(engine =>
    engine.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    engine.engine.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const groupedEngines = categories.reduce((acc, category) => {
    const categoryEngines = filteredEngines.filter(engine => engine.category === category);
    if (categoryEngines.length > 0) {
      acc[category] = categoryEngines;
    }
    return acc;
  }, {});

  // If no categories, group all engines under 'all'
  if (Object.keys(groupedEngines).length === 0 && filteredEngines.length > 0) {
    groupedEngines['all'] = filteredEngines;
  }

  const selectedEngineInfo = engines.find(e => e.engine === selectedEngine);

  const getCategoryIcon = (category) => {
    const icons = {
      relational: '🗄️',
      document: '📄',
      key_value: '🔑',
      wide_column: '📊',
      search: '🔍',
      graph: '🕸️',
      time_series: '⏰',
      analytical: '📈',
      cloud: '☁️',
      embedded: '💾'
    };
    return icons[category] || '🗃️';
  };

  const getCategoryName = (category) => {
    const names = {
      relational: 'Relacionales',
      document: 'Documentos',
      key_value: 'Clave-Valor',
      wide_column: 'Columna Ancha',
      search: 'Búsqueda',
      graph: 'Grafos',
      time_series: 'Series Temporales',
      analytical: 'Analíticas',
      cloud: 'Nube',
      embedded: 'Embebidas'
    };
    return names[category] || 'Otros';
  };

  if (loading) {
    return (
      <div className={`database-engine-selector ${compact ? 'compact' : ''}`}>
        {showLabel && <label className="selector-label">Motor de Base de Datos</label>}
        <div className="selector-loading">
          <Loader className="animate-spin" size={16} />
          <span>Cargando motores...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`database-engine-selector ${compact ? 'compact' : ''}`}>
      {showLabel && (
        <label className="selector-label">
          <Database size={16} />
          Motor de Base de Datos
          {error && (
            <button 
              onClick={loadDatabaseEngines}
              className="retry-button"
              title="Reintentar carga"
            >
              <RefreshCw size={14} />
            </button>
          )}
        </label>
      )}
      
      <div className="selector-container">
        <button
          className={`selector-trigger ${isOpen ? 'open' : ''} ${disabled ? 'disabled' : ''}`}
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
        >
          <div className="selected-engine">
            <span className="engine-icon">
              {selectedEngineInfo ? getCategoryIcon(selectedEngineInfo.category) : '🗃️'}
            </span>
            <span className="engine-name">
              {selectedEngineInfo ? selectedEngineInfo.name : 'Seleccionar motor'}
            </span>
          </div>
          <ChevronDown 
            size={16} 
            className={`chevron ${isOpen ? 'rotated' : ''}`}
          />
        </button>

        {isOpen && (
          <div className="selector-dropdown">
            <div className="dropdown-header">
              <div className="search-container">
                <Search size={16} />
                <input
                  type="text"
                  placeholder="Buscar motor..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
              </div>
              <div className="engines-count">
                {filteredEngines.length} de {engines.length} motores
              </div>
            </div>

            <div className="dropdown-content">
              {Object.keys(groupedEngines).length === 0 ? (
                <div className="no-results">
                  <AlertTriangle size={16} />
                  <span>No se encontraron motores</span>
                </div>
              ) : (
                Object.entries(groupedEngines).map(([category, categoryEngines]) => (
                  <div key={category} className="engine-category">
                    {categories.length > 0 && (
                      <div className="category-header">
                        <span className="category-icon">{getCategoryIcon(category)}</span>
                        <span className="category-name">{getCategoryName(category)}</span>
                        <span className="category-count">({categoryEngines.length})</span>
                      </div>
                    )}
                    <div className="category-engines">
                      {categoryEngines.map((engine) => (
                        <button
                          key={engine.engine}
                          className={`engine-option ${selectedEngine === engine.engine ? 'selected' : ''}`}
                          onClick={() => {
                            onEngineChange(engine.engine);
                            setIsOpen(false);
                            setSearchTerm('');
                          }}
                        >
                          <span className="engine-icon">
                            {getCategoryIcon(engine.category)}
                          </span>
                          <div className="engine-info">
                            <span className="engine-name">{engine.name}</span>
                            <span className="engine-id">{engine.engine}</span>
                          </div>
                          {selectedEngine === engine.engine && (
                            <Check size={16} className="check-icon" />
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>

            {error && (
              <div className="dropdown-footer error">
                <AlertTriangle size={14} />
                <span>{error}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Click outside to close */}
      {isOpen && (
        <div 
          className="selector-overlay" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default DatabaseEngineSelector;
