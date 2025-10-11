"""
Comprehensive Test Runner for Iteration 3
Orchestrates all testing modules and generates consolidated reports.

Usage:
    python tests/iteration_3/run_comprehensive_tests.py

    Optional arguments:
    --tracking-only     Run only plant tracking tests
    --chat-only        Run only chat tests
    --workflow-only    Run only workflow tests
    --no-cleanup       Don't clean up test data after tests

Requirements:
- Backend server must be running on http://localhost:8000
- Production database accessible
- Real Gemini API access
"""

import sys
import os
import argparse
import json
from datetime import datetime
from typing import Dict, Any
import time
import requests

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.iteration_3.test_plant_tracking_live import run_comprehensive_tests as run_tracking_tests
from tests.iteration_3.test_plant_chat_live import run_comprehensive_chat_tests
from tests.iteration_3.test_end_to_end_workflow import run_end_to_end_workflows


class ComprehensiveTestRunner:
    """Main test orchestrator for Iteration 3"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0,
            "server_status": "unknown",
            "modules": {},
            "summary": {
                "total_tests": 0,
                "total_passed": 0,
                "total_failed": 0,
                "pass_rate": 0.0
            }
        }

    def check_server_health(self) -> bool:
        """Check if backend server is running"""
        print("Checking backend server health...")

        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)

            if response.status_code == 200:
                print(f"✓ Server is running at {self.base_url}")
                self.test_results["server_status"] = "running"
                return True
            else:
                print(f"✗ Server returned status code: {response.status_code}")
                self.test_results["server_status"] = "error"
                return False

        except requests.exceptions.ConnectionError:
            print(f"✗ Cannot connect to server at {self.base_url}")
            print("  Please ensure the backend server is running.")
            self.test_results["server_status"] = "unreachable"
            return False
        except Exception as e:
            print(f"✗ Error checking server health: {e}")
            self.test_results["server_status"] = "error"
            return False

    def check_dependencies(self) -> bool:
        """Check if all dependencies are available"""
        print("\nChecking dependencies...")

        # Check if test data file exists
        test_data_path = "tests/iteration_3/fixtures/test_data.json"

        if not os.path.exists(test_data_path):
            print(f"✗ Test data file not found: {test_data_path}")
            return False

        print("✓ Test data file found")

        # Check if reports directory exists
        reports_dir = "tests/iteration_3/reports"

        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            print(f"✓ Created reports directory: {reports_dir}")
        else:
            print(f"✓ Reports directory exists: {reports_dir}")

        return True

    def run_plant_tracking_tests(self):
        """Run plant tracking endpoint tests"""
        print("\n" + "="*70)
        print("MODULE: PLANT TRACKING ENDPOINTS")
        print("="*70)

        try:
            start_time = time.time()
            results = run_tracking_tests()
            duration = time.time() - start_time

            self.test_results["modules"]["plant_tracking"] = {
                "status": "completed",
                "duration_seconds": round(duration, 2),
                "total_tests": results["total_tests"],
                "passed": results["passed"],
                "failed": results["failed"],
                "pass_rate": results["pass_rate"]
            }

            return True

        except Exception as e:
            print(f"\n✗ Error running plant tracking tests: {e}")

            self.test_results["modules"]["plant_tracking"] = {
                "status": "error",
                "error": str(e)
            }

            return False

    def run_plant_chat_tests(self):
        """Run plant chat endpoint tests"""
        print("\n" + "="*70)
        print("MODULE: PLANT CHAT ENDPOINTS")
        print("="*70)

        try:
            # Get a test instance ID from previous tests if available
            instance_id = None

            if "plant_tracking" in self.test_results["modules"]:
                # Try to use an instance from tracking tests
                # For now, we'll pass None and let it skip plant-specific tests
                instance_id = None

            start_time = time.time()
            results = run_comprehensive_chat_tests(test_instance_id=instance_id)
            duration = time.time() - start_time

            self.test_results["modules"]["plant_chat"] = {
                "status": "completed",
                "duration_seconds": round(duration, 2),
                "total_tests": results["total_tests"],
                "passed": results["passed"],
                "failed": results["failed"],
                "pass_rate": results["pass_rate"]
            }

            return True

        except Exception as e:
            print(f"\n✗ Error running plant chat tests: {e}")

            self.test_results["modules"]["plant_chat"] = {
                "status": "error",
                "error": str(e)
            }

            return False

    def run_workflow_tests(self):
        """Run end-to-end workflow tests"""
        print("\n" + "="*70)
        print("MODULE: END-TO-END WORKFLOWS")
        print("="*70)

        try:
            start_time = time.time()
            results = run_end_to_end_workflows()
            duration = time.time() - start_time

            # Count total steps
            total_steps = 0
            passed_steps = 0

            for workflow_data in results["workflows"].values():
                total_steps += len(workflow_data["steps"])
                passed_steps += workflow_data["passed"]

            self.test_results["modules"]["workflows"] = {
                "status": "completed",
                "duration_seconds": round(duration, 2),
                "total_workflows": len(results["workflows"]),
                "total_steps": total_steps,
                "passed_steps": passed_steps,
                "failed_steps": total_steps - passed_steps,
                "pass_rate": (passed_steps / total_steps * 100) if total_steps > 0 else 0
            }

            return True

        except Exception as e:
            print(f"\n✗ Error running workflow tests: {e}")

            self.test_results["modules"]["workflows"] = {
                "status": "error",
                "error": str(e)
            }

            return False

    def calculate_summary(self):
        """Calculate overall test summary"""
        total_tests = 0
        total_passed = 0
        total_failed = 0

        for module_name, module_data in self.test_results["modules"].items():
            if module_data["status"] == "completed":
                if module_name in ["plant_tracking", "plant_chat"]:
                    total_tests += module_data.get("total_tests", 0)
                    total_passed += module_data.get("passed", 0)
                    total_failed += module_data.get("failed", 0)
                elif module_name == "workflows":
                    total_tests += module_data.get("total_steps", 0)
                    total_passed += module_data.get("passed_steps", 0)
                    total_failed += module_data.get("failed_steps", 0)

        self.test_results["summary"] = {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "pass_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0
        }

    def print_final_report(self):
        """Print consolidated test report"""
        print("\n" + "="*70)
        print("ITERATION 3 - COMPREHENSIVE TEST REPORT")
        print("="*70)

        # Module summaries
        print("\nModule Results:")
        print("-" * 70)

        for module_name, module_data in self.test_results["modules"].items():
            module_display = module_name.replace("_", " ").title()

            if module_data["status"] == "completed":
                if module_name in ["plant_tracking", "plant_chat"]:
                    print(f"\n{module_display}:")
                    print(f"  Total Tests: {module_data['total_tests']}")
                    print(f"  Passed: {module_data['passed']} ✓")
                    print(f"  Failed: {module_data['failed']} ✗")
                    print(f"  Pass Rate: {module_data['pass_rate']:.2f}%")
                    print(f"  Duration: {module_data['duration_seconds']}s")
                elif module_name == "workflows":
                    print(f"\n{module_display}:")
                    print(f"  Total Workflows: {module_data['total_workflows']}")
                    print(f"  Total Steps: {module_data['total_steps']}")
                    print(f"  Passed Steps: {module_data['passed_steps']} ✓")
                    print(f"  Failed Steps: {module_data['failed_steps']} ✗")
                    print(f"  Pass Rate: {module_data['pass_rate']:.2f}%")
                    print(f"  Duration: {module_data['duration_seconds']}s")
            else:
                print(f"\n{module_display}: {module_data['status'].upper()}")

                if "error" in module_data:
                    print(f"  Error: {module_data['error']}")

        # Overall summary
        print("\n" + "="*70)
        print("OVERALL SUMMARY")
        print("="*70)

        summary = self.test_results["summary"]
        print(f"\nTotal Tests: {summary['total_tests']}")
        print(f"Passed: {summary['total_passed']} ✓")
        print(f"Failed: {summary['total_failed']} ✗")
        print(f"Pass Rate: {summary['pass_rate']:.2f}%")
        print(f"Total Duration: {self.test_results['duration_seconds']:.2f}s")

        # Status indicator
        if summary['pass_rate'] == 100:
            print(f"\n{'✓' * 35}")
            print("ALL TESTS PASSED!")
            print(f"{'✓' * 35}")
        elif summary['pass_rate'] >= 90:
            print(f"\n{'⚠' * 35}")
            print("MOSTLY PASSED - Minor Issues")
            print(f"{'⚠' * 35}")
        else:
            print(f"\n{'✗' * 35}")
            print("SIGNIFICANT FAILURES - Review Required")
            print(f"{'✗' * 35}")

    def save_consolidated_report(self):
        """Save consolidated test report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"tests/iteration_3/reports/comprehensive_results_{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)

        print(f"\nConsolidated report saved to: {report_file}")

        # Also save a summary text file
        summary_file = f"tests/iteration_3/reports/summary_{timestamp}.txt"

        with open(summary_file, 'w') as f:
            f.write("ITERATION 3 - COMPREHENSIVE TEST SUMMARY\n")
            f.write("="*70 + "\n\n")
            f.write(f"Test Date: {self.test_results['start_time']}\n")
            f.write(f"Duration: {self.test_results['duration_seconds']:.2f}s\n")
            f.write(f"Server Status: {self.test_results['server_status']}\n\n")

            f.write("Module Results:\n")
            f.write("-"*70 + "\n")

            for module_name, module_data in self.test_results["modules"].items():
                f.write(f"\n{module_name.upper()}:\n")

                if module_data["status"] == "completed":
                    if module_name in ["plant_tracking", "plant_chat"]:
                        f.write(f"  Total Tests: {module_data['total_tests']}\n")
                        f.write(f"  Passed: {module_data['passed']}\n")
                        f.write(f"  Failed: {module_data['failed']}\n")
                        f.write(f"  Pass Rate: {module_data['pass_rate']:.2f}%\n")

            f.write(f"\n{'='*70}\n")
            f.write("OVERALL SUMMARY\n")
            f.write(f"{'='*70}\n\n")

            summary = self.test_results["summary"]
            f.write(f"Total Tests: {summary['total_tests']}\n")
            f.write(f"Passed: {summary['total_passed']}\n")
            f.write(f"Failed: {summary['total_failed']}\n")
            f.write(f"Pass Rate: {summary['pass_rate']:.2f}%\n")

        print(f"Summary report saved to: {summary_file}")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Run comprehensive Iteration 3 tests")
    parser.add_argument("--tracking-only", action="store_true", help="Run only plant tracking tests")
    parser.add_argument("--chat-only", action="store_true", help="Run only chat tests")
    parser.add_argument("--workflow-only", action="store_true", help="Run only workflow tests")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't clean up test data after tests")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend server URL (default: localhost for VM testing)")

    args = parser.parse_args()

    print("\n" + "="*70)
    print("ITERATION 3 - COMPREHENSIVE TESTING SUITE")
    print("="*70)
    print(f"\nServer URL: {args.base_url}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    runner = ComprehensiveTestRunner(base_url=args.base_url)

    # Pre-flight checks
    if not runner.check_server_health():
        print("\n✗ Pre-flight checks failed. Aborting tests.")
        return 1

    if not runner.check_dependencies():
        print("\n✗ Dependency checks failed. Aborting tests.")
        return 1

    # Record start time
    start_time = time.time()

    # Run selected tests
    if args.tracking_only:
        runner.run_plant_tracking_tests()
    elif args.chat_only:
        runner.run_plant_chat_tests()
    elif args.workflow_only:
        runner.run_workflow_tests()
    else:
        # Run all tests
        runner.run_plant_tracking_tests()
        time.sleep(2)  # Brief pause between modules

        runner.run_plant_chat_tests()
        time.sleep(2)

        runner.run_workflow_tests()

    # Calculate total duration
    runner.test_results["duration_seconds"] = round(time.time() - start_time, 2)
    runner.test_results["end_time"] = datetime.now().isoformat()

    # Calculate summary
    runner.calculate_summary()

    # Print final report
    runner.print_final_report()

    # Save consolidated report
    runner.save_consolidated_report()

    # Cleanup reminder
    if not args.no_cleanup:
        print("\n" + "="*70)
        print("CLEANUP REMINDER")
        print("="*70)
        print("\nTest data was created in the production database.")
        print("To clean up test data, run:")
        print("  python tests/iteration_3/cleanup_test_data.py")
        print("\nOr use --no-cleanup flag to keep test data for inspection.")

    # Return exit code based on test results
    if runner.test_results["summary"]["total_failed"] == 0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
