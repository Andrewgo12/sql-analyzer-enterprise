import React, { useEffect, useRef } from 'react';
import { X, AlertTriangle, CheckCircle, Info, AlertCircle } from 'lucide-react';
import Button from './Button';

/**
 * GitHub-authentic Modal component
 * Supports different sizes and types
 */
const Modal = ({
  isOpen = false,
  onClose,
  title,
  children,
  size = 'medium',
  type = 'default',
  showCloseButton = true,
  closeOnBackdrop = true,
  closeOnEscape = true,
  className = '',
  ...props
}) => {
  const modalRef = useRef(null);
  const backdropRef = useRef(null);

  const modalClasses = [
    'modal',
    `modal-${size}`,
    `modal-${type}`,
    className
  ].filter(Boolean).join(' ');

  const backdropClasses = [
    'modal-backdrop',
    isOpen && 'open'
  ].filter(Boolean).join(' ');

  // Handle escape key
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose?.();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape, onClose]);

  // Handle focus trap
  useEffect(() => {
    if (!isOpen) return;

    const modal = modalRef.current;
    if (!modal) return;

    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTabKey = (e) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement?.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement?.focus();
          e.preventDefault();
        }
      }
    };

    document.addEventListener('keydown', handleTabKey);
    firstElement?.focus();

    return () => document.removeEventListener('keydown', handleTabKey);
  }, [isOpen]);

  // Handle backdrop click
  const handleBackdropClick = (e) => {
    if (closeOnBackdrop && e.target === backdropRef.current) {
      onClose?.();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      ref={backdropRef}
      className={backdropClasses}
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
    >
      <div ref={modalRef} className={modalClasses} {...props}>
        {(title || showCloseButton) && (
          <div className="modal-header">
            {title && (
              <h2 id="modal-title" className="modal-title">
                {title}
              </h2>
            )}
            {showCloseButton && (
              <button
                className="modal-close"
                onClick={onClose}
                aria-label="Close modal"
              >
                <X size={16} />
              </button>
            )}
          </div>
        )}

        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
};

/**
 * Modal Footer component
 */
const ModalFooter = ({
  children,
  className = '',
  align = 'right',
  ...props
}) => {
  const footerClasses = [
    'modal-footer',
    `modal-footer-${align}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={footerClasses} {...props}>
      {children}
    </div>
  );
};

/**
 * Confirmation Modal component
 */
const ConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  title = 'Confirm Action',
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  type = 'warning',
  loading = false,
  ...props
}) => {
  const getIcon = () => {
    switch (type) {
      case 'danger':
        return <AlertTriangle size={48} className="confirmation-icon" />;
      case 'success':
        return <CheckCircle size={48} className="confirmation-icon" />;
      case 'info':
        return <Info size={48} className="confirmation-icon" />;
      default:
        return <AlertCircle size={48} className="confirmation-icon" />;
    }
  };

  const getConfirmVariant = () => {
    switch (type) {
      case 'danger':
        return 'danger';
      case 'success':
        return 'success';
      default:
        return 'primary';
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="small"
      type="confirmation"
      {...props}
    >
      <div className="confirmation-content">
        {getIcon()}
        <div className="confirmation-message">
          {message}
        </div>
      </div>

      <ModalFooter>
        <Button
          variant="outline"
          onClick={onClose}
          disabled={loading}
        >
          {cancelText}
        </Button>
        <Button
          variant={getConfirmVariant()}
          onClick={onConfirm}
          loading={loading}
        >
          {confirmText}
        </Button>
      </ModalFooter>
    </Modal>
  );
};

/**
 * Alert Modal component
 */
const AlertModal = ({
  isOpen,
  onClose,
  title,
  message,
  type = 'info',
  buttonText = 'OK',
  ...props
}) => {
  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle size={24} className="alert-icon" />;
      case 'error':
        return <AlertCircle size={24} className="alert-icon" />;
      case 'warning':
        return <AlertTriangle size={24} className="alert-icon" />;
      default:
        return <Info size={24} className="alert-icon" />;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="small"
      type="alert"
      {...props}
    >
      <div className="alert-content">
        {getIcon()}
        <div className="alert-message">
          {message}
        </div>
      </div>

      <ModalFooter>
        <Button onClick={onClose}>
          {buttonText}
        </Button>
      </ModalFooter>
    </Modal>
  );
};

// Attach sub-components to main Modal component
Modal.Footer = ModalFooter;
Modal.Confirmation = ConfirmationModal;
Modal.Alert = AlertModal;

export default Modal;
