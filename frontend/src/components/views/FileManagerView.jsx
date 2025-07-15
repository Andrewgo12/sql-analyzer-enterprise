import React, { useState, useEffect } from 'react';
import {
  FolderOpen,
  Upload,
  FileText,
  Trash2,
  Edit,
  Eye,
  Download,
  Search,
  Filter,
  Grid,
  List,
  SortAsc,
  SortDesc,
  Calendar,
  HardDrive,
  CheckSquare,
  Square,
  MoreVertical,
  Copy,
  Move,
  Star,
  StarOff,
  Info,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Database,
  Archive,
  RefreshCw,
  Settings,
  Tag,
  Share,
  Lock,
  Unlock
} from 'lucide-react';

const FileManagerView = ({
  uploadedFiles,
  setUploadedFiles,
  selectedFiles,
  setSelectedFiles,
  onFileSelect,
  onFileDelete,
  onFileEdit,
  dragActive,
  onDragOver,
  onDragLeave,
  onDrop,
  onFileUpload
}) => {
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [sortBy, setSortBy] = useState('name'); // 'name', 'date', 'size'
  const [sortOrder, setSortOrder] = useState('asc'); // 'asc' or 'desc'
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all'); // 'all', 'sql', 'txt'
  const [showFileInfo, setShowFileInfo] = useState(null);
  const [batchMode, setBatchMode] = useState(false);
  const [selectedForBatch, setSelectedForBatch] = useState([]);
  const [validationResults, setValidationResults] = useState({});
  const [processingFiles, setProcessingFiles] = useState([]);
  const [showBatchActions, setShowBatchActions] = useState(false);
  const [filePreview, setFilePreview] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [tags, setTags] = useState({});
  const [showTagEditor, setShowTagEditor] = useState(null);

  const filteredFiles = uploadedFiles
    .filter(file => {
      const matchesSearch = file.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        file.content.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter = filterType === 'all' ||
        (filterType === 'sql' && file.name.endsWith('.sql')) ||
        (filterType === 'txt' && file.name.endsWith('.txt'));
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'date':
          comparison = new Date(a.uploadDate) - new Date(b.uploadDate);
          break;
        case 'size':
          comparison = a.size - b.size;
          break;
        default:
          comparison = 0;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  const handleSelectAll = () => {
    if (selectedFiles.length === filteredFiles.length) {
      setSelectedFiles([]);
    } else {
      setSelectedFiles(filteredFiles.map(file => file.id));
    }
  };

  const handleFileSelect = (fileId) => {
    if (selectedFiles.includes(fileId)) {
      setSelectedFiles(selectedFiles.filter(id => id !== fileId));
    } else {
      setSelectedFiles([...selectedFiles, fileId]);
    }
  };

  const handleBulkDelete = () => {
    if (window.confirm(`¿Eliminar ${selectedFiles.length} archivos seleccionados?`)) {
      setUploadedFiles(prev => prev.filter(file => !selectedFiles.includes(file.id)));
      setSelectedFiles([]);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileName) => {
    if (fileName.endsWith('.sql')) {
      return <Database className="file-icon sql" size={24} />;
    }
    return <FileText className="file-icon txt" size={24} />;
  };

  const validateFile = async (file) => {
    setProcessingFiles(prev => [...prev, file.id]);

    try {
      // Simulate file validation
      await new Promise(resolve => setTimeout(resolve, 1000));

      const validation = {
        isValid: Math.random() > 0.2, // 80% success rate
        errors: [],
        warnings: [],
        suggestions: [],
        stats: {
          lines: Math.floor(Math.random() * 1000) + 10,
          size: file.size,
          encoding: 'UTF-8',
          sqlStatements: Math.floor(Math.random() * 50) + 1
        }
      };

      if (!validation.isValid) {
        validation.errors.push('Sintaxis SQL inválida en línea 45');
        validation.errors.push('Tabla no encontrada: usuarios_temp');
      } else {
        validation.warnings.push('Consulta compleja detectada');
        validation.suggestions.push('Considera agregar índices para mejorar rendimiento');
      }

      setValidationResults(prev => ({
        ...prev,
        [file.id]: validation
      }));

    } catch (error) {
      setValidationResults(prev => ({
        ...prev,
        [file.id]: {
          isValid: false,
          errors: ['Error al validar archivo'],
          warnings: [],
          suggestions: []
        }
      }));
    } finally {
      setProcessingFiles(prev => prev.filter(id => id !== file.id));
    }
  };

  const handleBatchValidation = async () => {
    const filesToValidate = uploadedFiles.filter(file =>
      selectedForBatch.includes(file.id) && !validationResults[file.id]
    );

    for (const file of filesToValidate) {
      await validateFile(file);
    }
  };

  const handleBatchAnalysis = () => {
    const filesToAnalyze = uploadedFiles.filter(file =>
      selectedForBatch.includes(file.id)
    );

    filesToAnalyze.forEach(file => {
      onFileSelect(file);
    });
  };

  const toggleBatchSelection = (fileId) => {
    if (selectedForBatch.includes(fileId)) {
      setSelectedForBatch(prev => prev.filter(id => id !== fileId));
    } else {
      setSelectedForBatch(prev => [...prev, fileId]);
    }
  };

  const toggleFavorite = (fileId) => {
    if (favorites.includes(fileId)) {
      setFavorites(prev => prev.filter(id => id !== fileId));
    } else {
      setFavorites(prev => [...prev, fileId]);
    }
  };

  const addTag = (fileId, tag) => {
    setTags(prev => ({
      ...prev,
      [fileId]: [...(prev[fileId] || []), tag]
    }));
  };

  const removeTag = (fileId, tagToRemove) => {
    setTags(prev => ({
      ...prev,
      [fileId]: (prev[fileId] || []).filter(tag => tag !== tagToRemove)
    }));
  };

  const getFileStats = () => {
    const total = filteredFiles.length;
    const validated = Object.keys(validationResults).length;
    const valid = Object.values(validationResults).filter(r => r.isValid).length;
    const totalSize = filteredFiles.reduce((sum, file) => sum + file.size, 0);

    return { total, validated, valid, totalSize };
  };

  const renderToolbar = () => (
    <div className="file-manager-toolbar">
      <div className="toolbar-left">
        <input
          type="file"
          id="file-upload-input"
          multiple
          accept=".sql,.txt"
          onChange={(e) => onFileUpload(e.target.files)}
          style={{ display: 'none' }}
        />
        <button
          className="btn-primary"
          onClick={() => document.getElementById('file-upload-input').click()}
        >
          <Upload size={16} />
          Cargar Archivos
        </button>

        <button
          className={`btn-secondary ${batchMode ? 'active' : ''}`}
          onClick={() => setBatchMode(!batchMode)}
        >
          <CheckSquare size={16} />
          Modo Lote
        </button>

        {selectedFiles.length > 0 && (
          <>
            <button
              className="btn-danger"
              onClick={handleBulkDelete}
            >
              <Trash2 size={16} />
              Eliminar ({selectedFiles.length})
            </button>
            <button className="btn-secondary">
              <Download size={16} />
              Descargar
            </button>
          </>
        )}

        {batchMode && selectedForBatch.length > 0 && (
          <>
            <button
              className="btn-primary"
              onClick={handleBatchValidation}
            >
              <CheckCircle size={16} />
              Validar ({selectedForBatch.length})
            </button>
            <button
              className="btn-secondary"
              onClick={handleBatchAnalysis}
            >
              <Zap size={16} />
              Analizar Lote
            </button>
          </>
        )}
      </div>

      <div className="toolbar-center">
        <div className="search-box">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Buscar archivos..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="toolbar-right">
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="filter-select"
        >
          <option value="all">Todos los archivos</option>
          <option value="sql">Archivos SQL</option>
          <option value="txt">Archivos de texto</option>
        </select>

        <select
          value={`${sortBy}-${sortOrder}`}
          onChange={(e) => {
            const [field, order] = e.target.value.split('-');
            setSortBy(field);
            setSortOrder(order);
          }}
          className="sort-select"
        >
          <option value="name-asc">Nombre A-Z</option>
          <option value="name-desc">Nombre Z-A</option>
          <option value="date-desc">Más reciente</option>
          <option value="date-asc">Más antiguo</option>
          <option value="size-desc">Mayor tamaño</option>
          <option value="size-asc">Menor tamaño</option>
        </select>

        <div className="file-stats">
          {(() => {
            const stats = getFileStats();
            return (
              <div className="stats-display">
                <span className="stat-item">
                  <FileText size={14} />
                  {stats.total} archivos
                </span>
                <span className="stat-item">
                  <CheckCircle size={14} />
                  {stats.valid}/{stats.validated} válidos
                </span>
                <span className="stat-item">
                  <HardDrive size={14} />
                  {formatFileSize(stats.totalSize)}
                </span>
              </div>
            );
          })()}
        </div>

        <div className="view-toggle">
          <button
            className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
            onClick={() => setViewMode('grid')}
          >
            <Grid size={16} />
          </button>
          <button
            className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
            onClick={() => setViewMode('list')}
          >
            <List size={16} />
          </button>
        </div>
      </div>
    </div>
  );

  const renderFileCard = (file) => {
    const validation = validationResults[file.id];
    const isProcessing = processingFiles.includes(file.id);
    const isFavorite = favorites.includes(file.id);
    const fileTags = tags[file.id] || [];

    return (
      <div
        key={file.id}
        className={`file-card ${selectedFiles.includes(file.id) ? 'selected' : ''} ${viewMode} ${validation?.isValid === false ? 'invalid' : ''}`}
        onClick={() => handleFileSelect(file.id)}
      >
        <div className="file-card-header">
          <div className="file-select">
            {selectedFiles.includes(file.id) ? (
              <CheckSquare size={16} className="select-icon selected" />
            ) : (
              <Square size={16} className="select-icon" />
            )}
          </div>

          {batchMode && (
            <div className="batch-select">
              <input
                type="checkbox"
                checked={selectedForBatch.includes(file.id)}
                onChange={(e) => {
                  e.stopPropagation();
                  toggleBatchSelection(file.id);
                }}
                className="batch-checkbox"
              />
            </div>
          )}

          <div className="file-status">
            {isProcessing && (
              <RefreshCw size={14} className="processing-icon spinning" />
            )}
            {validation && (
              <div className={`validation-status ${validation.isValid ? 'valid' : 'invalid'}`}>
                {validation.isValid ? (
                  <CheckCircle size={14} />
                ) : (
                  <AlertTriangle size={14} />
                )}
              </div>
            )}
          </div>

          <div className="file-actions">
            <button
              className="action-btn"
              onClick={(e) => {
                e.stopPropagation();
                toggleFavorite(file.id);
              }}
              title={isFavorite ? "Quitar de favoritos" : "Agregar a favoritos"}
            >
              {isFavorite ? <Star size={14} /> : <StarOff size={14} />}
            </button>

            <button
              className="action-btn"
              onClick={(e) => {
                e.stopPropagation();
                validateFile(file);
              }}
              title="Validar archivo"
              disabled={isProcessing}
            >
              {isProcessing ? <RefreshCw size={14} className="spinning" /> : <CheckCircle size={14} />}
            </button>

            <button
              className="action-btn"
              onClick={(e) => {
                e.stopPropagation();
                onFileEdit(file);
              }}
              title="Editar archivo"
            >
              <Edit size={14} />
            </button>

            <button
              className="action-btn"
              onClick={(e) => {
                e.stopPropagation();
                setShowFileInfo(file);
              }}
              title="Información del archivo"
            >
              <Info size={14} />
            </button>

            <button
              className="action-btn danger"
              onClick={(e) => {
                e.stopPropagation();
                onFileDelete(file.id);
              }}
              title="Eliminar archivo"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>

        <div className="file-card-content">
          <div className="file-icon-container">
            {getFileIcon(file.name)}
          </div>
          <div className="file-info">
            <div className="file-name" title={file.name}>{file.name}</div>
            <div className="file-meta">
              <span className="file-size">{formatFileSize(file.size)}</span>
              <span className="file-date">
                {new Date(file.uploadDate).toLocaleDateString()}
              </span>
            </div>

            {fileTags.length > 0 && (
              <div className="file-tags">
                {fileTags.map((tag, index) => (
                  <span key={index} className="file-tag">
                    <Tag size={10} />
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {validation && (
          <div className={`validation-summary ${validation.isValid ? 'valid' : 'invalid'}`}>
            <div className="validation-header">
              {validation.isValid ? (
                <CheckCircle size={14} />
              ) : (
                <AlertTriangle size={14} />
              )}
              <span>{validation.isValid ? 'Válido' : 'Errores encontrados'}</span>
            </div>

            {validation.stats && (
              <div className="validation-stats">
                <span>{validation.stats.lines} líneas</span>
                <span>{validation.stats.sqlStatements} consultas</span>
              </div>
            )}

            {validation.errors.length > 0 && (
              <div className="validation-errors">
                {validation.errors.slice(0, 2).map((error, index) => (
                  <div key={index} className="error-item">
                    <AlertTriangle size={10} />
                    {error}
                  </div>
                ))}
                {validation.errors.length > 2 && (
                  <div className="more-errors">
                    +{validation.errors.length - 2} más
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {viewMode === 'list' && (
          <div className="file-card-details">
            <div className="file-preview">
              {file.content.substring(0, 100)}...
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderEmptyState = () => (
    <div
      className={`empty-state ${dragActive ? 'drag-active' : ''}`}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      <FolderOpen size={64} className="empty-icon" />
      <h3>No hay archivos cargados</h3>
      <p>Arrastra archivos SQL aquí o usa el botón "Cargar Archivos"</p>
      <button
        className="btn-primary"
        onClick={() => document.getElementById('file-upload-input').click()}
      >
        <Upload size={16} />
        Seleccionar Archivos
      </button>

      {dragActive && (
        <div className="drag-overlay">
          <Upload size={48} />
          <p>Suelta los archivos SQL aquí</p>
        </div>
      )}
    </div>
  );

  const renderFileInfo = () => {
    if (!showFileInfo) return null;

    return (
      <div className="file-info-modal">
        <div className="modal-backdrop" onClick={() => setShowFileInfo(null)}></div>
        <div className="modal-content">
          <div className="modal-header">
            <h3>Información del Archivo</h3>
            <button
              className="modal-close"
              onClick={() => setShowFileInfo(null)}
            >
              ×
            </button>
          </div>
          <div className="modal-body">
            <div className="info-row">
              <label>Nombre:</label>
              <span>{showFileInfo.name}</span>
            </div>
            <div className="info-row">
              <label>Tamaño:</label>
              <span>{formatFileSize(showFileInfo.size)}</span>
            </div>
            <div className="info-row">
              <label>Fecha de carga:</label>
              <span>{new Date(showFileInfo.uploadDate).toLocaleString()}</span>
            </div>
            <div className="info-row">
              <label>Última modificación:</label>
              <span>{new Date(showFileInfo.lastModified).toLocaleString()}</span>
            </div>
            <div className="info-row">
              <label>Tipo:</label>
              <span>{showFileInfo.type}</span>
            </div>
            <div className="info-row">
              <label>Líneas:</label>
              <span>{showFileInfo.content.split('\n').length}</span>
            </div>
          </div>
          <div className="modal-footer">
            <button
              className="btn-primary"
              onClick={() => {
                onFileEdit(showFileInfo);
                setShowFileInfo(null);
              }}
            >
              <Edit size={16} />
              Editar
            </button>
            <button
              className="btn-secondary"
              onClick={() => setShowFileInfo(null)}
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="file-manager-view">
      <div className="view-header">
        <div className="header-title">
          <FolderOpen size={24} />
          <div>
            <h1>Gestión de Archivos SQL</h1>
            <p>{filteredFiles.length} de {uploadedFiles.length} archivos</p>
          </div>
        </div>
      </div>

      {renderToolbar()}

      <div className="file-manager-content">
        {filteredFiles.length > 0 && (
          <div className="files-header">
            <div className="select-all">
              <button onClick={handleSelectAll}>
                {selectedFiles.length === filteredFiles.length ? (
                  <CheckSquare size={16} />
                ) : (
                  <Square size={16} />
                )}
                Seleccionar todo
              </button>
            </div>
            <div className="files-stats">
              {selectedFiles.length > 0 && (
                <span>{selectedFiles.length} seleccionados</span>
              )}
            </div>
          </div>
        )}

        {filteredFiles.length === 0 ? (
          uploadedFiles.length === 0 ? renderEmptyState() : (
            <div className="no-results">
              <Search size={48} />
              <h3>No se encontraron archivos</h3>
              <p>Intenta cambiar los filtros de búsqueda</p>
            </div>
          )
        ) : (
          <div className={`files-container ${viewMode}`}>
            {filteredFiles.map(renderFileCard)}
          </div>
        )}
      </div>

      {renderFileInfo()}
    </div>
  );
};

export default FileManagerView;
