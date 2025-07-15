import React, { useState, useEffect } from 'react';
import {
  Download,
  FileText,
  Database,
  Image,
  Archive,
  Code,
  Presentation,
  Table,
  Search,
  Check,
  Loader,
  AlertTriangle,
  RefreshCw,
  X,
  ChevronDown
} from 'lucide-react';
import { getExportFormats, exportAnalysis, downloadFile } from '../utils/api';

const ExportSystem = ({ 
  analysisData, 
  isOpen, 
  onClose, 
  onExportComplete 
}) => {
  const [formats, setFormats] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [exporting, setExporting] = useState({});
  const [exportHistory, setExportHistory] = useState([]);

  useEffect(() => {
    if (isOpen) {
      loadExportFormats();
    }
  }, [isOpen]);

  const loadExportFormats = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getExportFormats();
      
      setFormats(response.formats || []);
      setCategories(['all', ...(response.categories || [])]);
    } catch (err) {
      console.error('Failed to load export formats:', err);
      setError('Error cargando formatos de exportación');
      
      // Fallback formats
      const fallbackFormats = [
        { format: 'json', name: 'JSON', category: 'data', description: 'JavaScript Object Notation', file_extension: '.json', mime_type: 'application/json' },
        { format: 'html', name: 'HTML', category: 'document', description: 'HyperText Markup Language', file_extension: '.html', mime_type: 'text/html' },
        { format: 'pdf', name: 'PDF', category: 'document', description: 'Portable Document Format', file_extension: '.pdf', mime_type: 'application/pdf' },
        { format: 'csv', name: 'CSV', category: 'spreadsheet', description: 'Comma Separated Values', file_extension: '.csv', mime_type: 'text/csv' },
        { format: 'xlsx', name: 'Excel', category: 'spreadsheet', description: 'Microsoft Excel', file_extension: '.xlsx', mime_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
      ];
      setFormats(fallbackFormats);
      setCategories(['all', 'document', 'spreadsheet', 'data']);
    } finally {
      setLoading(false);
    }
  };

  const filteredFormats = formats.filter(format => {
    const matchesSearch = format.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         format.format.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (format.description && format.description.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || format.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const handleExport = async (format) => {
    if (!analysisData) {
      alert('No hay datos de análisis para exportar');
      return;
    }

    try {
      setExporting(prev => ({ ...prev, [format.format]: true }));
      
      const blob = await exportAnalysis(analysisData, format.format);
      const filename = `sql_analysis_${new Date().toISOString().replace(/[:.]/g, '-')}${format.file_extension}`;
      
      downloadFile(blob, format.format, filename);
      
      // Add to export history
      const exportRecord = {
        id: Date.now(),
        format: format.format,
        name: format.name,
        filename,
        timestamp: new Date().toISOString(),
        size: blob.size
      };
      
      setExportHistory(prev => [exportRecord, ...prev.slice(0, 9)]);
      
      if (onExportComplete) {
        onExportComplete(exportRecord);
      }
      
    } catch (error) {
      console.error(`Export failed for ${format.format}:`, error);
      alert(`Error exportando como ${format.name}: ${error.message}`);
    } finally {
      setExporting(prev => ({ ...prev, [format.format]: false }));
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      document: FileText,
      spreadsheet: Table,
      data: Database,
      database: Database,
      presentation: Presentation,
      archive: Archive,
      specialized: Code,
      web: Code
    };
    return icons[category] || FileText;
  };

  const getCategoryName = (category) => {
    const names = {
      document: 'Documentos',
      spreadsheet: 'Hojas de Cálculo',
      data: 'Datos',
      database: 'Base de Datos',
      presentation: 'Presentaciones',
      archive: 'Archivos',
      specialized: 'Especializados',
      web: 'Web'
    };
    return names[category] || category;
  };

  const getFormatIcon = (format) => {
    const icons = {
      pdf: FileText,
      html: Code,
      json: Database,
      csv: Table,
      xlsx: Table,
      docx: FileText,
      pptx: Presentation,
      zip: Archive,
      sql: Database
    };
    return icons[format.format] || FileText;
  };

  if (!isOpen) return null;

  return (
    <div className="export-system-overlay">
      <div className="export-system-modal">
        <div className="modal-header">
          <div className="header-title">
            <Download size={20} />
            <h2>Sistema de Exportación</h2>
            <span className="formats-count">
              {formats.length} formatos disponibles
            </span>
          </div>
          <button 
            className="close-button"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </div>

        <div className="modal-content">
          {loading ? (
            <div className="loading-state">
              <Loader className="animate-spin" size={24} />
              <p>Cargando formatos de exportación...</p>
            </div>
          ) : (
            <>
              <div className="export-controls">
                <div className="search-container">
                  <Search size={16} />
                  <input
                    type="text"
                    placeholder="Buscar formato..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="search-input"
                  />
                </div>

                <div className="category-filter">
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="category-select"
                  >
                    <option value="all">Todas las categorías</option>
                    {categories.filter(cat => cat !== 'all').map(category => (
                      <option key={category} value={category}>
                        {getCategoryName(category)}
                      </option>
                    ))}
                  </select>
                  <ChevronDown size={16} className="select-icon" />
                </div>

                {error && (
                  <div className="error-message">
                    <AlertTriangle size={16} />
                    <span>{error}</span>
                    <button onClick={loadExportFormats} className="retry-btn">
                      <RefreshCw size={14} />
                    </button>
                  </div>
                )}
              </div>

              <div className="formats-grid">
                {filteredFormats.length === 0 ? (
                  <div className="no-formats">
                    <AlertTriangle size={24} />
                    <p>No se encontraron formatos</p>
                  </div>
                ) : (
                  filteredFormats.map((format) => {
                    const FormatIcon = getFormatIcon(format);
                    const isExporting = exporting[format.format];
                    
                    return (
                      <div key={format.format} className="format-card">
                        <div className="format-header">
                          <FormatIcon size={20} className="format-icon" />
                          <div className="format-info">
                            <h3 className="format-name">{format.name}</h3>
                            <span className="format-extension">{format.file_extension}</span>
                          </div>
                        </div>
                        
                        {format.description && (
                          <p className="format-description">{format.description}</p>
                        )}
                        
                        <div className="format-meta">
                          <span className="format-category">
                            {getCategoryName(format.category)}
                          </span>
                          {format.mime_type && (
                            <span className="format-mime">{format.mime_type}</span>
                          )}
                        </div>
                        
                        <button
                          className={`export-button ${isExporting ? 'exporting' : ''}`}
                          onClick={() => handleExport(format)}
                          disabled={isExporting}
                        >
                          {isExporting ? (
                            <>
                              <Loader className="animate-spin" size={16} />
                              Exportando...
                            </>
                          ) : (
                            <>
                              <Download size={16} />
                              Exportar
                            </>
                          )}
                        </button>
                      </div>
                    );
                  })
                )}
              </div>

              {exportHistory.length > 0 && (
                <div className="export-history">
                  <h3>Exportaciones Recientes</h3>
                  <div className="history-list">
                    {exportHistory.map((record) => (
                      <div key={record.id} className="history-item">
                        <div className="history-info">
                          <span className="history-format">{record.name}</span>
                          <span className="history-filename">{record.filename}</span>
                          <span className="history-time">
                            {new Date(record.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="history-size">
                          {(record.size / 1024).toFixed(1)} KB
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExportSystem;
