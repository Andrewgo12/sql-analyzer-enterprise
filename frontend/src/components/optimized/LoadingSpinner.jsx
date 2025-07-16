import React, { memo } from 'react';
import { Loader, Database, Code, Activity } from 'lucide-react';

const LoadingSpinner = memo(({ 
  size = 'medium', 
  message = 'Cargando...', 
  type = 'default',
  fullScreen = false 
}) => {
  const getSizeClass = () => {
    switch (size) {
      case 'small': return 'spinner-small';
      case 'large': return 'spinner-large';
      default: return 'spinner-medium';
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'analysis':
        return <Code className="spinner-icon animate-spin" />;
      case 'database':
        return <Database className="spinner-icon animate-pulse" />;
      case 'metrics':
        return <Activity className="spinner-icon animate-bounce" />;
      default:
        return <Loader className="spinner-icon animate-spin" />;
    }
  };

  const spinnerContent = (
    <div className={`loading-spinner ${getSizeClass()}`}>
      <div className="spinner-container">
        {getIcon()}
        {message && (
          <div className="spinner-message">
            {message}
          </div>
        )}
      </div>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="loading-overlay">
        {spinnerContent}
      </div>
    );
  }

  return spinnerContent;
});

LoadingSpinner.displayName = 'LoadingSpinner';

export default LoadingSpinner;
