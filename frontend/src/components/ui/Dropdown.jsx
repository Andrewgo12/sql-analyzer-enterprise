import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check } from 'lucide-react';

/**
 * GitHub-authentic Dropdown component
 * Supports single and multi-select, search, and custom rendering
 */
const Dropdown = ({
  options = [],
  value,
  onChange,
  placeholder = 'Select option...',
  disabled = false,
  searchable = false,
  multiple = false,
  clearable = false,
  size = 'medium',
  className = '',
  renderOption,
  renderValue,
  ...props
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [focusedIndex, setFocusedIndex] = useState(-1);
  
  const dropdownRef = useRef(null);
  const searchInputRef = useRef(null);
  const listRef = useRef(null);

  const dropdownClasses = [
    'dropdown',
    `dropdown-${size}`,
    disabled && 'dropdown-disabled',
    isOpen && 'dropdown-open',
    className
  ].filter(Boolean).join(' ');

  // Filter options based on search term
  const filteredOptions = searchable && searchTerm
    ? options.filter(option => 
        option.label?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        option.value?.toString().toLowerCase().includes(searchTerm.toLowerCase())
      )
    : options;

  // Get selected options
  const selectedOptions = multiple
    ? options.filter(option => value?.includes(option.value))
    : options.find(option => option.value === value);

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setSearchTerm('');
        setFocusedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setFocusedIndex(prev => 
            prev < filteredOptions.length - 1 ? prev + 1 : 0
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setFocusedIndex(prev => 
            prev > 0 ? prev - 1 : filteredOptions.length - 1
          );
          break;
        case 'Enter':
          e.preventDefault();
          if (focusedIndex >= 0) {
            handleOptionSelect(filteredOptions[focusedIndex]);
          }
          break;
        case 'Escape':
          setIsOpen(false);
          setSearchTerm('');
          setFocusedIndex(-1);
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, focusedIndex, filteredOptions]);

  // Focus search input when dropdown opens
  useEffect(() => {
    if (isOpen && searchable && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen, searchable]);

  const handleToggle = () => {
    if (disabled) return;
    setIsOpen(!isOpen);
    setSearchTerm('');
    setFocusedIndex(-1);
  };

  const handleOptionSelect = (option) => {
    if (multiple) {
      const newValue = value?.includes(option.value)
        ? value.filter(v => v !== option.value)
        : [...(value || []), option.value];
      onChange?.(newValue);
    } else {
      onChange?.(option.value);
      setIsOpen(false);
    }
    setSearchTerm('');
    setFocusedIndex(-1);
  };

  const handleClear = (e) => {
    e.stopPropagation();
    onChange?.(multiple ? [] : null);
  };

  const renderSelectedValue = () => {
    if (multiple) {
      if (!selectedOptions?.length) return placeholder;
      if (selectedOptions.length === 1) {
        return renderValue ? renderValue(selectedOptions[0]) : selectedOptions[0].label;
      }
      return `${selectedOptions.length} selected`;
    } else {
      if (!selectedOptions) return placeholder;
      return renderValue ? renderValue(selectedOptions) : selectedOptions.label;
    }
  };

  const isSelected = (option) => {
    return multiple
      ? value?.includes(option.value)
      : value === option.value;
  };

  return (
    <div ref={dropdownRef} className={dropdownClasses} {...props}>
      <button
        type="button"
        className="dropdown-trigger"
        onClick={handleToggle}
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span className="dropdown-value">
          {renderSelectedValue()}
        </span>
        
        <div className="dropdown-actions">
          {clearable && (value || (multiple && value?.length > 0)) && (
            <button
              type="button"
              className="dropdown-clear"
              onClick={handleClear}
              aria-label="Clear selection"
            >
              ×
            </button>
          )}
          <ChevronDown 
            size={16} 
            className={`dropdown-arrow ${isOpen ? 'dropdown-arrow-open' : ''}`}
          />
        </div>
      </button>

      {isOpen && (
        <div className="dropdown-menu">
          {searchable && (
            <div className="dropdown-search">
              <input
                ref={searchInputRef}
                type="text"
                className="dropdown-search-input"
                placeholder="Search options..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          )}

          <ul ref={listRef} className="dropdown-list" role="listbox">
            {filteredOptions.length === 0 ? (
              <li className="dropdown-empty">
                {searchTerm ? 'No options found' : 'No options available'}
              </li>
            ) : (
              filteredOptions.map((option, index) => (
                <li
                  key={option.value}
                  className={`dropdown-option ${
                    isSelected(option) ? 'dropdown-option-selected' : ''
                  } ${
                    index === focusedIndex ? 'dropdown-option-focused' : ''
                  }`}
                  onClick={() => handleOptionSelect(option)}
                  role="option"
                  aria-selected={isSelected(option)}
                >
                  <div className="dropdown-option-content">
                    {renderOption ? renderOption(option) : (
                      <>
                        {multiple && (
                          <div className="dropdown-checkbox">
                            {isSelected(option) && <Check size={12} />}
                          </div>
                        )}
                        <span className="dropdown-option-label">
                          {option.label}
                        </span>
                        {!multiple && isSelected(option) && (
                          <Check size={16} className="dropdown-check" />
                        )}
                      </>
                    )}
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Dropdown;
