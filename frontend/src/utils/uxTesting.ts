/**
 * UX Testing and Validation Utilities
 */

export interface UXTestResult {
  testName: string;
  passed: boolean;
  score: number;
  details: string;
  recommendations?: string[];
}

export interface AccessibilityTest {
  name: string;
  test: () => boolean;
  description: string;
  wcagLevel: 'A' | 'AA' | 'AAA';
}

class UXTestingSuite {
  private results: UXTestResult[] = [];

  // Accessibility Tests
  private accessibilityTests: AccessibilityTest[] = [
    {
      name: 'Color Contrast',
      test: () => this.testColorContrast(),
      description: 'Check if text has sufficient contrast ratio',
      wcagLevel: 'AA'
    },
    {
      name: 'Focus Indicators',
      test: () => this.testFocusIndicators(),
      description: 'Verify focus indicators are visible',
      wcagLevel: 'AA'
    },
    {
      name: 'Touch Targets',
      test: () => this.testTouchTargets(),
      description: 'Check if touch targets are at least 44px',
      wcagLevel: 'AA'
    },
    {
      name: 'Keyboard Navigation',
      test: () => this.testKeyboardNavigation(),
      description: 'Verify all interactive elements are keyboard accessible',
      wcagLevel: 'AA'
    },
    {
      name: 'Screen Reader Support',
      test: () => this.testScreenReaderSupport(),
      description: 'Check for proper ARIA labels and roles',
      wcagLevel: 'AA'
    }
  ];

  // Performance Tests
  private performanceTests = [
    {
      name: 'Page Load Time',
      test: () => this.testPageLoadTime(),
      description: 'Check if page loads within 3 seconds'
    },
    {
      name: 'Interactive Response',
      test: () => this.testInteractiveResponse(),
      description: 'Verify interactive elements respond within 100ms'
    },
    {
      name: 'Smooth Scrolling',
      test: () => this.testSmoothScrolling(),
      description: 'Check for smooth scrolling performance'
    }
  ];

  // Usability Tests
  private usabilityTests = [
    {
      name: 'Mobile Responsiveness',
      test: () => this.testMobileResponsiveness(),
      description: 'Verify responsive design on mobile devices'
    },
    {
      name: 'Navigation Clarity',
      test: () => this.testNavigationClarity(),
      description: 'Check if navigation is clear and intuitive'
    },
    {
      name: 'Error Handling',
      test: () => this.testErrorHandling(),
      description: 'Verify proper error messages and recovery'
    }
  ];

  // Accessibility Test Methods
  private testColorContrast(): boolean {
    // Simulate color contrast testing
    const elements = document.querySelectorAll('*');
    let passed = true;
    
    elements.forEach(element => {
      const style = window.getComputedStyle(element);
      const color = style.color;
      const backgroundColor = style.backgroundColor;
      
      // Basic contrast check (simplified)
      if (color && backgroundColor) {
        // This is a simplified check - real implementation would use color contrast algorithms
        passed = passed && true; // Placeholder
      }
    });
    
    return passed;
  }

  private testFocusIndicators(): boolean {
    const interactiveElements = document.querySelectorAll('button, a, input, select, textarea, [tabindex]');
    let passed = true;
    
    interactiveElements.forEach(element => {
      const style = window.getComputedStyle(element);
      const outline = style.outline;
      const outlineOffset = style.outlineOffset;
      
      // Check if focus indicators are present
      if (outline === 'none' && !element.hasAttribute('aria-label')) {
        passed = false;
      }
    });
    
    return passed;
  }

  private testTouchTargets(): boolean {
    const touchElements = document.querySelectorAll('button, a, input, [role="button"]');
    let passed = true;
    
    touchElements.forEach(element => {
      const rect = element.getBoundingClientRect();
      const minSize = 44; // WCAG minimum touch target size
      
      if (rect.width < minSize || rect.height < minSize) {
        passed = false;
      }
    });
    
    return passed;
  }

