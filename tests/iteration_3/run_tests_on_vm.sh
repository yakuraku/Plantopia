#!/bin/bash
# Simple test runner for GCP VM
# Run this script on the VM after deployment

set -e

echo "=================================="
echo "Iteration 3 - Comprehensive Testing"
echo "=================================="
echo ""

# Activate virtual environment
source /opt/plantopia/Plantopia/venv/bin/activate

# Change to project directory
cd /opt/plantopia/Plantopia

# Run comprehensive tests against localhost (backend running on same VM)
echo "Running all Iteration 3 tests..."
python tests/iteration_3/run_comprehensive_tests.py --base-url http://localhost:8000

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests completed successfully!"
else
    echo ""
    echo "⚠️  Some tests failed. Check reports for details."
fi

# Show where reports are saved
echo ""
echo "📊 Test reports saved to:"
echo "   /opt/plantopia/Plantopia/tests/iteration_3/reports/"
echo ""
echo "💡 Download reports to local PC using:"
echo "   python tests/iteration_3/download_reports.py"
