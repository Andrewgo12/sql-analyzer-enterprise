import React, { createContext, useContext, useMemo } from 'react';

// UI Context
const UIContext = createContext(null);

export const UIProvider = ({ children, value }) => {
  const memoizedValue = useMemo(() => value, [value]);
  
  return (
    <UIContext.Provider value={memoizedValue}>
      {children}
    </UIContext.Provider>
  );
};

export const useUI = () => {
  const context = useContext(UIContext);
  if (!context) {
    throw new Error('useUI must be used within a UIProvider');
  }
  return context;
};

// Selector hooks for UI state
export const useActivePanel = () => {
  const { activePanel, actions } = useUI();
  return {
    activePanel,
    setActivePanel: actions.setActivePanel
  };
};

export const useSidebar = () => {
  const { sidebarCollapsed, actions } = useUI();
  return {
    sidebarCollapsed,
    toggleSidebar: actions.toggleSidebar
  };
};

export const useTheme = () => {
  const { theme, actions } = useUI();
  return {
    theme,
    setTheme: actions.setTheme
  };
};
