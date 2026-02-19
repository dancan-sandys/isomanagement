/**
 * Frontend Performance Monitoring and Optimization
 */

export interface PerformanceMetric {
  name: string;
  duration: number;
  timestamp: number;
  category: 'navigation' | 'api' | 'render' | 'user-interaction';
  metadata?: Record<string, any>;
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private observers: Map<string, PerformanceObserver> = new Map();

  constructor() {
    this.initializeObservers();
  }

  private initializeObservers() {
    // Monitor navigation timing
    if ('PerformanceObserver' in window) {
      const navigationObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'navigation') {
            const navEntry = entry as PerformanceNavigationTiming;
            this.recordMetric({
              name: 'page-navigation',
              duration: navEntry.loadEventEnd - navEntry.loadEventStart,
              timestamp: Date.now(),
              category: 'navigation',
              metadata: {
                url: navEntry.name,
                domContentLoaded: navEntry.domContentLoadedEventEnd - navEntry.domContentLoadedEventStart,
                loadComplete: navEntry.loadEventEnd - navEntry.loadEventStart,
              }
            });
          }
        });
      });
      
      navigationObserver.observe({ entryTypes: ['navigation'] });
      this.observers.set('navigation', navigationObserver);
    }

    // Monitor long tasks
    if ('PerformanceObserver' in window) {
      const longTaskObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'longtask') {
            this.recordMetric({
              name: 'long-task',
              duration: entry.duration,
              timestamp: Date.now(),
              category: 'render',
              metadata: {
                startTime: entry.startTime,
                name: entry.name,
              }
            });
          }
        });
      });
      
      longTaskObserver.observe({ entryTypes: ['longtask'] });
      this.observers.set('longtask', longTaskObserver);
    }
  }

  recordMetric(metric: PerformanceMetric) {
    this.metrics.push(metric);
    
    // Keep only last 1000 metrics to prevent memory issues
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000);
    }

    // Log slow operations
    if (metric.duration > 100) {
      console.warn(`Slow operation detected: ${metric.name} took ${metric.duration}ms`, metric);
    }
  }

  recordAPICall(endpoint: string, duration: number, success: boolean) {
    this.recordMetric({
      name: `api-${endpoint}`,
      duration,
      timestamp: Date.now(),
      category: 'api',
      metadata: {
        endpoint,
        success,
      }
    });
  }

  recordUserInteraction(action: string, duration: number) {
    this.recordMetric({
      name: `user-${action}`,
      duration,
      timestamp: Date.now(),
      category: 'user-interaction',
      metadata: {
        action,
      }
    });
  }

  getMetrics(category?: string, timeRange?: { start: number; end: number }) {
    let filtered = this.metrics;

    if (category) {
      filtered = filtered.filter(m => m.category === category);
    }

    if (timeRange) {
      filtered = filtered.filter(m => 
        m.timestamp >= timeRange.start && m.timestamp <= timeRange.end
      );
    }

    return filtered;
  }

  getPerformanceSummary() {
    const now = Date.now();
    const last5Minutes = now - 5 * 60 * 1000;
    const recentMetrics = this.getMetrics(undefined, { start: last5Minutes, end: now });

    const apiMetrics = recentMetrics.filter(m => m.category === 'api');
    const navigationMetrics = recentMetrics.filter(m => m.category === 'navigation');
    const renderMetrics = recentMetrics.filter(m => m.category === 'render');

    return {
      totalMetrics: recentMetrics.length,
      averageAPITime: apiMetrics.length > 0 
        ? apiMetrics.reduce((sum, m) => sum + m.duration, 0) / apiMetrics.length 
        : 0,
      averageNavigationTime: navigationMetrics.length > 0
        ? navigationMetrics.reduce((sum, m) => sum + m.duration, 0) / navigationMetrics.length
        : 0,
      slowOperations: recentMetrics.filter(m => m.duration > 100).length,
      apiCalls: apiMetrics.length,
      navigations: navigationMetrics.length,
    };
  }

  exportMetrics() {
    return {
      metrics: this.metrics,
      summary: this.getPerformanceSummary(),
      timestamp: Date.now(),
    };
  }

  clearMetrics() {
    this.metrics = [];
  }

  disconnect() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers.clear();
  }
}

// Global performance monitor instance
export const performanceMonitor = new PerformanceMonitor();

// Performance optimization utilities
export const performanceUtils = {
  // Debounce function calls
  debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  },

  // Throttle function calls
  throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
  ): (...args: Parameters<T>) => void {
    let inThrottle: boolean;
    return (...args: Parameters<T>) => {
      if (!inThrottle) {
        func(...args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  // Lazy load images
  lazyLoadImage(img: HTMLImageElement, src: string) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          img.src = src;
          observer.unobserve(img);
        }
      });
    });
    observer.observe(img);
  },

  // Preload critical resources
  preloadResource(href: string, as: string = 'fetch') {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = href;
    link.as = as;
    document.head.appendChild(link);
  },

  // Measure function execution time
  measureTime<T>(name: string, fn: () => T): T {
    const start = performance.now();
    const result = fn();
    const duration = performance.now() - start;
    
    performanceMonitor.recordMetric({
      name: `function-${name}`,
      duration,
      timestamp: Date.now(),
      category: 'render',
      metadata: { functionName: name }
    });
    
    return result;
  },

  // Async version of measureTime
  async measureTimeAsync<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const start = performance.now();
    const result = await fn();
    const duration = performance.now() - start;
    
    performanceMonitor.recordMetric({
      name: `async-function-${name}`,
      duration,
      timestamp: Date.now(),
      category: 'api',
      metadata: { functionName: name }
    });
    
    return result;
  }
};

// React performance optimization hooks
export const usePerformanceOptimization = () => {
  const optimizeScroll = performanceUtils.throttle((callback: () => void) => {
    callback();
  }, 16); // ~60fps

  const optimizeResize = performanceUtils.debounce((callback: () => void) => {
    callback();
  }, 250);

  const optimizeSearch = performanceUtils.debounce((callback: (query: string) => void) => {
    callback;
  }, 300);

  return {
    optimizeScroll,
    optimizeResize,
    optimizeSearch,
  };
};

export default performanceMonitor;

