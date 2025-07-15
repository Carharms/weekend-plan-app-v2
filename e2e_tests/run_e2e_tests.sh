#!/bin/bash

# Run end-to-end tests with Playwright and generate comprehensive reports

echo "SInitiate e2e tests with Playwright"

# Create directories for test outputs
mkdir -p e2e_tests/reports
mkdir -p e2e_tests/screenshots

# Set env
export HEADLESS=true
export SLOWMO=50
export TEST_BASE_URL="http://localhost:5000"

# Run the Flask app
echo "Starting Flask application..."
cd ..
python app.py > e2e_tests/app.log 2>&1 &
APP_PID=$!
cd e2e_tests

# Wait for application to start
echo "Waiting for application to start"
sleep 10

# Check if application is running
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "Application is running successfully"
else
    echo "Application failed to start"
    kill $APP_PID
    exit 1
fi

# Backup: installing Playwright if it isn't setup already
if ! command -v playwright &> /dev/null; then
    echo "Installing Playwright..."
    chmod +x install_playwright.sh
    ./install_playwright.sh
fi

# Run E2E tests with comprehensive reporting
echo "Initaiting e2e tests"
python -m pytest test_user_journey.py \
    --html=reports/e2e-report.html \
    --self-contained-html \
    --junitxml=reports/e2e-results.xml \
    --verbose \
    --tb=short \
    --capture=no

# Capture exit code
TEST_EXIT_CODE=$?

# Stop the Flask application
echo "Stopping Flask app"
kill $APP_PID

# Generate summary report
echo "Generating test summary"
cat > reports/test_summary.txt << EOF
=== End-to-End Test Summary ===
Date: $(date)
Test Framework: Playwright + pytest
Browser: Chromium (headless)
Application URL: $TEST_BASE_URL

Test Results:
$(python -m pytest test_user_journey.py --collect-only -q | grep "test session starts" -A 10)

Exit Code: $TEST_EXIT_CODE
$([ $TEST_EXIT_CODE -eq 0 ] && echo "Status: PASSED" || echo "Status: FAILED")

Generated Files:
- HTML Report: reports/e2e-report.html
- JUnit XML: reports/e2e-results.xml
- Screenshots: screenshots/
- Application Log: app.log
EOF

# Display results
echo ""
echo "E2E Tests Completed!"
echo "Reports can be found here: e2e_tests/reports/"
echo "Screenshots can be found here: e2e_tests/screenshots/"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "Each test passed successfully!"
else
    echo "Test failures. Check reports for failure details!"
fi

exit $TEST_EXIT_CODE