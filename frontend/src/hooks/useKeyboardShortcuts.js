import { useEffect } from 'react';

/**
 * Custom hook for keyboard shortcuts
 * Provides enterprise-grade keyboard shortcuts for productivity
 */
export const useKeyboardShortcuts = (callbacks) => {
  useEffect(() => {
    const handleKeyDown = (event) => {
      const { ctrlKey, metaKey, shiftKey, altKey, key } = event;
      const isCtrlOrCmd = ctrlKey || metaKey;

      // Prevent default browser shortcuts when our shortcuts are active
      const shouldPreventDefault = () => {
        // Ctrl/Cmd + S (Save)
        if (isCtrlOrCmd && key === 's') return true;
        // Ctrl/Cmd + Enter (Analyze)
        if (isCtrlOrCmd && key === 'Enter') return true;
        // Ctrl/Cmd + Shift + E (Export)
        if (isCtrlOrCmd && shiftKey && key === 'E') return true;
        // Ctrl/Cmd + Shift + M (Metrics)
        if (isCtrlOrCmd && shiftKey && key === 'M') return true;
        // Ctrl/Cmd + Shift + C (Connection)
        if (isCtrlOrCmd && shiftKey && key === 'C') return true;
        // Ctrl/Cmd + T (New Tab)
        if (isCtrlOrCmd && key === 't') return true;
        // Ctrl/Cmd + W (Close Tab)
        if (isCtrlOrCmd && key === 'w') return true;
        // F5 (Analyze)
        if (key === 'F5') return true;
        // F9 (Toggle Sidebar)
        if (key === 'F9') return true;
        // F10 (Toggle Right Panel)
        if (key === 'F10') return true;
        // F11 (Toggle Bottom Panel)
        if (key === 'F11') return true;
        
        return false;
      };

      if (shouldPreventDefault()) {
        event.preventDefault();
      }

      // Execute shortcuts
      try {
        // File operations
        if (isCtrlOrCmd && key === 's' && callbacks.onSave) {
          callbacks.onSave();
        }
        
        // Analysis operations
        if (isCtrlOrCmd && key === 'Enter' && callbacks.onAnalyze) {
          callbacks.onAnalyze();
        }
        
        if (key === 'F5' && callbacks.onAnalyze) {
          callbacks.onAnalyze();
        }
        
        // Export operations
        if (isCtrlOrCmd && shiftKey && key === 'E' && callbacks.onExport) {
          callbacks.onExport();
        }
        
        // Metrics dashboard
        if (isCtrlOrCmd && shiftKey && key === 'M' && callbacks.onOpenMetrics) {
          callbacks.onOpenMetrics();
        }
        
        // Connection modal
        if (isCtrlOrCmd && shiftKey && key === 'C' && callbacks.onOpenConnection) {
          callbacks.onOpenConnection();
        }
        
        // Tab operations
        if (isCtrlOrCmd && key === 't' && callbacks.onNewTab) {
          callbacks.onNewTab();
        }
        
        if (isCtrlOrCmd && key === 'w' && callbacks.onCloseTab) {
          callbacks.onCloseTab();
        }
        
        // Tab navigation
        if (isCtrlOrCmd && key >= '1' && key <= '9' && callbacks.onSelectTab) {
          const tabIndex = parseInt(key) - 1;
          callbacks.onSelectTab(tabIndex);
        }
        
        // Panel toggles
        if (key === 'F9' && callbacks.onToggleSidebar) {
          callbacks.onToggleSidebar();
        }
        
        if (key === 'F10' && callbacks.onToggleRightPanel) {
          callbacks.onToggleRightPanel();
        }
        
        if (key === 'F11' && callbacks.onToggleBottomPanel) {
          callbacks.onToggleBottomPanel();
        }
        
        // View mode switching
        if (isCtrlOrCmd && key === '1' && callbacks.onSetViewMode) {
          callbacks.onSetViewMode('editor');
        }
        
        if (isCtrlOrCmd && key === '2' && callbacks.onSetViewMode) {
          callbacks.onSetViewMode('split');
        }
        
        if (isCtrlOrCmd && key === '3' && callbacks.onSetViewMode) {
          callbacks.onSetViewMode('results');
        }
        
        // Search and replace
        if (isCtrlOrCmd && key === 'f' && callbacks.onFind) {
          callbacks.onFind();
        }
        
        if (isCtrlOrCmd && key === 'h' && callbacks.onReplace) {
          callbacks.onReplace();
        }
        
        // Format SQL
        if (isCtrlOrCmd && shiftKey && key === 'F' && callbacks.onFormat) {
          callbacks.onFormat();
        }
        
        // Comment/Uncomment
        if (isCtrlOrCmd && key === '/' && callbacks.onToggleComment) {
          callbacks.onToggleComment();
        }
        
        // Duplicate line
        if (isCtrlOrCmd && shiftKey && key === 'D' && callbacks.onDuplicateLine) {
          callbacks.onDuplicateLine();
        }
        
        // Move line up/down
        if (altKey && key === 'ArrowUp' && callbacks.onMoveLineUp) {
          callbacks.onMoveLineUp();
        }
        
        if (altKey && key === 'ArrowDown' && callbacks.onMoveLineDown) {
          callbacks.onMoveLineDown();
        }
        
        // Zoom
        if (isCtrlOrCmd && key === '=' && callbacks.onZoomIn) {
          callbacks.onZoomIn();
        }
        
        if (isCtrlOrCmd && key === '-' && callbacks.onZoomOut) {
          callbacks.onZoomOut();
        }
        
        if (isCtrlOrCmd && key === '0' && callbacks.onZoomReset) {
          callbacks.onZoomReset();
        }
        
        // Help
        if (key === 'F1' && callbacks.onShowHelp) {
          callbacks.onShowHelp();
        }
        
        // Quick actions
        if (isCtrlOrCmd && shiftKey && key === 'P' && callbacks.onCommandPalette) {
          callbacks.onCommandPalette();
        }
        
      } catch (error) {
        console.error('Keyboard shortcut error:', error);
      }
    };

    // Add event listener
    document.addEventListener('keydown', handleKeyDown);

    // Cleanup
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [callbacks]);
};

/**
 * Get formatted shortcut display text
 */
export const getShortcutText = (shortcut) => {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  const cmdKey = isMac ? '⌘' : 'Ctrl';
  const altKey = isMac ? '⌥' : 'Alt';
  const shiftKey = '⇧';
  
  const shortcuts = {
    save: `${cmdKey}+S`,
    analyze: `${cmdKey}+Enter`,
    analyzeF5: 'F5',
    export: `${cmdKey}+${shiftKey}+E`,
    metrics: `${cmdKey}+${shiftKey}+M`,
    connection: `${cmdKey}+${shiftKey}+C`,
    newTab: `${cmdKey}+T`,
    closeTab: `${cmdKey}+W`,
    toggleSidebar: 'F9',
    toggleRightPanel: 'F10',
    toggleBottomPanel: 'F11',
    viewEditor: `${cmdKey}+1`,
    viewSplit: `${cmdKey}+2`,
    viewResults: `${cmdKey}+3`,
    find: `${cmdKey}+F`,
    replace: `${cmdKey}+H`,
    format: `${cmdKey}+${shiftKey}+F`,
    comment: `${cmdKey}+/`,
    duplicate: `${cmdKey}+${shiftKey}+D`,
    moveUp: `${altKey}+↑`,
    moveDown: `${altKey}+↓`,
    zoomIn: `${cmdKey}+=`,
    zoomOut: `${cmdKey}+-`,
    zoomReset: `${cmdKey}+0`,
    help: 'F1',
    commandPalette: `${cmdKey}+${shiftKey}+P`
  };
  
  return shortcuts[shortcut] || shortcut;
};

/**
 * Get all available shortcuts with descriptions
 */
export const getAllShortcuts = () => {
  return [
    { category: 'Archivo', shortcuts: [
      { key: 'save', description: 'Guardar archivo actual' },
      { key: 'newTab', description: 'Nueva pestaña' },
      { key: 'closeTab', description: 'Cerrar pestaña actual' }
    ]},
    { category: 'Análisis', shortcuts: [
      { key: 'analyze', description: 'Analizar SQL' },
      { key: 'analyzeF5', description: 'Analizar SQL (alternativo)' },
      { key: 'export', description: 'Exportar resultados' }
    ]},
    { category: 'Vista', shortcuts: [
      { key: 'viewEditor', description: 'Vista de editor' },
      { key: 'viewSplit', description: 'Vista dividida' },
      { key: 'viewResults', description: 'Vista de resultados' },
      { key: 'toggleSidebar', description: 'Alternar barra lateral' },
      { key: 'toggleRightPanel', description: 'Alternar panel derecho' },
      { key: 'toggleBottomPanel', description: 'Alternar panel inferior' }
    ]},
    { category: 'Edición', shortcuts: [
      { key: 'find', description: 'Buscar' },
      { key: 'replace', description: 'Buscar y reemplazar' },
      { key: 'format', description: 'Formatear SQL' },
      { key: 'comment', description: 'Comentar/descomentar' },
      { key: 'duplicate', description: 'Duplicar línea' },
      { key: 'moveUp', description: 'Mover línea arriba' },
      { key: 'moveDown', description: 'Mover línea abajo' }
    ]},
    { category: 'Sistema', shortcuts: [
      { key: 'metrics', description: 'Dashboard de métricas' },
      { key: 'connection', description: 'Configurar conexión' },
      { key: 'help', description: 'Ayuda' },
      { key: 'commandPalette', description: 'Paleta de comandos' }
    ]},
    { category: 'Zoom', shortcuts: [
      { key: 'zoomIn', description: 'Aumentar zoom' },
      { key: 'zoomOut', description: 'Disminuir zoom' },
      { key: 'zoomReset', description: 'Restablecer zoom' }
    ]}
  ];
};
