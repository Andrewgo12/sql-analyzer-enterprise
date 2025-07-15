import React, { createContext, useContext, useMemo } from 'react';

// Performance Context
const PerformanceContext = createContext(null);

export const PerformanceProvider = ({ children, value }) => {
  const memoizedValue = useMemo(() => value, [value]);
  
  return (
    <PerformanceContext.Provider value={memoizedValue}>
      {children}
    </PerformanceContext.Provider>
  );
};

export const usePerformance = () => {
  const context = useContext(PerformanceContext);
  if (!context) {
    throw new Error('usePerformance must be used within a PerformanceProvider');
  }
  return context;
};

// Selector hooks for performance metrics
export const usePerformanceMetrics = () => {
  const { metrics } = usePerformance();
  return metrics;
};

export const useResponseTime = () => {
  const { metrics } = usePerformance();
  return metrics.responseTime;
};

export const useMemoryUsage = () => {
  const { metrics } = usePerformance();
  return metrics.memoryUsage;
};

export const useCacheHitRate = () => {
  const { metrics } = usePerformance();
  return metrics.cacheHitRate;
};
