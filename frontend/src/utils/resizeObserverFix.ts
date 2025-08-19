/**
 * ResizeObserver Loop Error Fix
 * 
 * This utility fixes the "ResizeObserver loop completed with undelivered notifications" error
 * that commonly occurs in React applications when components are resized rapidly.
 */

// Store the original console.error
const originalConsoleError = console.error;

// Override console.error to suppress ResizeObserver errors
console.error = (...args: any[]) => {
  const message = args[0];
  
  // Check if the error is a ResizeObserver loop error
  if (
    typeof message === 'string' &&
    message.includes('ResizeObserver loop completed with undelivered notifications')
  ) {
    // Suppress this specific error
    return;
  }
  
  // Log all other errors normally
  originalConsoleError.apply(console, args);
};

// Alternative approach: Create a debounced ResizeObserver
export class DebouncedResizeObserver {
  private observer: ResizeObserver;
  private timeoutId: number | null = null;
  private callback: ResizeObserverCallback;
  private delay: number;

  constructor(callback: ResizeObserverCallback, delay: number = 100) {
    this.callback = callback;
    this.delay = delay;
    
    this.observer = new ResizeObserver((entries, observer) => {
      // Clear existing timeout
      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
      }
      
      // Debounce the callback
      this.timeoutId = window.setTimeout(() => {
        this.callback(entries, observer);
      }, this.delay);
    });
  }

  observe(target: Element): void {
    this.observer.observe(target);
  }

  unobserve(target: Element): void {
    this.observer.unobserve(target);
  }

  disconnect(): void {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }
    this.observer.disconnect();
  }
}

// Hook for React components
export const useDebouncedResizeObserver = (
  callback: ResizeObserverCallback,
  delay: number = 100
) => {
  return new DebouncedResizeObserver(callback, delay);
};

// Utility function to create a safe ResizeObserver
export const createSafeResizeObserver = (callback: ResizeObserverCallback) => {
  try {
    return new ResizeObserver((entries, observer) => {
      try {
        callback(entries, observer);
      } catch (error) {
        // Log error but don't break the observer
        console.warn('ResizeObserver callback error:', error);
      }
    });
  } catch (error) {
    console.warn('Failed to create ResizeObserver:', error);
    return null;
  }
};

// Global error handler for ResizeObserver errors
export const setupResizeObserverErrorHandler = () => {
  const originalErrorHandler = window.onerror;
  
  window.onerror = (message, source, lineno, colno, error) => {
    // Check if it's a ResizeObserver error
    if (
      typeof message === 'string' &&
      message.includes('ResizeObserver loop completed with undelivered notifications')
    ) {
      // Suppress this error
      return true;
    }
    
    // Call original error handler for other errors
    if (originalErrorHandler) {
      return originalErrorHandler(message, source, lineno, colno, error);
    }
    
    return false;
  };
};

// Initialize the error handler
setupResizeObserverErrorHandler();

// Export a function to manually suppress ResizeObserver errors
export const suppressResizeObserverErrors = () => {
  const originalError = console.error;
  console.error = (...args: any[]) => {
    const message = args[0];
    if (
      typeof message === 'string' &&
      message.includes('ResizeObserver loop completed with undelivered notifications')
    ) {
      return;
    }
    originalError.apply(console, args);
  };
};

// Export a function to restore original console.error
export const restoreConsoleError = () => {
  console.error = originalConsoleError;
};
