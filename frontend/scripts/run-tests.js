#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🧪 TRACEABILITY & RECALL MODULE - COMPREHENSIVE TEST SUITE');
console.log('========================================================\n');

const testResults = {
  unit: { passed: 0, failed: 0, total: 0 },
  integration: { passed: 0, failed: 0, total: 0 },
  mobile: { passed: 0, failed: 0, total: 0 },
  accessibility: { passed: 0, failed: 0, total: 0 },
  performance: { passed: 0, failed: 0, total: 0 },
  coverage: { statements: 0, branches: 0, functions: 0, lines: 0 }
};

const runTestSuite = (suiteName, command) => {
  console.log(`\n📋 Running ${suiteName.toUpperCase()} Tests...`);
  console.log('─'.repeat(50));
  
  try {
    const output = execSync(command, { 
      encoding: 'utf8', 
      stdio: 'pipe',
      timeout: 300000 // 5 minutes timeout
    });
    
    // Parse test results
    const lines = output.split('\n');
    let passed = 0, failed = 0, total = 0;
    
    lines.forEach(line => {
      if (line.includes('Tests:')) {
        const match = line.match(/(\d+) passed, (\d+) failed/);
        if (match) {
          passed = parseInt(match[1]);
          failed = parseInt(match[2]);
          total = passed + failed;
        }
      }
    });
    
    testResults[suiteName] = { passed, failed, total };
    
    console.log(`✅ ${suiteName} tests completed:`);
    console.log(`   Passed: ${passed}`);
    console.log(`   Failed: ${failed}`);
    console.log(`   Total: ${total}`);
    
    return true;
  } catch (error) {
    console.log(`❌ ${suiteName} tests failed:`);
    console.log(`   Error: ${error.message}`);
    testResults[suiteName] = { passed: 0, failed: 1, total: 1 };
    return false;
  }
};

const runCoverageTest = () => {
  console.log('\n📊 Running Coverage Analysis...');
  console.log('─'.repeat(50));
  
  try {
    const output = execSync('npm run test:coverage', { 
      encoding: 'utf8', 
      stdio: 'pipe',
      timeout: 300000
    });
    
    // Parse coverage results
    const lines = output.split('\n');
    lines.forEach(line => {
      if (line.includes('Statements')) {
        const match = line.match(/(\d+\.?\d*)%/);
        if (match) testResults.coverage.statements = parseFloat(match[1]);
      }
      if (line.includes('Branches')) {
        const match = line.match(/(\d+\.?\d*)%/);
        if (match) testResults.coverage.branches = parseFloat(match[1]);
      }
      if (line.includes('Functions')) {
        const match = line.match(/(\d+\.?\d*)%/);
        if (match) testResults.coverage.functions = parseFloat(match[1]);
      }
      if (line.includes('Lines')) {
        const match = line.match(/(\d+\.?\d*)%/);
        if (match) testResults.coverage.lines = parseFloat(match[1]);
      }
    });
    
    console.log('✅ Coverage analysis completed:');
    console.log(`   Statements: ${testResults.coverage.statements}%`);
    console.log(`   Branches: ${testResults.coverage.branches}%`);
    console.log(`   Functions: ${testResults.coverage.functions}%`);
    console.log(`   Lines: ${testResults.coverage.lines}%`);
    
    return true;
  } catch (error) {
    console.log(`❌ Coverage analysis failed: ${error.message}`);
    return false;
  }
};

