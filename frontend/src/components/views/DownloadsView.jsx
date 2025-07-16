import React, { useState, useEffect } from 'react';
import {
  Download,
  FileText,
  Trash2,
  Eye,
  FolderOpen,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  Search,
  Filter,
  MoreVertical,
  ExternalLink
} from 'lucide-react';
import { Card, Button, Input, Dropdown } from '../ui';

const DownloadsView = () => {
  const [downloads, setDownloads] = useState([]);
  const [filteredDownloads, setFilteredDownloads] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');

  const filterOptions = [
    { value: 'all', label: 'Todos los archivos' },
    { value: 'json', label: 'JSON' },
    { value: 'csv', label: 'CSV' },
    { value: 'html', label: 'HTML' },
    { value: 'pdf', label: 'PDF' },
    { value: 'xml', label: 'XML' }
  ];

  const sortOptions = [
    { value: 'date', label: 'Fecha' },
    { value: 'name', label: 'Nombre' },
    { value: 'size', label: 'Tamaño' },
    { value: 'type', label: 'Tipo' }
  ];

  // Load downloads from localStorage
  useEffect(() => {
    const savedDownloads = localStorage.getItem('sql_analyzer_downloads');
    if (savedDownloads) {
      try {
        const parsedDownloads = JSON.parse(savedDownloads);
        setDownloads(parsedDownloads);
      } catch (error) {
        console.error('Error loading downloads:', error);
      }
    } else {
      // Mock data for demonstration
      const mockDownloads = [
        {
          id: 1,
          name: 'analysis_report_2024.json',
          type: 'json',
          size: 15420,
          date: new Date('2024-01-15T10:30:00'),
          status: 'completed',
          url: '#',
          description: 'Análisis completo de consultas SQL'
        },
        {
          id: 2,
          name: 'database_schema.html',
          type: 'html',
          size: 8750,
          date: new Date('2024-01-14T15:45:00'),
          status: 'completed',
          url: '#',
          description: 'Documentación del esquema de base de datos'
        },
        {
          id: 3,
          name: 'performance_metrics.csv',
          type: 'csv',
          size: 3200,
          date: new Date('2024-01-13T09:15:00'),
          status: 'completed',
          url: '#',
          description: 'Métricas de rendimiento del sistema'
        },
        {
          id: 4,
          name: 'error_report.pdf',
          type: 'pdf',
          size: 25600,
          date: new Date('2024-01-12T14:20:00'),
          status: 'failed',
          url: '#',
          description: 'Reporte de errores encontrados'
        }
      ];
      setDownloads(mockDownloads);
      localStorage.setItem('sql_analyzer_downloads', JSON.stringify(mockDownloads));
    }
  }, []);

  // Filter and sort downloads
  useEffect(() => {
    let filtered = downloads;

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(download =>
        download.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        download.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(download => download.type === filterType);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'size':
          aValue = a.size;
          bValue = b.size;
          break;
        case 'type':
          aValue = a.type;
          bValue = b.type;
          break;
        default:
          aValue = new Date(a.date);
          bValue = new Date(b.date);
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredDownloads(filtered);
  }, [downloads, searchTerm, filterType, sortBy, sortOrder]);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getFileIcon = (type) => {
    switch (type) {
      case 'json':
      case 'xml':
        return <FileText size={20} className="file-icon json" />;
      case 'csv':
        return <FileText size={20} className="file-icon csv" />;
      case 'html':
        return <FileText size={20} className="file-icon html" />;
      case 'pdf':
        return <FileText size={20} className="file-icon pdf" />;
      default:
        return <FileText size={20} className="file-icon" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} className="status-icon success" />;
      case 'failed':
        return <AlertCircle size={16} className="status-icon error" />;
      case 'processing':
        return <Loader2 size={16} className="status-icon processing animate-spin" />;
      default:
        return null;
    }
  };

  const handleDownload = (download) => {
    // Simulate download
    const link = document.createElement('a');
    link.href = download.url;
    link.download = download.name;
    link.click();
  };

  const handleDelete = (downloadId) => {
    if (window.confirm('¿Eliminar este archivo de la lista de descargas?')) {
      const updatedDownloads = downloads.filter(d => d.id !== downloadId);
      setDownloads(updatedDownloads);
      localStorage.setItem('sql_analyzer_downloads', JSON.stringify(updatedDownloads));
    }
  };

  const handleClearAll = () => {
    if (window.confirm('¿Eliminar todos los archivos de la lista de descargas?')) {
      setDownloads([]);
      localStorage.removeItem('sql_analyzer_downloads');
    }
  };

  const totalSize = downloads.reduce((sum, download) => sum + download.size, 0);
  const completedDownloads = downloads.filter(d => d.status === 'completed').length;

  return (
    <div className="downloads-view">
      <div className="downloads-header">
        <h1 className="downloads-title">
          <Download size={24} className="title-icon" />
          Gestión de Descargas
        </h1>
        <div className="downloads-actions">
          <Button variant="outline" onClick={handleClearAll}>
            <Trash2 size={16} />
            Limpiar todo
          </Button>
        </div>
      </div>

      <div className="downloads-stats">
        <div className="stats-grid">
          <Card.Stats
            title="Total de archivos"
            value={downloads.length}
            icon={FileText}
          />
          <Card.Stats
            title="Completados"
            value={completedDownloads}
            icon={CheckCircle}
            changeType="success"
          />
          <Card.Stats
            title="Tamaño total"
            value={formatFileSize(totalSize)}
            icon={FolderOpen}
          />
        </div>
      </div>

      <div className="downloads-controls">
        <div className="search-filter-group">
          <Input
            placeholder="Buscar archivos..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            icon={Search}
            className="search-input"
          />
          
          <Dropdown
            options={filterOptions}
            value={filterType}
            onChange={setFilterType}
            placeholder="Filtrar por tipo"
          />
          
          <Dropdown
            options={sortOptions}
            value={sortBy}
            onChange={setSortBy}
            placeholder="Ordenar por"
          />
          
          <Button
            variant="outline"
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </Button>
        </div>
      </div>

      <div className="downloads-content">
        {filteredDownloads.length === 0 ? (
          <div className="downloads-empty">
            <Download size={64} />
            <h3>No hay descargas</h3>
            <p>
              {searchTerm || filterType !== 'all'
                ? 'No se encontraron archivos que coincidan con los filtros'
                : 'Aún no has descargado ningún archivo'
              }
            </p>
          </div>
        ) : (
          <div className="downloads-list">
            {filteredDownloads.map((download) => (
              <Card key={download.id} className="download-item" hover>
                <Card.Body>
                  <div className="download-info">
                    <div className="download-icon">
                      {getFileIcon(download.type)}
                    </div>
                    
                    <div className="download-details">
                      <div className="download-name">
                        {download.name}
                        {getStatusIcon(download.status)}
                      </div>
                      <div className="download-description">
                        {download.description}
                      </div>
                      <div className="download-meta">
                        <span className="download-size">
                          {formatFileSize(download.size)}
                        </span>
                        <span className="download-date">
                          <Clock size={12} />
                          {formatDate(download.date)}
                        </span>
                      </div>
                    </div>
                    
                    <div className="download-actions">
                      {download.status === 'completed' && (
                        <Button
                          variant="outline"
                          size="small"
                          onClick={() => handleDownload(download)}
                        >
                          <Download size={14} />
                          Descargar
                        </Button>
                      )}
                      
                      <Button
                        variant="ghost"
                        size="small"
                        onClick={() => handleDelete(download.id)}
                      >
                        <Trash2 size={14} />
                      </Button>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DownloadsView;
