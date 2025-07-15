import React, { useRef, useEffect, useState } from 'react';

const CodeEditor = ({ 
  value, 
  onChange, 
  language = 'sql',
  theme = 'dark',
  fontSize = 14,
  wordWrap = true,
  lineNumbers = true,
  minimap = true,
  readOnly = false 
}) => {
  const editorRef = useRef(null);
  const [lineCount, setLineCount] = useState(1);
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });

  useEffect(() => {
    const lines = (value.match(/\n/g) || []).length + 1;
    setLineCount(lines);
  }, [value]);

  const handleTextareaChange = (e) => {
    const newValue = e.target.value;
    onChange(newValue);
    
    // Update cursor position
    const textarea = e.target;
    const textBeforeCursor = newValue.substring(0, textarea.selectionStart);
    const lines = textBeforeCursor.split('\n');
    const line = lines.length;
    const column = lines[lines.length - 1].length + 1;
    setCursorPosition({ line, column });
  };

  const handleKeyDown = (e) => {
    const textarea = e.target;
    
    // Tab handling
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newValue = value.substring(0, start) + '  ' + value.substring(end);
      onChange(newValue);
      
      // Set cursor position after tab
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 2;
      }, 0);
    }
    
    // Auto-indent on Enter
    if (e.key === 'Enter') {
      const start = textarea.selectionStart;
      const textBeforeCursor = value.substring(0, start);
      const lines = textBeforeCursor.split('\n');
      const currentLine = lines[lines.length - 1];
      const indent = currentLine.match(/^\s*/)[0];
      
      // Add extra indent for certain SQL keywords
      const sqlKeywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT'];
      const lastWord = currentLine.trim().split(/\s+/).pop()?.toUpperCase();
      const extraIndent = sqlKeywords.includes(lastWord) ? '  ' : '';
      
      const newValue = value.substring(0, start) + '\n' + indent + extraIndent + value.substring(start);
      onChange(newValue);
      
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 1 + indent.length + extraIndent.length;
      }, 0);
      
      e.preventDefault();
    }
  };

  const generateLineNumbers = () => {
    return Array.from({ length: lineCount }, (_, i) => i + 1);
  };

  const highlightSQL = (text) => {
    // Simple SQL syntax highlighting
    const keywords = [
      'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP',
      'TABLE', 'INDEX', 'VIEW', 'DATABASE', 'SCHEMA', 'JOIN', 'INNER', 'LEFT', 'RIGHT',
      'OUTER', 'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN', 'LIKE',
      'ORDER', 'BY', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'INTERSECT',
      'EXCEPT', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'IF', 'NULL', 'TRUE', 'FALSE'
    ];
    
    const functions = [
      'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'CONCAT', 'SUBSTRING', 'LENGTH',
      'UPPER', 'LOWER', 'TRIM', 'NOW', 'DATE', 'TIME', 'YEAR', 'MONTH', 'DAY'
    ];
    
    let highlighted = text;
    
    // Highlight keywords
    keywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
      highlighted = highlighted.replace(regex, `<span class="sql-keyword">${keyword}</span>`);
    });
    
    // Highlight functions
    functions.forEach(func => {
      const regex = new RegExp(`\\b${func}\\s*\\(`, 'gi');
      highlighted = highlighted.replace(regex, (match) => 
        `<span class="sql-function">${match.slice(0, -1)}</span>(`
      );
    });
    
    // Highlight strings
    highlighted = highlighted.replace(/'([^']*)'/g, '<span class="sql-string">\'$1\'</span>');
    highlighted = highlighted.replace(/"([^"]*)"/g, '<span class="sql-string">"$1"</span>');
    
    // Highlight numbers
    highlighted = highlighted.replace(/\b\d+(\.\d+)?\b/g, '<span class="sql-number">$&</span>');
    
    // Highlight comments
    highlighted = highlighted.replace(/--.*$/gm, '<span class="sql-comment">$&</span>');
    highlighted = highlighted.replace(/\/\*[\s\S]*?\*\//g, '<span class="sql-comment">$&</span>');
    
    return highlighted;
  };

  return (
    <div className={`code-editor ${theme}`}>
      <div className="editor-container">
        {lineNumbers && (
          <div className="line-numbers">
            {generateLineNumbers().map(lineNum => (
              <div key={lineNum} className="line-number">
                {lineNum}
              </div>
            ))}
          </div>
        )}
        
        <div className="editor-content">
          {/* Syntax highlighting overlay */}
          <div 
            className="syntax-highlight"
            dangerouslySetInnerHTML={{ 
              __html: highlightSQL(value).replace(/\n/g, '<br/>') 
            }}
          />
          
          {/* Actual textarea */}
          <textarea
            ref={editorRef}
            value={value}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            className="editor-textarea"
            style={{ fontSize: `${fontSize}px` }}
            spellCheck={false}
            readOnly={readOnly}
            placeholder={readOnly ? 'Análisis en progreso...' : 'Escribe tu consulta SQL aquí...'}
          />
        </div>
        
        {minimap && value.length > 500 && (
          <div className="editor-minimap">
            <div className="minimap-content">
              {value.split('\n').map((line, index) => (
                <div 
                  key={index} 
                  className="minimap-line"
                  style={{ 
                    height: '2px',
                    backgroundColor: line.trim() ? 'var(--text-secondary)' : 'transparent',
                    opacity: line.trim() ? 0.6 : 0
                  }}
                />
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Editor footer */}
      <div className="editor-footer">
        <div className="editor-info">
          <span>Línea {cursorPosition.line}, Columna {cursorPosition.column}</span>
          <span>{value.length} caracteres</span>
          <span>{lineCount} líneas</span>
        </div>
        
        <div className="editor-settings">
          <span className="language-indicator">{language.toUpperCase()}</span>
          {wordWrap && <span className="wrap-indicator">Wrap</span>}
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;