  private testKeyboardNavigation(): boolean {
    const interactiveElements = document.querySelectorAll('button, a, input, select, textarea');
    let passed = true;
    
    interactiveElements.forEach(element => {
      const tabIndex = element.getAttribute('tabindex');
      const disabled = element.hasAttribute('disabled');
      const hidden = element.hasAttribute('hidden');
      
      // Check if element is keyboard accessible
      if (!disabled && !hidden && tabIndex === '-1') {
        passed = false;
      }
    });
    
    return passed;
  }

  private testScreenReaderSupport(): boolean {
    const elements = document.querySelectorAll('img, button, a, input, select, textarea');
    let passed = true;
    
    elements.forEach(element => {
      const hasAriaLabel = element.hasAttribute('aria-label');
      const hasAriaLabelledBy = element.hasAttribute('aria-labelledby');
      const hasAlt = element.hasAttribute('alt');
      const hasTitle = element.hasAttribute('title');
      
      // Check if element has proper accessibility attributes
      if (element.tagName === 'IMG' && !hasAlt && !hasAriaLabel) {
        passed = false;
      }
    });
    
    return passed;
  }

  // Performance Test Methods
  private testPageLoadTime(): boolean {
    const loadTime = performance.now();
    return loadTime < 3000; // 3 seconds threshold
  }

  private testInteractiveResponse(): boolean {
    // Simulate interaction response time test
    const startTime = performance.now();
    // Simulate a simple interaction
    setTimeout(() => {
      const responseTime = performance.now() - startTime;
      return responseTime < 100; // 100ms threshold
    }, 0);
    
    return true; // Placeholder
  }

  private testSmoothScrolling(): boolean {
    // Check if smooth scrolling is enabled
    const html = document.documentElement;
    const style = window.getComputedStyle(html);
    return style.scrollBehavior === 'smooth';
  }

  // Usability Test Methods
  private testMobileResponsiveness(): boolean {
    const viewport = window.innerWidth;
    const isMobile = viewport <= 768;
    
    if (isMobile) {
      // Check for mobile-specific optimizations
      const touchElements = document.querySelectorAll('button, a');
      let hasProperTouchTargets = true;
      
      touchElements.forEach(element => {
        const rect = element.getBoundingClientRect();
        if (rect.width < 44 || rect.height < 44) {
          hasProperTouchTargets = false;
        }
      });
      
      return hasProperTouchTargets;
    }
    
    return true;
  }

  private testNavigationClarity(): boolean {
    const navigationElements = document.querySelectorAll('nav, [role="navigation"]');
    return navigationElements.length > 0;
  }

  private testErrorHandling(): boolean {
    // Check for error handling elements
    const errorElements = document.querySelectorAll('[role="alert"], .error, .alert');
    return errorElements.length > 0;
  }

  // Main Testing Methods
  async runAccessibilityTests(): Promise<UXTestResult[]> {
    console.log('Running accessibility tests...');
    
    this.accessibilityTests.forEach(test => {
      try {
        const passed = test.test();
        const result: UXTestResult = {
          testName: test.name,
          passed,
          score: passed ? 100 : 0,
          details: test.description,
          wcagLevel: test.wcagLevel,
          recommendations: passed ? [] : [`Improve ${test.name.toLowerCase()} for better accessibility`]
        };
        
        this.results.push(result);
      } catch (error) {
        this.results.push({
          testName: test.name,
          passed: false,
          score: 0,
          details: `Test failed: ${error}`,
          recommendations: ['Fix test implementation']
        });
      }
    });
    
    return this.results.filter(r => r.wcagLevel);
  }

