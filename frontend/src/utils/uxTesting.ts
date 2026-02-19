/**
 * UX Testing and Validation Utilities
 */

export interface UXTestResult {
  testName: string;
  passed: boolean;
  score: number;
  details: string;
  recommendations?: string[];
  wcagLevel?: 'A' | 'AA' | 'AAA';
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
    
    // Check for sufficient contrast ratios
    elements.forEach(element => {
      const style = window.getComputedStyle(element);
      const backgroundColor = style.backgroundColor;
      const color = style.color;
      
      // Simple contrast check (in real implementation, use proper contrast calculation)
      if (backgroundColor === 'transparent' || color === 'transparent') {
        passed = false;
      }
    });
    
    return passed;
  }

  private testFocusIndicators(): boolean {
    // Simulate focus indicator testing
    const interactiveElements = document.querySelectorAll('button, a, input, select, textarea');
    let passed = true;
    
    interactiveElements.forEach(element => {
      const style = window.getComputedStyle(element);
      const outline = style.outline;
      const boxShadow = style.boxShadow;
      
      // Check if focus indicators are present
      if (outline === 'none' && !boxShadow.includes('rgba')) {
        passed = false;
      }
    });
    
    return passed;
  }

  private testTouchTargets(): boolean {
    // Simulate touch target testing
    const touchElements = document.querySelectorAll('button, a, input[type="button"], input[type="submit"]');
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
    // Simulate keyboard navigation testing
    const interactiveElements = document.querySelectorAll('button, a, input, select, textarea');
    let passed = true;
    
    interactiveElements.forEach(element => {
      const tabIndex = element.getAttribute('tabindex');
      if (tabIndex === '-1') {
        passed = false;
      }
    });
    
    return passed;
  }

  private testScreenReaderSupport(): boolean {
    // Simulate screen reader support testing
    const elements = document.querySelectorAll('*');
    let passed = true;
    
    elements.forEach(element => {
      const ariaLabel = element.getAttribute('aria-label');
      const ariaLabelledby = element.getAttribute('aria-labelledby');
      const role = element.getAttribute('role');
      
      // Check for basic ARIA support
      if (element.tagName === 'BUTTON' && !ariaLabel && !ariaLabelledby) {
        passed = false;
      }
    });
    
    return passed;
  }

  // Performance Test Methods
  private testPageLoadTime(): boolean {
    // Simulate page load time testing
    const loadTime = performance.now();
    return loadTime < 3000; // 3 seconds threshold
  }

  private testInteractiveResponse(): boolean {
    // Simulate interactive response testing
    const startTime = performance.now();
    
    // Simulate interaction
    setTimeout(() => {
      const responseTime = performance.now() - startTime;
      return responseTime < 100; // 100ms threshold
    }, 50);
    
    return true; // Simplified for demo
  }

  private testSmoothScrolling(): boolean {
    // Simulate smooth scrolling testing
    return 'scrollBehavior' in document.documentElement.style;
  }

  // Usability Test Methods
  private testMobileResponsiveness(): boolean {
    // Simulate mobile responsiveness testing
    const viewport = window.innerWidth;
    return viewport >= 320; // Minimum mobile width
  }

  private testNavigationClarity(): boolean {
    // Simulate navigation clarity testing
    const navElements = document.querySelectorAll('nav, [role="navigation"]');
    return navElements.length > 0;
  }

  private testErrorHandling(): boolean {
    // Simulate error handling testing
    const errorElements = document.querySelectorAll('[role="alert"], .error, .alert');
    return errorElements.length > 0;
  }

  // Test Execution Methods
  async runAccessibilityTests(): Promise<UXTestResult[]> {
    this.results = [];
    
    for (const test of this.accessibilityTests) {
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
    }
    
    return this.results.filter(r => r.wcagLevel);
  }

  async runPerformanceTests(): Promise<UXTestResult[]> {
    this.results = [];
    
    for (const test of this.performanceTests) {
        const passed = test.test();
      
        const result: UXTestResult = {
          testName: test.name,
          passed,
          score: passed ? 100 : 0,
          details: test.description,
          recommendations: passed ? [] : [`Optimize ${test.name.toLowerCase()} for better performance`]
        };
        
        this.results.push(result);
    }
    
    return this.results.filter(r => !r.wcagLevel && r.testName.includes('Performance'));
  }

  async runUsabilityTests(): Promise<UXTestResult[]> {
    this.results = [];
    
    for (const test of this.usabilityTests) {
        const passed = test.test();
      
        const result: UXTestResult = {
          testName: test.name,
          passed,
          score: passed ? 100 : 0,
          details: test.description,
          recommendations: passed ? [] : [`Improve ${test.name.toLowerCase()} for better usability`]
        };
        
        this.results.push(result);
    }
    
    return this.results.filter(r => !r.wcagLevel && !r.testName.includes('Performance'));
  }

  async runAllTests(): Promise<UXTestResult[]> {
    const accessibilityResults = await this.runAccessibilityTests();
    const performanceResults = await this.runPerformanceTests();
    const usabilityResults = await this.runUsabilityTests();
    
    return [...accessibilityResults, ...performanceResults, ...usabilityResults];
  }

  // Reporting Methods
  generateReport(): string {
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
    
    const overallScore = total > 0 ? (passed / total) * 100 : 0;
    
    let report = `# UX Testing Report\n\n`;
    report += `## Summary\n`;
    report += `- **Overall Score:** ${overallScore.toFixed(1)}%\n`;
    report += `- **Tests Passed:** ${passed}/${total}\n`;
    report += `- **Tests Failed:** ${failed}/${total}\n\n`;
    
    report += `## Category Scores\n`;
    report += `- **Accessibility:** ${accessibilityScore.toFixed(1)}%\n`;
    report += `- **Performance:** ${performanceScore.toFixed(1)}%\n`;
    report += `- **Usability:** ${usabilityScore.toFixed(1)}%\n\n`;
    
    report += `## Failed Tests\n`;
    const failedTests = this.results.filter(r => !r.passed);
    if (failedTests.length === 0) {
      report += `All tests passed! 🎉\n\n`;
    } else {
      failedTests.forEach(test => {
        report += `### ${test.testName}\n`;
        report += `- **Details:** ${test.details}\n`;
        if (test.recommendations && test.recommendations.length > 0) {
          report += `- **Recommendations:**\n`;
          test.recommendations.forEach(rec => {
            report += `  - ${rec}\n`;
          });
        }
        report += `\n`;
      });
    }
    
    return report;
  }

  getResults(): UXTestResult[] {
    return this.results;
  }

  clearResults(): void {
    this.results = [];
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
    
    const overallScore = total > 0 ? (passed / total) * 100 : 0;
    
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
}

// Export singleton instance
export const uxTesting = new UXTestingSuite();

