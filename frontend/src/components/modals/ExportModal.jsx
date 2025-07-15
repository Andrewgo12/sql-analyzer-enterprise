import React, { useState, useEffect } from 'react';
import { 
  X, 
  Download, 
  FileText, 
  Database, 
  Image,
  Archive,
  Code,
  Presentation,
  CheckCircle,
  AlertCircle,
  Info,
  Eye,
  Settings
} from 'lucide-react';

const ExportModal = ({ isOpen, onClose, onExport, currentAnalysis }) => {
  const [selectedFormat, setSelectedFormat] = useState('json');
  const [exportOptions, setExportOptions] = useState({
    includeCharts: true,
    includeImages: false,
    includeRawData: true,
    includeRecommendations: true,
    includeSchema: false,
    compressionLevel: 'medium'
  });
  const [availableFormats, setAvailableFormats] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load available export formats from API
  useEffect(() => {
    if (isOpen) {
      loadExportFormats();
    }
  }, [isOpen]);

  const loadExportFormats = async () => {
    try {
      const response = await fetch('/api/export/formats');
      const data = await response.json();
      setAvailableFormats(data.formats || []);
    } catch (error) {
      console.error('Error loading export formats:', error);
      // Fallback formats
      setAvailableFormats([
        {
          format: 'json',
          name: 'JSON Data',
          category: 'data',
          description: 'Structured JSON format for API integration',
          file_extension: 'json',
          supports_charts: false,
          supports_images: false,
          supports_styling: false,
          is_binary: false
        },
        {
          format: 'html',
          name: 'HTML Document',
          category: 'document',
          description: 'Interactive HTML report with embedded CSS',
          file_extension: 'html',
          supports_charts: true,
          supports_images: true,
          supports_styling: true,
          is_binary: false
        },
        {
          format: 'pdf',
          name: 'PDF Document',
          category: 'document',
          description: 'Professional PDF report with styling',
          file_extension: 'pdf',
          supports_charts: true,
          supports_images: true,
          supports_styling: true,
          is_binary: true
        },
        {
          format: 'xlsx',
          name: 'Excel Workbook',
          category: 'spreadsheet',
          description: 'Multi-sheet Excel workbook',
          file_extension: 'xlsx',
          supports_charts: true,
          supports_images: true,
          supports_styling: true,
          is_binary: true
        }
      ]);
    }
  };

  const formatCategories = {
    document: { icon: <FileText size={16} />, label: 'Documentos', color: 'blue' },
    spreadsheet: { icon: <Database size={16} />, label: 'Hojas de Cálculo', color: 'green' },
    data: { icon: <Code size={16} />, label: 'Datos', color: 'purple' },
    presentation: { icon: <Presentation size={16} />, label: 'Presentaciones', color: 'orange' },
    archive: { icon: <Archive size={16} />, label: 'Archivos', color: 'gray' },
    specialized: { icon: <Settings size={16} />, label: 'Especializados', color: 'teal' }
  };

  const groupedFormats = availableFormats.reduce((groups, format) => {
    const category = format.category || 'data';
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(format);
    return groups;
  }, {});

  const selectedFormatInfo = availableFormats.find(f => f.format === selectedFormat);

  const handleExport = async () => {
    if (!currentAnalysis) {
      alert('No hay análisis disponible para exportar');
      return;
    }

    setIsLoading(true);
    try {
      await onExport(selectedFormat, exportOptions);
    } catch (error) {
      console.error('Export error:', error);
      alert('Error durante la exportación');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptionChange = (option) => {
    setExportOptions(prev => ({
      ...prev,
      [option]: !prev[option]
    }));
  };

  const getFormatIcon = (format) => {
    switch (format.category) {
      case 'document':
        return <FileText size={20} />;
      case 'spreadsheet':
        return <Database size={20} />;
      case 'presentation':
        return <Presentation size={20} />;
      case 'archive':
        return <Archive size={20} />;
      case 'data':
        return <Code size={20} />;
      default:
        return <FileText size={20} />;
    }
  };

  const getFeatureIcon = (supported) => {
    return supported ? (
      <CheckCircle className="feature-supported" size={14} />
    ) : (
      <X className="feature-not-supported" size={14} />
    );
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container large">
        <div className="modal-header">
          <div className="modal-title">
            <Download size={20} />
            <span>Exportar Análisis</span>
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-content">
          {!currentAnalysis ? (
            <div className="no-analysis-warning">
              <AlertCircle size={48} />
              <h3>No hay análisis disponible</h3>
              <p>Ejecuta un análisis antes de exportar los resultados</p>
            </div>
          ) : (
            <>
              {/* Format Selection */}
              <div className="export-section">
                <h3>Seleccionar Formato</h3>
                <div className="format-categories">
                  {Object.entries(groupedFormats).map(([category, formats]) => (
                    <div key={category} className="format-category">
                      <div className="category-header">
                        {formatCategories[category]?.icon}
                        <span>{formatCategories[category]?.label || category}</span>
                        <span className="format-count">({formats.length})</span>
                      </div>
                      
                      <div className="format-grid">
                        {formats.map(format => (
                          <div
                            key={format.format}
                            className={`format-card ${selectedFormat === format.format ? 'selected' : ''}`}
                            onClick={() => setSelectedFormat(format.format)}
                          >
                            <div className="format-icon">
                              {getFormatIcon(format)}
                            </div>
                            <div className="format-info">
                              <h4>{format.name}</h4>
                              <p>{format.description}</p>
                              <div className="format-features">
                                <span className="feature">
                                  {getFeatureIcon(format.supports_charts)}
                                  Gráficos
                                </span>
                                <span className="feature">
                                  {getFeatureIcon(format.supports_styling)}
                                  Estilos
                                </span>
                                <span className="feature">
                                  {getFeatureIcon(!format.is_binary)}
                                  Texto
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Format Details */}
              {selectedFormatInfo && (
                <div className="export-section">
                  <h3>Detalles del Formato</h3>
                  <div className="format-details">
                    <div className="detail-item">
                      <strong>Formato:</strong> {selectedFormatInfo.name}
                    </div>
                    <div className="detail-item">
                      <strong>Extensión:</strong> .{selectedFormatInfo.file_extension}
                    </div>
                    <div className="detail-item">
                      <strong>Categoría:</strong> {formatCategories[selectedFormatInfo.category]?.label}
                    </div>
                    <div className="detail-item">
                      <strong>Descripción:</strong> {selectedFormatInfo.description}
                    </div>
                  </div>
                </div>
              )}

              {/* Export Options */}
              <div className="export-section">
                <h3>Opciones de Exportación</h3>
                <div className="export-options">
                  <label className="option-item">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeCharts}
                      onChange={() => handleOptionChange('includeCharts')}
                      disabled={!selectedFormatInfo?.supports_charts}
                    />
                    <span className="option-label">Incluir gráficos</span>
                    <span className="option-description">Agregar visualizaciones de datos</span>
                  </label>

                  <label className="option-item">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeImages}
                      onChange={() => handleOptionChange('includeImages')}
                      disabled={!selectedFormatInfo?.supports_images}
                    />
                    <span className="option-label">Incluir imágenes</span>
                    <span className="option-description">Agregar capturas y diagramas</span>
                  </label>

                  <label className="option-item">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeRawData}
                      onChange={() => handleOptionChange('includeRawData')}
                    />
                    <span className="option-label">Incluir datos sin procesar</span>
                    <span className="option-description">Datos técnicos completos</span>
                  </label>

                  <label className="option-item">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeRecommendations}
                      onChange={() => handleOptionChange('includeRecommendations')}
                    />
                    <span className="option-label">Incluir recomendaciones</span>
                    <span className="option-description">Sugerencias de mejora</span>
                  </label>

                  <label className="option-item">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeSchema}
                      onChange={() => handleOptionChange('includeSchema')}
                    />
                    <span className="option-label">Incluir información de esquema</span>
                    <span className="option-description">Estructura de base de datos</span>
                  </label>
                </div>

                {/* Compression Level */}
                {selectedFormatInfo?.category === 'archive' && (
                  <div className="compression-options">
                    <h4>Nivel de Compresión</h4>
                    <div className="compression-selector">
                      <label>
                        <input
                          type="radio"
                          name="compression"
                          value="low"
                          checked={exportOptions.compressionLevel === 'low'}
                          onChange={(e) => setExportOptions(prev => ({
                            ...prev,
                            compressionLevel: e.target.value
                          }))}
                        />
                        Bajo (rápido)
                      </label>
                      <label>
                        <input
                          type="radio"
                          name="compression"
                          value="medium"
                          checked={exportOptions.compressionLevel === 'medium'}
                          onChange={(e) => setExportOptions(prev => ({
                            ...prev,
                            compressionLevel: e.target.value
                          }))}
                        />
                        Medio (balanceado)
                      </label>
                      <label>
                        <input
                          type="radio"
                          name="compression"
                          value="high"
                          checked={exportOptions.compressionLevel === 'high'}
                          onChange={(e) => setExportOptions(prev => ({
                            ...prev,
                            compressionLevel: e.target.value
                          }))}
                        />
                        Alto (máxima compresión)
                      </label>
                    </div>
                  </div>
                )}
              </div>

              {/* Export Preview */}
              <div className="export-section">
                <h3>Vista Previa</h3>
                <div className="export-preview">
                  <div className="preview-info">
                    <Info size={16} />
                    <span>
                      Se exportará el análisis de "{currentAnalysis.filename}" 
                      en formato {selectedFormatInfo?.name} 
                      ({Math.round((currentAnalysis.file_size || 0) / 1024)}KB)
                    </span>
                  </div>
                  
                  <div className="preview-stats">
                    <div className="stat">
                      <strong>Errores:</strong> {currentAnalysis.summary?.total_errors || 0}
                    </div>
                    <div className="stat">
                      <strong>Rendimiento:</strong> {currentAnalysis.summary?.performance_score || 100}%
                    </div>
                    <div className="stat">
                      <strong>Seguridad:</strong> {currentAnalysis.summary?.security_score || 100}%
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="modal-footer">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Cancelar
          </button>
          <button 
            type="button" 
            className="btn-primary"
            onClick={handleExport}
            disabled={!currentAnalysis || isLoading}
          >
            <Download size={16} />
            {isLoading ? 'Exportando...' : 'Exportar'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExportModal;
