import React, { createContext, useContext, useMemo } from 'react';

// Analysis Context
const AnalysisContext = createContext(null);

export const AnalysisProvider = ({ children, value }) => {
  // Memoize the context value to prevent unnecessary re-renders
  const memoizedValue = useMemo(() => value, [value]);
  
  return (
    <AnalysisContext.Provider value={memoizedValue}>
      {children}
    </AnalysisContext.Provider>
  );
};

export const useAnalysis = () => {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return context;
};

// Selector hooks for specific parts of the analysis state
export const useAnalysisResults = () => {
  const { analysisResults } = useAnalysis();
  return analysisResults;
};

export const useAnalysisLoading = () => {
  const { isAnalyzing } = useAnalysis();
  return isAnalyzing;
};

export const useAnalysisError = () => {
  const { analysisError } = useAnalysis();
  return analysisError;
};

export const useAnalysisActions = () => {
  const { actions } = useAnalysis();
  return actions;
};

export const useFileState = () => {
  const { selectedFile, fileContent } = useAnalysis();
  return { selectedFile, fileContent };
};

export const useDatabaseEngine = () => {
  const { selectedEngine, actions } = useAnalysis();
  return {
    selectedEngine,
    setDatabaseEngine: actions.setDatabaseEngine
  };
};

export const useExportState = () => {
  const { exportFormat, isExporting, actions } = useAnalysis();
  return {
    exportFormat,
    isExporting,
    setExportFormat: actions.setExportFormat,
    exportResults: actions.exportResults
  };
};
