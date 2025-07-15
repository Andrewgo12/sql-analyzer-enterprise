import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  Info, 
  X,
  Bell
} from 'lucide-react';

const NotificationSystem = () => {
  const [notifications, setNotifications] = useState([]);
  const [isVisible, setIsVisible] = useState(true);

  // Auto-remove notifications after 5 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setNotifications(prev => 
        prev.filter(notification => 
          Date.now() - notification.timestamp < 5000
        )
      );
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const addNotification = (type, title, message, duration = 5000) => {
    const notification = {
      id: Date.now() + Math.random(),
      type,
      title,
      message,
      timestamp: Date.now(),
      duration
    };

    setNotifications(prev => [...prev, notification]);

    // Auto-remove after duration
    setTimeout(() => {
      removeNotification(notification.id);
    }, duration);
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle size={20} />;
      case 'warning':
        return <AlertTriangle size={20} />;
      case 'error':
        return <XCircle size={20} />;
      case 'info':
      default:
        return <Info size={20} />;
    }
  };

  const getNotificationClass = (type) => {
    return `notification notification-${type}`;
  };

  // Global notification function
  window.showNotification = addNotification;

  if (!isVisible || notifications.length === 0) {
    return null;
  }

  return (
    <div className="notification-container">
      {notifications.map(notification => (
        <div
          key={notification.id}
          className={getNotificationClass(notification.type)}
        >
          <div className="notification-icon">
            {getNotificationIcon(notification.type)}
          </div>
          
          <div className="notification-content">
            <div className="notification-title">
              {notification.title}
            </div>
            {notification.message && (
              <div className="notification-message">
                {notification.message}
              </div>
            )}
          </div>

          <button
            className="notification-close"
            onClick={() => removeNotification(notification.id)}
          >
            <X size={16} />
          </button>

          <div 
            className="notification-progress"
            style={{
              animationDuration: `${notification.duration}ms`
            }}
          />
        </div>
      ))}
    </div>
  );
};

// Utility functions for easy notification usage
export const notify = {
  success: (title, message) => window.showNotification?.('success', title, message),
  warning: (title, message) => window.showNotification?.('warning', title, message),
  error: (title, message) => window.showNotification?.('error', title, message),
  info: (title, message) => window.showNotification?.('info', title, message)
};

export default NotificationSystem;
