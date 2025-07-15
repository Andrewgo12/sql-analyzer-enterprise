import React, { useState } from 'react';
import { 
  X, 
  Keyboard, 
  Book, 
  Zap, 
  Database, 
  FileText,
  Settings,
  Info,
  ExternalLink
} from 'lucide-react';
import { getAllShortcuts, getShortcutText } from '../../hooks/useKeyboardShortcuts';

const HelpModal = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('shortcuts');

  if (!isOpen) return null;

  const shortcuts = getAllShortcuts();

  const helpSections = {
    shortcuts: {
      title: 'Atajos de Teclado',
      icon: <Keyboard size={20} />,
      content: (
        <div className="shortcuts-content">
          <p className="help-description">
            Utiliza estos atajos de teclado para trabajar más eficientemente con SQL Analyzer Enterprise.
          </p>
          
          {shortcuts.map((category, index) => (
            <div key={index} className="shortcut-category">
              <h4 className="category-title">{category.category}</h4>
              <div className="shortcuts-list">
                {category.shortcuts.map((shortcut, shortcutIndex) => (
                  <div key={shortcutIndex} className="shortcut-item">
                    <div className="shortcut-keys">
                      <kbd className="shortcut-key">{getShortcutText(shortcut.key)}</kbd>
                    </div>
                    <div className="shortcut-description">
                      {shortcut.description}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )
    },
    
    features: {
      title: 'Características',
      icon: <Zap size={20} />,
      content: (
        <div className="features-content">
          <h4>Análisis SQL Enterprise</h4>
          <ul className="feature-list">
            <li>Soporte para 22+ motores de base de datos</li>
            <li>Análisis sintáctico, semántico y de rendimiento</li>
            <li>Detección de vulnerabilidades de seguridad</li>
            <li>Corrección automática de errores</li>
            <li>Puntuación de confianza con ML</li>
          </ul>

          <h4>Sistema de Exportación</h4>
          <ul className="feature-list">
            <li>38+ formatos de exportación disponibles</li>
            <li>Documentos: PDF, HTML, Word, RTF, LaTeX</li>
            <li>Datos: JSON, XML, CSV, Excel, Parquet</li>
            <li>Especializados: OpenAPI, GraphQL, Swagger</li>
            <li>Componentes web: React, Vue, Angular</li>
          </ul>

          <h4>Interfaz Enterprise</h4>
          <ul className="feature-list">
            <li>Diseño full-screen profesional</li>
            <li>Editor de código avanzado</li>
            <li>Dashboard de métricas en tiempo real</li>
            <li>Sistema de notificaciones</li>
            <li>Gestión de pestañas múltiples</li>
          </ul>
        </div>
      )
    },

    databases: {
      title: 'Bases de Datos',
      icon: <Database size={20} />,
      content: (
        <div className="databases-content">
          <h4>Motores Soportados</h4>
          
          <div className="db-category">
            <h5>SQL Relacionales</h5>
            <div className="db-list">
              <span className="db-item">MySQL</span>
              <span className="db-item">PostgreSQL</span>
              <span className="db-item">SQL Server</span>
              <span className="db-item">Oracle</span>
              <span className="db-item">MariaDB</span>
              <span className="db-item">SQLite</span>
            </div>
          </div>

          <div className="db-category">
            <h5>NoSQL</h5>
            <div className="db-list">
              <span className="db-item">MongoDB</span>
              <span className="db-item">Redis</span>
              <span className="db-item">Neo4j</span>
              <span className="db-item">ArangoDB</span>
            </div>
          </div>

          <div className="db-category">
            <h5>Especializadas</h5>
            <div className="db-list">
              <span className="db-item">InfluxDB</span>
              <span className="db-item">TimescaleDB</span>
              <span className="db-item">Elasticsearch</span>
              <span className="db-item">ClickHouse</span>
              <span className="db-item">BigQuery</span>
            </div>
          </div>

          <div className="db-category">
            <h5>Embebidas</h5>
            <div className="db-list">
              <span className="db-item">H2</span>
              <span className="db-item">DuckDB</span>
              <span className="db-item">SQLite</span>
            </div>
          </div>
        </div>
      )
    },

    about: {
      title: 'Acerca de',
      icon: <Info size={20} />,
      content: (
        <div className="about-content">
          <div className="app-info">
            <h4>SQL Analyzer Enterprise</h4>
            <p className="version">Versión 2.0.0</p>
            <p className="description">
              Plataforma enterprise de análisis SQL con soporte para múltiples motores de base de datos,
              análisis avanzado y sistema de exportación completo.
            </p>
          </div>

          <div className="tech-stack">
            <h4>Tecnologías</h4>
            <ul className="tech-list">
              <li><strong>Frontend:</strong> React 18, Vite, Lucide Icons</li>
              <li><strong>Backend:</strong> Python 3.11, Flask, SQLAlchemy</li>
              <li><strong>Análisis:</strong> Motor SQL personalizado, ML</li>
              <li><strong>Exportación:</strong> 38+ formatos soportados</li>
            </ul>
          </div>

          <div className="capabilities">
            <h4>Capacidades Enterprise</h4>
            <ul className="capability-list">
              <li>✅ 22+ motores de base de datos</li>
              <li>✅ 38+ formatos de exportación</li>
              <li>✅ Análisis en tiempo real</li>
              <li>✅ Dashboard de métricas</li>
              <li>✅ Sistema de notificaciones</li>
              <li>✅ Atajos de teclado</li>
              <li>✅ Interfaz responsive</li>
              <li>✅ Arquitectura escalable</li>
            </ul>
          </div>

          <div className="links">
            <h4>Enlaces</h4>
            <div className="link-list">
              <a href="#" className="help-link">
                <FileText size={16} />
                Documentación
                <ExternalLink size={14} />
              </a>
              <a href="#" className="help-link">
                <Settings size={16} />
                Configuración
                <ExternalLink size={14} />
              </a>
            </div>
          </div>
        </div>
      )
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-container large">
        <div className="modal-header">
          <div className="modal-title">
            <Book size={20} />
            <span>Ayuda y Documentación</span>
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="help-modal-content">
          <div className="help-tabs">
            {Object.entries(helpSections).map(([key, section]) => (
              <button
                key={key}
                className={`help-tab ${activeTab === key ? 'active' : ''}`}
                onClick={() => setActiveTab(key)}
              >
                {section.icon}
                <span>{section.title}</span>
              </button>
            ))}
          </div>

          <div className="help-content">
            {helpSections[activeTab]?.content}
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default HelpModal;
