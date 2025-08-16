#!/usr/bin/env python3
"""
PRP Module Test Runner

This script runs comprehensive tests for the PRP module including:
- Integration tests
- Compliance tests (ISO 22002-1:2025)
- Performance tests
- Load tests

Usage:
    python run_prp_tests.py [--type integration|compliance|performance|all]
"""

import sys
import os
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def run_tests(test_type="all", verbose=False):
    """Run PRP module tests"""
    
    # Test files to run
    test_files = {
        "integration": ["tests/test_prp_integration.py"],
        "compliance": ["tests/test_prp_compliance.py"],
        "performance": ["tests/test_prp_performance.py"],
        "all": ["tests/test_prp_integration.py", "tests/test_prp_compliance.py", "tests/test_prp_performance.py"]
    }
    
    if test_type not in test_files:
        print(f"❌ Invalid test type: {test_type}")
        print("Available types: integration, compliance, performance, all")
        return False
    
    files_to_test = test_files[test_type]
    
    print(f"🚀 Starting PRP Module Tests - {test_type.upper()}")
    print(f"📅 Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Test files: {', '.join(files_to_test)}")
    print("=" * 80)
    
    results = {}
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    skipped_tests = 0
    
    for test_file in files_to_test:
        if not os.path.exists(test_file):
            print(f"⚠️  Test file not found: {test_file}")
            continue
        
        print(f"\n📋 Running tests from: {test_file}")
        print("-" * 60)
        
        # Run pytest for the specific file
        cmd = [
            sys.executable, "-m", "pytest", test_file,
            "--tb=short",
            "--durations=10",
            "--maxfail=10"
        ]
        
        if verbose:
            cmd.append("-v")
        
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=backend_dir)
            end_time = time.time()
            
            # Parse pytest output
            output_lines = result.stdout.split('\n')
            test_summary = None
            
            for line in output_lines:
                if "passed" in line and ("failed" in line or "skipped" in line):
                    test_summary = line.strip()
                    break
            
            # Extract test counts
            if test_summary:
                # Parse summary like "5 passed, 2 failed, 1 skipped in 10.5s"
                parts = test_summary.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        if "passed" in parts[i+1]:
                            passed = int(part)
                        elif "failed" in parts[i+1]:
                            failed = int(part)
                        elif "skipped" in parts[i+1]:
                            skipped = int(part)
            
            total_tests += passed + failed + skipped
            passed_tests += passed
            failed_tests += failed
            skipped_tests += skipped
            
            # Store results
            results[test_file] = {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "return_code": result.returncode,
                "duration": end_time - start_time,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "output": result.stdout,
                "errors": result.stderr
            }
            
            # Print results
            if result.returncode == 0:
                print(f"✅ {test_file}: PASSED ({passed} passed, {failed} failed, {skipped} skipped)")
            else:
                print(f"❌ {test_file}: FAILED ({passed} passed, {failed} failed, {skipped} skipped)")
            
            print(f"⏱️  Duration: {end_time - start_time:.2f} seconds")
            
            # Show errors if any
            if result.stderr:
                print(f"⚠️  Errors/Warnings:")
                for line in result.stderr.split('\n')[:5]:  # Show first 5 error lines
                    if line.strip():
                        print(f"   {line}")
            
        except Exception as e:
            print(f"❌ Error running {test_file}: {str(e)}")
            results[test_file] = {
                "status": "ERROR",
                "error": str(e)
            }
            failed_tests += 1
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"⏭️  Skipped: {skipped_tests}")
    
    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Overall status
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED!")
        overall_status = "PASSED"
    else:
        print(f"\n💥 {failed_tests} TESTS FAILED!")
        overall_status = "FAILED"
    
    # Save detailed results
    save_test_results(results, overall_status, {
        "total": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "skipped": skipped_tests,
        "success_rate": success_rate if total_tests > 0 else 0
    })
    
    return failed_tests == 0

def save_test_results(results, overall_status, summary):
    """Save test results to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_prp_{timestamp}.json"
    
    test_report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": overall_status,
        "summary": summary,
        "test_files": results
    }
    
    try:
        with open(results_file, 'w') as f:
            json.dump(test_report, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save results: {str(e)}")

def run_compliance_check():
    """Run additional compliance checks"""
    print("\n🔍 Running ISO 22002-1:2025 Compliance Checks")
    print("-" * 60)
    
    # Check if all required categories are present
    try:
        from app.models.prp import PRPCategory
        
        required_categories = [
            "construction_and_layout", "layout_of_premises", "supplies_of_air_water_energy",
            "supporting_services", "suitability_cleaning_maintenance", "management_of_purchased_materials",
            "prevention_of_cross_contamination", "cleaning_and_sanitizing", "pest_control",
            "personnel_hygiene_facilities", "personnel_hygiene_practices", "reprocessing",
            "product_recall_procedures", "warehousing", "product_information_consumer_awareness",
            "food_defense_biovigilance_bioterrorism", "control_of_nonconforming_product", "product_release"
        ]
        
        missing_categories = []
        for category in required_categories:
            if not hasattr(PRPCategory, category.upper()):
                missing_categories.append(category)
        
        if missing_categories:
            print(f"❌ Missing ISO categories: {', '.join(missing_categories)}")
            return False
        else:
            print("✅ All ISO 22002-1:2025 categories are present")
            return True
            
    except ImportError as e:
        print(f"❌ Could not import PRP models: {str(e)}")
        return False

def run_performance_benchmarks():
    """Run performance benchmarks"""
    print("\n⚡ Running Performance Benchmarks")
    print("-" * 60)
    
    try:
        # Import and run basic performance checks
        from tests.test_prp_performance import TestPRPPerformance
        
        print("✅ Performance test module loaded successfully")
        print("📊 Run 'python -m pytest tests/test_prp_performance.py -v' for detailed performance tests")
        
    except ImportError as e:
        print(f"❌ Could not import performance tests: {str(e)}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run PRP Module Tests")
    parser.add_argument("--type", choices=["integration", "compliance", "performance", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--compliance-only", action="store_true", help="Run only compliance checks")
    parser.add_argument("--benchmarks-only", action="store_true", help="Run only performance benchmarks")
    
    args = parser.parse_args()
    
    print("🏭 PRP Module Test Suite - ISO 22002-1:2025 Compliance")
    print("=" * 80)
    
    if args.compliance_only:
        success = run_compliance_check()
    elif args.benchmarks_only:
        success = run_performance_benchmarks()
    else:
        # Run main tests
        success = run_tests(args.type, args.verbose)
        
        # Run additional checks
        if success:
            print("\n" + "=" * 80)
            print("🔍 ADDITIONAL CHECKS")
            print("=" * 80)
            
            compliance_ok = run_compliance_check()
            benchmarks_ok = run_performance_benchmarks()
            
            if not compliance_ok:
                success = False
                print("❌ Compliance checks failed")
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 ALL CHECKS PASSED - PRP Module is ready for deployment!")
        sys.exit(0)
    else:
        print("💥 SOME CHECKS FAILED - Please review and fix issues before deployment!")
        sys.exit(1)

if __name__ == "__main__":
    main()
