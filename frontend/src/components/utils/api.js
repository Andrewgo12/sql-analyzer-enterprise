/**
 * SQL Analyzer Enterprise - API Utilities
 * Comprehensive API communication layer
 */

const API_BASE_URL = 'http://localhost:5000';

// API request wrapper with error handling
const apiRequest = async (endpoint, options = {}) => {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return await response.text();
  } catch (error) {
    console.error(`API Error for ${endpoint}:`, error);
    throw error;
  }
};

// Health check
export const checkHealth = async () => {
  return await apiRequest('/api/health');
};

// System metrics
export const getSystemMetrics = async () => {
  return await apiRequest('/api/metrics');
};

// Dashboard metrics
export const getDashboardMetrics = async () => {
  return await apiRequest('/api/metrics/dashboard');
};

// Database engines
export const getSupportedDatabases = async () => {
  return await apiRequest('/api/databases/supported');
};

// SQL Analysis
export const analyzeSQL = async (file, databaseEngine = 'mysql') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('database_engine', databaseEngine);

  return await apiRequest('/api/analyze', {
    method: 'POST',
    body: formData,
    headers: {} // Remove Content-Type to let browser set it for FormData
  });
};

// Export formats
export const getExportFormats = async () => {
  return await apiRequest('/api/export/formats');
};

// Export data
export const exportData = async (format, data) => {
  return await apiRequest(`/api/export/${format}`, {
    method: 'POST',
    body: JSON.stringify(data)
  });
};

// Connection testing
export const testConnection = async (connectionData) => {
  return await apiRequest('/api/connections/test', {
    method: 'POST',
    body: JSON.stringify(connectionData)
  });
};

// File operations
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  return await apiRequest('/api/files/upload', {
    method: 'POST',
    body: formData,
    headers: {}
  });
};

export const deleteFile = async (fileId) => {
  return await apiRequest(`/api/files/${fileId}`, {
    method: 'DELETE'
  });
};

// Terminal commands
export const executeCommand = async (command) => {
  return await apiRequest('/api/terminal/execute', {
    method: 'POST',
    body: JSON.stringify({ command })
  });
};

// Analysis history
export const getAnalysisHistory = async () => {
  return await apiRequest('/api/analysis/history');
};

export const deleteAnalysis = async (analysisId) => {
  return await apiRequest(`/api/analysis/${analysisId}`, {
    method: 'DELETE'
  });
};

// WebSocket connection for real-time updates
export const createWebSocketConnection = (onMessage, onError) => {
  const ws = new WebSocket('ws://localhost:5000/ws');
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('WebSocket message parse error:', error);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
  
  return ws;
};

// Utility functions
export const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

export const formatDuration = (seconds) => {
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  }
};

export const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleString();
};

// Error handling utilities
export const handleApiError = (error, defaultMessage = 'An error occurred') => {
  if (error.message) {
    return error.message;
  }
  return defaultMessage;
};

// Cache utilities
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export const getCachedData = (key) => {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  return null;
};

export const setCachedData = (key, data) => {
  cache.set(key, {
    data,
    timestamp: Date.now()
  });
};

export const clearCache = () => {
  cache.clear();
};

// Default export with all functions
export default {
  checkHealth,
  getSystemMetrics,
  getDashboardMetrics,
  getSupportedDatabases,
  analyzeSQL,
  getExportFormats,
  exportData,
  testConnection,
  uploadFile,
  deleteFile,
  executeCommand,
  getAnalysisHistory,
  deleteAnalysis,
  createWebSocketConnection,
  formatBytes,
  formatDuration,
  formatTimestamp,
  handleApiError,
  getCachedData,
  setCachedData,
  clearCache
};