const generateTestReport = () => {
  console.log('\n📈 TEST EXECUTION SUMMARY');
  console.log('========================');
  
  const totalTests = Object.values(testResults).reduce((sum, suite) => {
    if (suite.total !== undefined) {
      return sum + suite.total;
    }
    return sum;
  }, 0);
  
  const totalPassed = Object.values(testResults).reduce((sum, suite) => {
    if (suite.passed !== undefined) {
      return sum + suite.passed;
    }
    return sum;
  }, 0);
  
  const totalFailed = Object.values(testResults).reduce((sum, suite) => {
    if (suite.failed !== undefined) {
      return sum + suite.failed;
    }
    return sum;
  }, 0);
  
  console.log(`\n📊 Overall Results:`);
  console.log(`   Total Tests: ${totalTests}`);
  console.log(`   Passed: ${totalPassed}`);
  console.log(`   Failed: ${totalFailed}`);
  console.log(`   Success Rate: ${totalTests > 0 ? ((totalPassed / totalTests) * 100).toFixed(1) : 0}%`);
  
  console.log(`\n📋 Test Suite Breakdown:`);
  Object.entries(testResults).forEach(([suite, results]) => {
    if (results.total !== undefined) {
      const successRate = results.total > 0 ? ((results.passed / results.total) * 100).toFixed(1) : 0;
      const status = results.failed === 0 ? '✅' : '❌';
      console.log(`   ${status} ${suite}: ${results.passed}/${results.total} (${successRate}%)`);
    }
  });
  
  console.log(`\n📊 Coverage Summary:`);
  console.log(`   Statements: ${testResults.coverage.statements}%`);
  console.log(`   Branches: ${testResults.coverage.branches}%`);
  console.log(`   Functions: ${testResults.coverage.functions}%`);
  console.log(`   Lines: ${testResults.coverage.lines}%`);
  
  // Generate detailed report file
  const reportData = {
    timestamp: new Date().toISOString(),
    summary: {
      totalTests,
      totalPassed,
      totalFailed,
      successRate: totalTests > 0 ? ((totalPassed / totalTests) * 100).toFixed(1) : 0
    },
    testSuites: testResults,
    recommendations: []
  };
  
  // Add recommendations based on results
  if (testResults.coverage.statements < 80) {
    reportData.recommendations.push('Increase statement coverage to at least 80%');
  }
  if (testResults.coverage.branches < 70) {
    reportData.recommendations.push('Increase branch coverage to at least 70%');
  }
  if (totalFailed > 0) {
    reportData.recommendations.push('Fix failing tests before deployment');
  }
  if (testResults.accessibility.failed > 0) {
    reportData.recommendations.push('Address accessibility test failures');
  }
  if (testResults.performance.failed > 0) {
    reportData.recommendations.push('Address performance test failures');
  }
  
  // Write report to file
  const reportPath = path.join(__dirname, '../test-reports');
  if (!fs.existsSync(reportPath)) {
    fs.mkdirSync(reportPath, { recursive: true });
  }
  
  const reportFile = path.join(reportPath, `test-report-${Date.now()}.json`);
  fs.writeFileSync(reportFile, JSON.stringify(reportData, null, 2));
  
  console.log(`\n📄 Detailed report saved to: ${reportFile}`);
  
  // Generate HTML report
  const htmlReport = `
<!DOCTYPE html>
<html>
<head>
    <title>Traceability & Recall Module - Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { margin: 20px 0; }
        .suite { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 3px; }
        .passed { background: #d4edda; }
        .failed { background: #f8d7da; }
        .coverage { background: #d1ecf1; padding: 10px; border-radius: 3px; }
        .recommendations { background: #fff3cd; padding: 10px; border-radius: 3px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Traceability & Recall Module - Test Report</h1>
        <p>Generated: ${new Date().toLocaleString()}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <p><strong>Total Tests:</strong> ${totalTests}</p>
        <p><strong>Passed:</strong> ${totalPassed}</p>
        <p><strong>Failed:</strong> ${totalFailed}</p>
        <p><strong>Success Rate:</strong> ${totalTests > 0 ? ((totalPassed / totalTests) * 100).toFixed(1) : 0}%</p>
    </div>
    
    <div class="coverage">
        <h2>📊 Coverage</h2>
        <p><strong>Statements:</strong> ${testResults.coverage.statements}%</p>
        <p><strong>Branches:</strong> ${testResults.coverage.branches}%</p>
        <p><strong>Functions:</strong> ${testResults.coverage.functions}%</p>
        <p><strong>Lines:</strong> ${testResults.coverage.lines}%</p>
    </div>
    
    <h2>📋 Test Suites</h2>
    ${Object.entries(testResults).map(([suite, results]) => {
      if (results.total !== undefined) {
        const successRate = results.total > 0 ? ((results.passed / results.total) * 100).toFixed(1) : 0;
        const status = results.failed === 0 ? '✅' : '❌';
        const className = results.failed === 0 ? 'passed' : 'failed';
        return `
          <div class="suite ${className}">
            <h3>${status} ${suite}</h3>
            <p>Passed: ${results.passed} | Failed: ${results.failed} | Total: ${results.total} | Success Rate: ${successRate}%</p>
          </div>
        `;
      }
      return '';
    }).join('')}
    
    ${reportData.recommendations.length > 0 ? `
    <div class="recommendations">
        <h2>💡 Recommendations</h2>
        <ul>
            ${reportData.recommendations.map(rec => `<li>${rec}</li>`).join('')}
        </ul>
    </div>
    ` : ''}
</body>
</html>
  `;
  
  const htmlReportFile = path.join(reportPath, `test-report-${Date.now()}.html`);
  fs.writeFileSync(htmlReportFile, htmlReport);
  
  console.log(`📄 HTML report saved to: ${htmlReportFile}`);
  
  return totalFailed === 0;
};

// Main execution
const main = async () => {
  console.log('🚀 Starting comprehensive test suite execution...\n');
  
  // Run all test suites
  const unitSuccess = runTestSuite('unit', 'npm run test:unit');
  const integrationSuccess = runTestSuite('integration', 'npm run test:integration');
  const mobileSuccess = runTestSuite('mobile', 'npm run test:mobile');
  const accessibilitySuccess = runTestSuite('accessibility', 'npm run test:accessibility');
  const performanceSuccess = runTestSuite('performance', 'npm run test:performance');
  
  // Run coverage analysis
  const coverageSuccess = runCoverageTest();
  
  // Generate final report
  const allTestsPassed = generateTestReport();
  
  console.log('\n🎯 TEST EXECUTION COMPLETE');
  console.log('==========================');
  
  if (allTestsPassed) {
    console.log('✅ All tests passed! The traceability module is ready for deployment.');
    process.exit(0);
  } else {
    console.log('❌ Some tests failed. Please review the results and fix issues before deployment.');
    process.exit(1);
  }
};

// Handle errors
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

// Run the main function
main().catch(error => {
  console.error('Test execution failed:', error);
  process.exit(1);
});