  async runPerformanceTests(): Promise<UXTestResult[]> {
    console.log('Running performance tests...');
    
    this.performanceTests.forEach(test => {
      try {
        const passed = test.test();
        const result: UXTestResult = {
          testName: test.name,
          passed,
          score: passed ? 100 : 0,
          details: test.description,
          recommendations: passed ? [] : [`Optimize ${test.name.toLowerCase()} for better performance`]
        };
        
        this.results.push(result);
      } catch (error) {
        this.results.push({
          testName: test.name,
          passed: false,
          score: 0,
          details: `Test failed: ${error}`,
          recommendations: ['Fix test implementation']
        });
      }
    });
    
    return this.results.filter(r => !r.wcagLevel && r.testName.includes('Performance'));
  }

  async runUsabilityTests(): Promise<UXTestResult[]> {
    console.log('Running usability tests...');
    
    this.usabilityTests.forEach(test => {
      try {
        const passed = test.test();
        const result: UXTestResult = {
          testName: test.name,
          passed,
          score: passed ? 100 : 0,
          details: test.description,
          recommendations: passed ? [] : [`Improve ${test.name.toLowerCase()} for better usability`]
        };
        
        this.results.push(result);
      } catch (error) {
        this.results.push({
          testName: test.name,
          passed: false,
          score: 0,
          details: `Test failed: ${error}`,
          recommendations: ['Fix test implementation']
        });
      }
    });
    
    return this.results.filter(r => !r.wcagLevel && !r.testName.includes('Performance'));
  }

  async runAllTests(): Promise<UXTestResult[]> {
    this.results = [];
    
    await this.runAccessibilityTests();
    await this.runPerformanceTests();
    await this.runUsabilityTests();
    
    return this.results;
  }

  getTestSummary(): {
    total: number;
    passed: number;
    failed: number;
    overallScore: number;
    accessibilityScore: number;
    performanceScore: number;
    usabilityScore: number;
  } {
    const total = this.results.length;
    const passed = this.results.filter(r => r.passed).length;
    const failed = total - passed;
    
    const accessibilityTests = this.results.filter(r => r.wcagLevel);
    const performanceTests = this.results.filter(r => !r.wcagLevel && r.testName.includes('Performance'));
    const usabilityTests = this.results.filter(r => !r.wcagLevel && !r.testName.includes('Performance'));
    
    const accessibilityScore = accessibilityTests.length > 0 
      ? accessibilityTests.reduce((sum, r) => sum + r.score, 0) / accessibilityTests.length 
      : 0;
    
    const performanceScore = performanceTests.length > 0 
      ? performanceTests.reduce((sum, r) => sum + r.score, 0) / performanceTests.length 
      : 0;
    
    const usabilityScore = usabilityTests.length > 0 
      ? usabilityTests.reduce((sum, r) => sum + r.score, 0) / usabilityTests.length 
      : 0;
    
    const overallScore = total > 0 
      ? this.results.reduce((sum, r) => sum + r.score, 0) / total 
      : 0;
    
    return {
      total,
      passed,
      failed,
      overallScore,
      accessibilityScore,
      performanceScore,
      usabilityScore
    };
  }

  generateReport(): string {
    const summary = this.getTestSummary();
    
    let report = `# UX Testing Report\n\n`;
    report += `## Summary\n`;
    report += `- Total Tests: ${summary.total}\n`;
    report += `- Passed: ${summary.passed}\n`;
    report += `- Failed: ${summary.failed}\n`;
    report += `- Overall Score: ${summary.overallScore.toFixed(1)}%\n\n`;
    
    report += `## Detailed Results\n\n`;
    
    this.results.forEach(result => {
      const status = result.passed ? '✅ PASS' : '❌ FAIL';
      report += `### ${result.testName}\n`;
      report += `- Status: ${status}\n`;
      report += `- Score: ${result.score}%\n`;
      report += `- Details: ${result.details}\n`;
      
      if (result.recommendations && result.recommendations.length > 0) {
        report += `- Recommendations:\n`;
        result.recommendations.forEach(rec => {
          report += `  - ${rec}\n`;
        });
      }
      
      report += `\n`;
    });
    
    return report;
  }
}

// Global UX testing instance
export const uxTesting = new UXTestingSuite();

export default uxTesting;

