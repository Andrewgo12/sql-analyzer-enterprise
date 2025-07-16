import React from 'react';

/**
 * GitHub-authentic Card component
 * Flexible card container with header, body, and footer sections
 */
const Card = ({
  children,
  className = '',
  hover = false,
  padding = 'default',
  ...props
}) => {
  const cardClasses = [
    'card',
    hover && 'card-hover',
    `card-padding-${padding}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={cardClasses} {...props}>
      {children}
    </div>
  );
};

/**
 * Card Header component
 */
const CardHeader = ({
  children,
  className = '',
  actions,
  ...props
}) => {
  return (
    <div className={`card-header ${className}`} {...props}>
      <div className="card-header-content">
        {children}
      </div>
      {actions && (
        <div className="card-header-actions">
          {actions}
        </div>
      )}
    </div>
  );
};

/**
 * Card Title component
 */
const CardTitle = ({
  children,
  className = '',
  size = 'default',
  ...props
}) => {
  const titleClasses = [
    'card-title',
    `card-title-${size}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <h3 className={titleClasses} {...props}>
      {children}
    </h3>
  );
};

/**
 * Card Description component
 */
const CardDescription = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <p className={`card-description ${className}`} {...props}>
      {children}
    </p>
  );
};

/**
 * Card Body component
 */
const CardBody = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <div className={`card-body ${className}`} {...props}>
      {children}
    </div>
  );
};

/**
 * Card Footer component
 */
const CardFooter = ({
  children,
  className = '',
  align = 'right',
  ...props
}) => {
  const footerClasses = [
    'card-footer',
    `card-footer-${align}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={footerClasses} {...props}>
      {children}
    </div>
  );
};

/**
 * Card Stats component for metrics display
 */
const CardStats = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon,
  className = '',
  ...props
}) => {
  const statsClasses = [
    'card-stats',
    className
  ].filter(Boolean).join(' ');

  const changeClasses = [
    'card-stats-change',
    `card-stats-change-${changeType}`
  ].filter(Boolean).join(' ');

  return (
    <div className={statsClasses} {...props}>
      <div className="card-stats-header">
        <span className="card-stats-title">{title}</span>
        {icon && (
          <div className="card-stats-icon">
            {React.isValidElement(icon) ? icon : React.createElement(icon, { size: 16 })}
          </div>
        )}
      </div>
      
      <div className="card-stats-value">
        {value}
      </div>
      
      {change && (
        <div className={changeClasses}>
          {change}
        </div>
      )}
    </div>
  );
};

/**
 * Card List component for displaying lists within cards
 */
const CardList = ({
  children,
  className = '',
  divided = true,
  ...props
}) => {
  const listClasses = [
    'card-list',
    divided && 'card-list-divided',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={listClasses} {...props}>
      {children}
    </div>
  );
};

/**
 * Card List Item component
 */
const CardListItem = ({
  children,
  className = '',
  onClick,
  ...props
}) => {
  const itemClasses = [
    'card-list-item',
    onClick && 'card-list-item-clickable',
    className
  ].filter(Boolean).join(' ');

  const Component = onClick ? 'button' : 'div';

  return (
    <Component className={itemClasses} onClick={onClick} {...props}>
      {children}
    </Component>
  );
};

// Attach sub-components to main Card component
Card.Header = CardHeader;
Card.Title = CardTitle;
Card.Description = CardDescription;
Card.Body = CardBody;
Card.Footer = CardFooter;
Card.Stats = CardStats;
Card.List = CardList;
Card.ListItem = CardListItem;

export default Card;
