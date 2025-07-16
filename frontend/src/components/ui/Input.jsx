import React, { forwardRef } from 'react';
import { AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react';

/**
 * GitHub-authentic Input component
 * Supports validation states, icons, and various input types
 */
const Input = forwardRef(({
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  onBlur,
  onFocus,
  disabled = false,
  required = false,
  error,
  success,
  helperText,
  icon,
  iconPosition = 'left',
  size = 'medium',
  fullWidth = false,
  className = '',
  ...props
}, ref) => {
  const [showPassword, setShowPassword] = React.useState(false);
  const [focused, setFocused] = React.useState(false);

  const inputId = React.useId();
  const isPassword = type === 'password';
  const actualType = isPassword && showPassword ? 'text' : type;

  const containerClasses = [
    'form-group',
    fullWidth && 'form-group-full-width',
    className
  ].filter(Boolean).join(' ');

  const inputClasses = [
    'form-input',
    `form-input-${size}`,
    error && 'error',
    success && 'success',
    disabled && 'disabled',
    focused && 'focused',
    icon && `form-input-with-icon-${iconPosition}`
  ].filter(Boolean).join(' ');

  const handleFocus = (e) => {
    setFocused(true);
    onFocus?.(e);
  };

  const handleBlur = (e) => {
    setFocused(false);
    onBlur?.(e);
  };

  const renderIcon = () => {
    if (error) {
      return <AlertCircle size={16} className="input-icon input-icon-error" />;
    }
    if (success) {
      return <CheckCircle size={16} className="input-icon input-icon-success" />;
    }
    if (icon) {
      const IconComponent = icon;
      return <IconComponent size={16} className="input-icon" />;
    }
    return null;
  };

  const renderPasswordToggle = () => {
    if (!isPassword) return null;
    
    return (
      <button
        type="button"
        className="password-toggle"
        onClick={() => setShowPassword(!showPassword)}
        tabIndex={-1}
      >
        {showPassword ? (
          <EyeOff size={16} className="password-toggle-icon" />
        ) : (
          <Eye size={16} className="password-toggle-icon" />
        )}
      </button>
    );
  };

  return (
    <div className={containerClasses}>
      {label && (
        <label htmlFor={inputId} className={`form-label ${required ? 'required' : ''}`}>
          {label}
        </label>
      )}
      
      <div className="input-wrapper">
        {iconPosition === 'left' && renderIcon()}
        
        <input
          ref={ref}
          id={inputId}
          type={actualType}
          className={inputClasses}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          disabled={disabled}
          required={required}
          {...props}
        />
        
        {iconPosition === 'right' && renderIcon()}
        {renderPasswordToggle()}
      </div>
      
      {(error || success || helperText) && (
        <div className="input-feedback">
          {error && (
            <div className="form-error">
              <AlertCircle size={12} />
              <span>{error}</span>
            </div>
          )}
          {success && (
            <div className="form-success">
              <CheckCircle size={12} />
              <span>{success}</span>
            </div>
          )}
          {helperText && !error && !success && (
            <div className="form-help">
              {helperText}
            </div>
          )}
        </div>
      )}
    </div>
  );
});

Input.displayName = 'Input';

// Input variants
Input.Text = (props) => <Input type="text" {...props} />;
Input.Email = (props) => <Input type="email" {...props} />;
Input.Password = (props) => <Input type="password" {...props} />;
Input.Number = (props) => <Input type="number" {...props} />;
Input.Search = (props) => <Input type="search" {...props} />;
Input.Tel = (props) => <Input type="tel" {...props} />;
Input.Url = (props) => <Input type="url" {...props} />;

export default Input;
