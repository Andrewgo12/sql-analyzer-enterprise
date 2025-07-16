import React, { useState, useEffect } from 'react';
import {
  Download,
  FileText,
  Settings,
  X,
  File,
  Archive,
  Image,
  Database,
  Code,
  CheckCircle,
  AlertCircle,
  Info,
  Loader2
} from 'lucide-react';
import { Modal, Button, Input, Dropdown, Card } from '../ui';

const ExportModal = ({ isOpen, onClose, onExport, analysisData = null, analysisId = null }) => {
  const [exportOptions, setExportOptions] = useState({
    format: 'json',
    includeMetadata: true,
    includeComments: true,
    includeStatistics: true,
    includeErrors: true,
    includeSuggestions: true,
    compression: false,
    filename: '',
    quality: 'high',
    template: 'standard'
  });

  const [exporting, setExporting] = useState(false);
  const [errors, setErrors] = useState({});

  const formats = [
    {
      value: 'json',
      label: 'JSON',
      description: 'Formato estructurado para APIs y desarrollo',
      icon: Code,
      size: 'Pequeño',
      compatibility: 'Excelente'
    },
    {
      value: 'html',
      label: 'HTML',
      description: 'Reporte visual navegable con gráficos',
      icon: FileText,
      size: 'Mediano',
      compatibility: 'Universal'
    },
    {
      value: 'pdf',
      label: 'PDF',
      description: 'Documento profesional imprimible',
      icon: File,
      size: 'Grande',
      compatibility: 'Universal'
    },
    {
      value: 'csv',
      label: 'CSV',
      description: 'Datos tabulares para Excel y análisis',
      icon: Database,
      size: 'Pequeño',
      compatibility: 'Excelente'
    },
    {
      value: 'xml',
      label: 'XML',
      description: 'Formato estructurado estándar',
      icon: Code,
      size: 'Mediano',
      compatibility: 'Buena'
    },
    {
      value: 'markdown',
      label: 'Markdown',
      description: 'Documentación técnica legible',
      icon: FileText,
      size: 'Pequeño',
      compatibility: 'Buena'
    },
    {
      value: 'excel',
      label: 'Excel',
      description: 'Hoja de cálculo con múltiples pestañas',
      icon: Database,
      size: 'Grande',
      compatibility: 'Buena'
    },
    {
      value: 'word',
      label: 'Word',
      description: 'Documento de texto enriquecido',
      icon: FileText,
      size: 'Grande',
      compatibility: 'Buena'
    }
  ];

  const qualityOptions = [
    { value: 'basic', label: 'Básica - Solo resultados principales' },
    { value: 'standard', label: 'Estándar - Análisis completo' },
    { value: 'detailed', label: 'Detallada - Incluye todo el contexto' },
    { value: 'comprehensive', label: 'Exhaustiva - Máximo detalle posible' }
  ];

  const templateOptions = [
    { value: 'standard', label: 'Estándar - Formato clásico' },
    { value: 'executive', label: 'Ejecutivo - Resumen para directivos' },
    { value: 'technical', label: 'Técnico - Para desarrolladores' },
    { value: 'audit', label: 'Auditoría - Cumplimiento y seguridad' }
  ];

  // Generate default filename based on analysis data
  useEffect(() => {
    if (analysisData && !exportOptions.filename) {
      const timestamp = new Date().toISOString().slice(0, 10);
      const defaultName = `sql_analysis_${timestamp}`;
      setExportOptions(prev => ({
        ...prev,
        filename: defaultName
      }));
    }
  }, [analysisData]);

  const validateForm = () => {
    const newErrors = {};

    if (!exportOptions.filename.trim()) {
      newErrors.filename = 'El nombre del archivo es requerido';
    }

    // Validate filename characters
    const invalidChars = /[<>:"/\\|?*]/;
    if (invalidChars.test(exportOptions.filename)) {
      newErrors.filename = 'El nombre contiene caracteres no válidos';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleOptionChange = (key, value) => {
    setExportOptions(prev => ({
      ...prev,
      [key]: value
    }));

    // Clear specific error when user makes changes
    if (errors[key]) {
      setErrors(prev => ({
        ...prev,
        [key]: undefined
      }));
    }
  };

  const handleExport = async () => {
    if (!validateForm()) {
      return;
    }

    setExporting(true);

    try {
      const exportData = {
        ...exportOptions,
        analysisId,
        data: analysisData,
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      };

      await onExport?.(exportData);
      onClose?.();
    } catch (error) {
      console.error('Export failed:', error);
      setErrors({ general: 'Error al exportar el análisis' });
    } finally {
      setExporting(false);
    }
  };

  const getSelectedFormat = () => {
    return formats.find(f => f.value === exportOptions.format);
  };

  const getEstimatedSize = () => {
    if (!analysisData) return 'N/A';
    
    const baseSize = JSON.stringify(analysisData).length;
    const format = getSelectedFormat();
    
    let multiplier = 1;
    switch (format?.value) {
      case 'html':
        multiplier = 3;
        break;
      case 'pdf':
        multiplier = 5;
        break;
      case 'excel':
      case 'word':
        multiplier = 4;
        break;
      case 'xml':
        multiplier = 2;
        break;
      default:
        multiplier = 1;
    }

    const estimatedBytes = baseSize * multiplier;
    
    if (estimatedBytes < 1024) return `${estimatedBytes} B`;
    if (estimatedBytes < 1024 * 1024) return `${(estimatedBytes / 1024).toFixed(1)} KB`;
    return `${(estimatedBytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const selectedFormat = getSelectedFormat();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={
        <div className="modal-title-with-icon">
          <Download size={20} />
          Exportar Análisis SQL
        </div>
      }
      size="large"
      className="export-modal"
    >
      <div className="export-form">
        {errors.general && (
          <div className="form-error-banner">
            <AlertCircle size={16} />
            {errors.general}
          </div>
        )}

        <div className="form-section">
          <h3 className="form-section-title">Formato de Exportación</h3>
          
          <div className="format-grid">
            {formats.map(format => (
              <label key={format.value} className={`format-card ${exportOptions.format === format.value ? 'selected' : ''}`}>
                <input
                  type="radio"
                  name="format"
                  value={format.value}
                  checked={exportOptions.format === format.value}
                  onChange={(e) => handleOptionChange('format', e.target.value)}
                  className="format-radio"
                />
                <div className="format-content">
                  <div className="format-header">
                    <format.icon size={20} className="format-icon" />
                    <span className="format-name">{format.label}</span>
                  </div>
                  <p className="format-description">{format.description}</p>
                  <div className="format-meta">
                    <span className="format-size">Tamaño: {format.size}</span>
                    <span className="format-compatibility">Compatibilidad: {format.compatibility}</span>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className="form-section">
          <h3 className="form-section-title">Configuración del Archivo</h3>
          
          <div className="form-grid">
            <Input
              label="Nombre del archivo"
              value={exportOptions.filename}
              onChange={(e) => handleOptionChange('filename', e.target.value)}
              placeholder="sql_analysis_2024"
              error={errors.filename}
              required
              fullWidth
              helperText="No incluyas la extensión del archivo"
            />

            <Dropdown
              label="Calidad del reporte"
              options={qualityOptions}
              value={exportOptions.quality}
              onChange={(value) => handleOptionChange('quality', value)}
              fullWidth
            />

            <Dropdown
              label="Plantilla"
              options={templateOptions}
              value={exportOptions.template}
              onChange={(value) => handleOptionChange('template', value)}
              fullWidth
            />
          </div>
        </div>

        <div className="form-section">
          <h3 className="form-section-title">Contenido a Incluir</h3>
          
          <div className="checkbox-grid">
            <label className="export-checkbox">
              <input
                type="checkbox"
                checked={exportOptions.includeMetadata}
                onChange={(e) => handleOptionChange('includeMetadata', e.target.checked)}
              />
              <span>Metadatos del análisis</span>
              <p className="checkbox-description">Información sobre fecha, versión y configuración</p>
            </label>

            <label className="export-checkbox">
              <input
                type="checkbox"
                checked={exportOptions.includeComments}
                onChange={(e) => handleOptionChange('includeComments', e.target.checked)}
              />
              <span>Comentarios explicativos</span>
              <p className="checkbox-description">Explicaciones detalladas de cada hallazgo</p>
            </label>

            <label className="export-checkbox">
              <input
                type="checkbox"
                checked={exportOptions.includeStatistics}
                onChange={(e) => handleOptionChange('includeStatistics', e.target.checked)}
              />
              <span>Estadísticas de análisis</span>
              <p className="checkbox-description">Métricas y resúmenes numéricos</p>
            </label>
          </div>
        </div>

        {analysisData && (
          <Card className="export-preview">
            <Card.Header>
              <Card.Title size="small">Vista Previa del Contenido</Card.Title>
            </Card.Header>
            <Card.Body>
              <div className="preview-stats">
                <div className="preview-stat">
                  <span className="stat-label">Consultas analizadas:</span>
                  <span className="stat-value">{analysisData.queries?.length || 0}</span>
                </div>
                <div className="preview-stat">
                  <span className="stat-label">Errores encontrados:</span>
                  <span className="stat-value error">{analysisData.errors?.length || 0}</span>
                </div>
                <div className="preview-stat">
                  <span className="stat-label">Sugerencias:</span>
                  <span className="stat-value success">{analysisData.suggestions?.length || 0}</span>
                </div>
                <div className="preview-stat">
                  <span className="stat-label">Tamaño estimado:</span>
                  <span className="stat-value">{getEstimatedSize()}</span>
                </div>
              </div>
              
              {selectedFormat && (
                <div className="format-info-selected">
                  <selectedFormat.icon size={16} />
                  <span>Exportando como {selectedFormat.label}</span>
                  <span className="format-extension">.{selectedFormat.value}</span>
                </div>
              )}
            </Card.Body>
          </Card>
        )}
      </div>

      <Modal.Footer>
        <Button variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <Button
          variant="primary"
          onClick={handleExport}
          loading={exporting}
          disabled={!exportOptions.filename.trim() || !analysisData}
          icon={exporting ? Loader2 : Download}
        >
          {exporting ? 'Exportando...' : 'Exportar Análisis'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ExportModal;
