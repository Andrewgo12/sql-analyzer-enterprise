import React, { useState, useEffect } from 'react';
import {
  History,
  Search,
  Filter,
  Calendar,
  Clock,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Eye,
  Download,
  Trash2,
  Star,
  StarOff,
  Code,
  Database,
  FileText,
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  SortAsc,
  SortDesc,
  Share,
  Archive,
  Tag,
  Zap
} from 'lucide-react';
import ExportSystem from '../ExportSystem';

const HistoryView = ({
  analysisHistory,
  setAnalysisHistory,
  onViewAnalysis,
  onDeleteAnalysis,
  onExportAnalysis,
  onRerunAnalysis
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all'); // 'all', 'success', 'errors', 'warnings'
  const [filterDate, setFilterDate] = useState('all'); // 'all', 'today', 'week', 'month'
  const [sortBy, setSortBy] = useState('date'); // 'date', 'name', 'errors', 'score'
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc', 'desc'
  const [selectedItems, setSelectedItems] = useState([]);
  const [showDetails, setShowDetails] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportData, setExportData] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid', 'list', 'timeline'
  const [groupBy, setGroupBy] = useState('none'); // 'none', 'date', 'status', 'engine'

  const getDateFilter = (date) => {
    const now = new Date();
    const itemDate = new Date(date);

    switch (filterDate) {
      case 'today':
        return itemDate.toDateString() === now.toDateString();
      case 'week':
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        return itemDate >= weekAgo;
      case 'month':
        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        return itemDate >= monthAgo;
      default:
        return true;
    }
  };

  const getStatusFilter = (item) => {
    const errors = item.summary?.total_errors || 0;
    const warnings = item.summary?.total_warnings || 0;

    switch (filterStatus) {
      case 'success':
        return errors === 0 && warnings === 0;
      case 'errors':
        return errors > 0;
      case 'warnings':
        return warnings > 0 && errors === 0;
      default:
        return true;
    }
  };

  const filteredHistory = analysisHistory
    .filter(item => {
      const matchesSearch = item.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.content?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.connection?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesStatus = getStatusFilter(item);
      const matchesDate = getDateFilter(item.timestamp);

      return matchesSearch && matchesStatus && matchesDate;
    })
    .sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case 'date':
          comparison = new Date(a.timestamp) - new Date(b.timestamp);
          break;
        case 'name':
          comparison = (a.title || '').localeCompare(b.title || '');
          break;
        case 'errors':
          comparison = (a.summary?.total_errors || 0) - (b.summary?.total_errors || 0);
          break;
        case 'score':
          comparison = (a.summary?.performance_score || 0) - (b.summary?.performance_score || 0);
          break;
        default:
          comparison = 0;
      }

      return sortOrder === 'asc' ? comparison : -comparison;
    });

  const handleSelectAll = () => {
    if (selectedItems.length === filteredHistory.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(filteredHistory.map(item => item.id));
    }
  };

  const handleSelectItem = (itemId) => {
    if (selectedItems.includes(itemId)) {
      setSelectedItems(selectedItems.filter(id => id !== itemId));
    } else {
      setSelectedItems([...selectedItems, itemId]);
    }
  };

  const handleBulkDelete = () => {
    if (window.confirm(`¿Eliminar ${selectedItems.length} análisis seleccionados?`)) {
      setAnalysisHistory(prev => prev.filter(item => !selectedItems.includes(item.id)));
      setSelectedItems([]);
    }
  };

  const toggleFavorite = (itemId) => {
    if (favorites.includes(itemId)) {
      setFavorites(favorites.filter(id => id !== itemId));
    } else {
      setFavorites([...favorites, itemId]);
    }
  };

  const handleExportSelected = () => {
    if (selectedItems.length === 0) {
      alert('Selecciona al menos un análisis para exportar');
      return;
    }

    const selectedAnalyses = analysisHistory.filter(item => selectedItems.includes(item.id));
    const exportPayload = {
      export_type: 'history_batch',
      analyses: selectedAnalyses,
      metadata: {
        exported_at: new Date().toISOString(),
        total_analyses: selectedAnalyses.length,
        date_range: {
          from: Math.min(...selectedAnalyses.map(a => new Date(a.timestamp))),
          to: Math.max(...selectedAnalyses.map(a => new Date(a.timestamp)))
        }
      }
    };

    setExportData(exportPayload);
    setShowExportModal(true);
  };

  const handleExportSingle = (analysis) => {
    const exportPayload = {
      export_type: 'single_analysis',
      analysis: analysis,
      metadata: {
        exported_at: new Date().toISOString(),
        analysis_id: analysis.id,
        analysis_date: analysis.timestamp
      }
    };

    setExportData(exportPayload);
    setShowExportModal(true);
  };

  const handleExportComplete = (exportRecord) => {
    console.log('Export completed:', exportRecord);
    setShowExportModal(false);
    setExportData(null);
  };

  const getAnalysisStats = () => {
    const total = filteredHistory.length;
    const withErrors = filteredHistory.filter(item => (item.summary?.total_errors || 0) > 0).length;
    const withWarnings = filteredHistory.filter(item => (item.summary?.total_warnings || 0) > 0).length;
    const avgScore = total > 0 ?
      filteredHistory.reduce((sum, item) => sum + (item.summary?.performance_score || 0), 0) / total : 0;

    return { total, withErrors, withWarnings, avgScore };
  };

  const groupAnalyses = (analyses) => {
    if (groupBy === 'none') return { 'Todos los análisis': analyses };

    const groups = {};

    analyses.forEach(analysis => {
      let groupKey;

      switch (groupBy) {
        case 'date':
          groupKey = new Date(analysis.timestamp).toLocaleDateString();
          break;
        case 'status':
          if ((analysis.summary?.total_errors || 0) > 0) {
            groupKey = 'Con errores';
          } else if ((analysis.summary?.total_warnings || 0) > 0) {
            groupKey = 'Con advertencias';
          } else {
            groupKey = 'Sin problemas';
          }
          break;
        case 'engine':
          groupKey = analysis.database_engine || 'Sin especificar';
          break;
        default:
          groupKey = 'Otros';
      }

      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(analysis);
    });

    return groups;
  };

  const getStatusBadge = (item) => {
    const errors = item.summary?.total_errors || 0;
    const warnings = item.summary?.total_warnings || 0;

    if (errors > 0) {
      return <span className="status-badge error">Errores: {errors}</span>;
    } else if (warnings > 0) {
      return <span className="status-badge warning">Advertencias: {warnings}</span>;
    } else {
      return <span className="status-badge success">Sin errores</span>;
    }
  };

  const getPerformanceIcon = (score) => {
    if (score >= 90) return <TrendingUp className="performance-icon good" size={16} />;
    if (score >= 70) return <Minus className="performance-icon average" size={16} />;
    return <TrendingDown className="performance-icon poor" size={16} />;
  };

  const renderToolbar = () => (
    <div className="history-toolbar">
      <div className="toolbar-left">
        <div className="search-box">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Buscar en historial..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>

        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="filter-select"
        >
          <option value="all">Todos los estados</option>
          <option value="success">Sin errores</option>
          <option value="errors">Con errores</option>
          <option value="warnings">Con advertencias</option>
        </select>

        <select
          value={filterDate}
          onChange={(e) => setFilterDate(e.target.value)}
          className="filter-select"
        >
          <option value="all">Todas las fechas</option>
          <option value="today">Hoy</option>
          <option value="week">Última semana</option>
          <option value="month">Último mes</option>
        </select>

        <select
          value={groupBy}
          onChange={(e) => setGroupBy(e.target.value)}
          className="filter-select"
        >
          <option value="none">Sin agrupar</option>
          <option value="date">Agrupar por fecha</option>
          <option value="status">Agrupar por estado</option>
          <option value="engine">Agrupar por motor</option>
        </select>
      </div>

      <div className="toolbar-center">
        <div className="view-mode-toggle">
          <button
            className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
            onClick={() => setViewMode('grid')}
            title="Vista de cuadrícula"
          >
            <BarChart3 size={16} />
          </button>
          <button
            className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
            onClick={() => setViewMode('list')}
            title="Vista de lista"
          >
            <FileText size={16} />
          </button>
          <button
            className={`view-btn ${viewMode === 'timeline' ? 'active' : ''}`}
            onClick={() => setViewMode('timeline')}
            title="Vista cronológica"
          >
            <Clock size={16} />
          </button>
        </div>
      </div>

      <div className="toolbar-right">
        <div className="analysis-stats">
          {(() => {
            const stats = getAnalysisStats();
            return (
              <div className="stats-summary">
                <span className="stat-item">
                  <BarChart3 size={14} />
                  {stats.total} análisis
                </span>
                <span className="stat-item">
                  <AlertTriangle size={14} />
                  {stats.withErrors} errores
                </span>
                <span className="stat-item">
                  <Zap size={14} />
                  {Math.round(stats.avgScore)}% promedio
                </span>
              </div>
            );
          })()}
        </div>

        {selectedItems.length > 0 && (
          <>
            <button
              className="btn-danger"
              onClick={handleBulkDelete}
            >
              <Trash2 size={16} />
              Eliminar ({selectedItems.length})
            </button>
            <button
              className="btn-secondary"
              onClick={handleExportSelected}
            >
              <Download size={16} />
              Exportar Seleccionados
            </button>
          </>
        )}

        <select
          value={`${sortBy}-${sortOrder}`}
          onChange={(e) => {
            const [field, order] = e.target.value.split('-');
            setSortBy(field);
            setSortOrder(order);
          }}
          className="sort-select"
        >
          <option value="date-desc">Más reciente</option>
          <option value="date-asc">Más antiguo</option>
          <option value="name-asc">Nombre A-Z</option>
          <option value="name-desc">Nombre Z-A</option>
          <option value="errors-desc">Más errores</option>
          <option value="errors-asc">Menos errores</option>
          <option value="score-desc">Mejor puntuación</option>
          <option value="score-asc">Peor puntuación</option>
        </select>
      </div>
    </div>
  );

  const renderHistoryItem = (item) => (
    <div
      key={item.id}
      className={`history-item ${selectedItems.includes(item.id) ? 'selected' : ''}`}
    >
      <div className="item-header">
        <div className="item-select">
          <input
            type="checkbox"
            checked={selectedItems.includes(item.id)}
            onChange={() => handleSelectItem(item.id)}
          />
        </div>

        <div className="item-info">
          <div className="item-title">
            <Code size={16} className="item-icon" />
            <h3>{item.title || `Análisis ${item.id}`}</h3>
            <button
              className="favorite-btn"
              onClick={() => toggleFavorite(item.id)}
            >
              {favorites.includes(item.id) ? (
                <Star size={16} className="favorite-active" />
              ) : (
                <StarOff size={16} />
              )}
            </button>
          </div>

          <div className="item-meta">
            <span className="meta-item">
              <Calendar size={12} />
              {new Date(item.timestamp).toLocaleString()}
            </span>
            <span className="meta-item">
              <Database size={12} />
              {item.connection || 'Sin conexión'}
            </span>
            <span className="meta-item">
              <FileText size={12} />
              {item.lineCount || 0} líneas
            </span>
          </div>
        </div>

        <div className="item-status">
          {getStatusBadge(item)}
          <div className="performance-score">
            {getPerformanceIcon(item.summary?.performance_score || 100)}
            <span>{item.summary?.performance_score || 100}%</span>
          </div>
        </div>

        <div className="item-actions">
          <button
            className="action-btn"
            onClick={() => onViewAnalysis(item)}
            title="Ver análisis"
          >
            <Eye size={16} />
          </button>
          <button
            className="action-btn"
            onClick={() => onRerunAnalysis(item)}
            title="Ejecutar de nuevo"
          >
            <RefreshCw size={16} />
          </button>
          <button
            className="action-btn"
            onClick={() => handleExportSingle(item)}
            title="Exportar"
          >
            <Download size={16} />
          </button>
          <button
            className="action-btn"
            onClick={() => setShowDetails(item)}
            title="Ver detalles"
          >
            <BarChart3 size={16} />
          </button>
          <button
            className="action-btn danger"
            onClick={() => onDeleteAnalysis(item.id)}
            title="Eliminar"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      <div className="item-preview">
        <div className="sql-preview">
          <code>{item.content?.substring(0, 150)}...</code>
        </div>
      </div>
    </div>
  );

  const renderDetailsModal = () => {
    if (!showDetails) return null;

    return (
      <div className="details-modal">
        <div className="modal-backdrop" onClick={() => setShowDetails(null)}></div>
        <div className="modal-content">
          <div className="modal-header">
            <h3>Detalles del Análisis</h3>
            <button
              className="modal-close"
              onClick={() => setShowDetails(null)}
            >
              ×
            </button>
          </div>
          <div className="modal-body">
            <div className="details-grid">
              <div className="detail-item">
                <label>Título:</label>
                <span>{showDetails.title}</span>
              </div>
              <div className="detail-item">
                <label>Fecha:</label>
                <span>{new Date(showDetails.timestamp).toLocaleString()}</span>
              </div>
              <div className="detail-item">
                <label>Conexión:</label>
                <span>{showDetails.connection || 'Sin conexión'}</span>
              </div>
              <div className="detail-item">
                <label>Líneas de código:</label>
                <span>{showDetails.lineCount || 0}</span>
              </div>
              <div className="detail-item">
                <label>Tamaño del archivo:</label>
                <span>{showDetails.fileSize ? `${(showDetails.fileSize / 1024).toFixed(1)} KB` : 'N/A'}</span>
              </div>
              <div className="detail-item">
                <label>Errores totales:</label>
                <span>{showDetails.summary?.total_errors || 0}</span>
              </div>
              <div className="detail-item">
                <label>Advertencias:</label>
                <span>{showDetails.summary?.total_warnings || 0}</span>
              </div>
              <div className="detail-item">
                <label>Puntuación de rendimiento:</label>
                <span>{showDetails.summary?.performance_score || 100}%</span>
              </div>
            </div>

            <div className="sql-content">
              <h4>Contenido SQL:</h4>
              <pre><code>{showDetails.content}</code></pre>
            </div>
          </div>
          <div className="modal-footer">
            <button
              className="btn-primary"
              onClick={() => {
                onViewAnalysis(showDetails);
                setShowDetails(null);
              }}
            >
              <Eye size={16} />
              Ver Análisis Completo
            </button>
            <button
              className="btn-secondary"
              onClick={() => setShowDetails(null)}
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="history-view">
      <div className="view-header">
        <div className="header-title">
          <History size={24} />
          <div>
            <h1>Historial de Análisis</h1>
            <p>{filteredHistory.length} de {analysisHistory.length} análisis</p>
          </div>
        </div>
        <div className="header-actions">
          {selectedItems.length > 0 && (
            <button onClick={handleSelectAll}>
              Deseleccionar todo
            </button>
          )}
          {selectedItems.length === 0 && filteredHistory.length > 0 && (
            <button onClick={handleSelectAll}>
              Seleccionar todo
            </button>
          )}
        </div>
      </div>

      {renderToolbar()}

      <div className="history-content">
        {filteredHistory.length === 0 ? (
          analysisHistory.length === 0 ? (
            <div className="empty-state">
              <History size={64} className="empty-icon" />
              <h3>No hay análisis en el historial</h3>
              <p>Los análisis que realices aparecerán aquí</p>
            </div>
          ) : (
            <div className="no-results">
              <Search size={48} />
              <h3>No se encontraron análisis</h3>
              <p>Intenta cambiar los filtros de búsqueda</p>
            </div>
          )
        ) : (
          <div className={`history-content-${viewMode}`}>
            {(() => {
              const groupedAnalyses = groupAnalyses(filteredHistory);

              return Object.entries(groupedAnalyses).map(([groupName, analyses]) => (
                <div key={groupName} className="analysis-group">
                  {groupBy !== 'none' && (
                    <div className="group-header">
                      <h3>{groupName}</h3>
                      <span className="group-count">({analyses.length})</span>
                    </div>
                  )}
                  <div className={`history-list ${viewMode}`}>
                    {analyses.map(renderHistoryItem)}
                  </div>
                </div>
              ));
            })()}
          </div>
        )}
      </div>

      {renderDetailsModal()}

      <ExportSystem
        analysisData={exportData}
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        onExportComplete={handleExportComplete}
      />
    </div>
  );
};

export default HistoryView;
