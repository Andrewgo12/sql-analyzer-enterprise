import React, { memo } from 'react';
import {
  Home,
  Code,
  Database,
  History,
  Terminal,
  Download,
  Activity,
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useSidebar } from '../../contexts/UIContext';

const Sidebar = memo(() => {
  const { isCollapsed, toggleSidebar, activePanel, setActivePanel } = useSidebar();

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: Home,
      description: 'Vista general del sistema'
    },
    {
      id: 'sql-analysis',
      label: 'Análisis SQL',
      icon: Code,
      description: 'Analizar consultas SQL'
    },
    {
      id: 'connections',
      label: 'Conexiones',
      icon: Database,
      description: 'Gestionar conexiones de BD'
    },
    {
      id: 'history',
      label: 'Historial',
      icon: History,
      description: 'Análisis anteriores'
    },
    {
      id: 'terminal',
      label: 'Terminal',
      icon: Terminal,
      description: 'Terminal integrado'
    },
    {
      id: 'downloads',
      label: 'Descargas',
      icon: Download,
      description: 'Gestionar descargas'
    },
    {
      id: 'metrics',
      label: 'Métricas',
      icon: Activity,
      description: 'Monitoreo del sistema'
    },
    {
      id: 'settings',
      label: 'Configuración',
      icon: Settings,
      description: 'Configuración general'
    }
  ];

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : 'expanded'}`}>
      {/* Header */}
      <div className="sidebar-header">
        <div className="logo">
          {!isCollapsed && (
            <span className="logo-text">SQL Analyzer</span>
          )}
        </div>
        <button
          onClick={toggleSidebar}
          className="collapse-button"
          aria-label={isCollapsed ? 'Expandir sidebar' : 'Colapsar sidebar'}
        >
          {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <ul className="nav-list">
          {menuItems.map((item) => {
            const IconComponent = item.icon;
            const isActive = activePanel === item.id;

            return (
              <li key={item.id} className="nav-item">
                <button
                  onClick={() => setActivePanel(item.id)}
                  className={`nav-button ${isActive ? 'active' : ''}`}
                  title={isCollapsed ? item.label : item.description}
                  aria-label={item.label}
                >
                  <IconComponent size={20} className="nav-icon" />
                  {!isCollapsed && (
                    <span className="nav-label">{item.label}</span>
                  )}
                  {isActive && <div className="active-indicator" />}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      {!isCollapsed && (
        <div className="sidebar-footer">
          <div className="version-info">
            <span className="version">v2.0.0</span>
            <span className="status">Enterprise</span>
          </div>
        </div>
      )}
    </div>
  );
});

Sidebar.displayName = 'Sidebar';

export default Sidebar;
