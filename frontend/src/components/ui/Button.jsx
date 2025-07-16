import React from 'react';
import { Loader2 } from 'lucide-react';

/**
 * GitHub-authentic Button component
 * Supports multiple variants, sizes, and states
 */
const Button = ({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  onClick,
  type = 'button',
  className = '',
  ...props
}) => {
  const baseClasses = [
    'btn',
    `btn-${variant}`,
    `btn-${size}`,
    disabled && 'btn-disabled',
    loading && 'btn-loading',
    fullWidth && 'btn-full-width',
    className
  ].filter(Boolean).join(' ');

  const handleClick = (e) => {
    if (disabled || loading) {
      e.preventDefault();
      return;
    }
    onClick?.(e);
  };

  const renderIcon = () => {
    if (loading) {
      return <Loader2 size={16} className="btn-icon animate-spin" />;
    }
    if (icon) {
      const IconComponent = icon;
      return <IconComponent size={16} className="btn-icon" />;
    }
    return null;
  };

  return (
    <button
      type={type}
      className={baseClasses}
      disabled={disabled || loading}
      onClick={handleClick}
      {...props}
    >
      {iconPosition === 'left' && renderIcon()}
      {children && <span className="btn-text">{children}</span>}
      {iconPosition === 'right' && renderIcon()}
    </button>
  );
};

// Button variants
Button.Primary = (props) => <Button variant="primary" {...props} />;
Button.Secondary = (props) => <Button variant="secondary" {...props} />;
Button.Outline = (props) => <Button variant="outline" {...props} />;
Button.Ghost = (props) => <Button variant="ghost" {...props} />;
Button.Danger = (props) => <Button variant="danger" {...props} />;
Button.Success = (props) => <Button variant="success" {...props} />;

// Button sizes
Button.Small = (props) => <Button size="small" {...props} />;
Button.Medium = (props) => <Button size="medium" {...props} />;
Button.Large = (props) => <Button size="large" {...props} />;

export default Button;
