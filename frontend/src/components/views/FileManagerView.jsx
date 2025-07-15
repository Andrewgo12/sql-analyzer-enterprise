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
  Info
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
      return <FileText className="file-icon sql" size={24} />;
    }
    return <FileText className="file-icon txt" size={24} />;
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

  const renderFileCard = (file) => (
    <div 
      key={file.id}
      className={`file-card ${selectedFiles.includes(file.id) ? 'selected' : ''} ${viewMode}`}
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
        <div className="file-actions">
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
        </div>
      </div>
      
      {viewMode === 'list' && (
        <div className="file-card-details">
          <div className="file-preview">
            {file.content.substring(0, 100)}...
          </div>
        </div>
      )}
    </div>
  );

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
