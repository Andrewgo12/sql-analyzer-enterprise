/**
 * SQL Analyzer Enterprise - Development Configuration
 * Configuration settings for development environment
 */

export const config = {
  // API Configuration
  API_BASE_URL: 'http://localhost:5000',
  WS_URL: 'ws://localhost:5000/ws',
  
  // Performance Settings
  MAX_FILE_SIZE: 100 * 1024 * 1024, // 100MB
  SUPPORTED_FORMATS: ['.sql', '.txt'],
  REFRESH_INTERVAL: 5000, // 5 seconds
  CACHE_DURATION: 300000, // 5 minutes
  
  // Feature Flags
  FEATURES: {
    REAL_TIME_METRICS: true,
    EXPORT_SYSTEM: true,
    TERMINAL: true,
    BATCH_PROCESSING: true,
    WEBSOCKET_SUPPORT: true,
    ADVANCED_ANALYTICS: true,
    FILE_MANAGER: true,
    CONNECTION_MANAGER: true
  },
  
  // UI Configuration
  UI: {
    THEME: 'light',
    SIDEBAR_COLLAPSED: false,
    SHOW_ANIMATIONS: true,
    TRANSITION_DURATION: 200,
    AUTO_REFRESH: true
  },
  
  // Development Settings
  DEBUG: true,
  LOG_LEVEL: 'debug',
  MOCK_DATA: false,
  
  // Error Handling
  ERROR_RETRY_ATTEMPTS: 3,
  ERROR_RETRY_DELAY: 1000,
  
  // Export Formats
  EXPORT_FORMATS: [
    'json', 'html', 'pdf', 'csv', 'xlsx', 
    'xml', 'txt', 'md', 'sql', 'zip'
  ],
  
  // Database Engines
  DEFAULT_DATABASE_ENGINE: 'mysql',
  
  // Terminal Configuration
  TERMINAL: {
    MAX_HISTORY: 1000,
    DEFAULT_THEME: 'dark',
    FONT_SIZE: 14,
    AUTO_SCROLL: true,
    SHOW_TIMESTAMPS: true
  }
};

export default config;
