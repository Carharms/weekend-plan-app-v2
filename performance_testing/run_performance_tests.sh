#!/bin/bash
# Run performance tests with k6

echo "Starting performance tests..."

# create directory for results
mkdir -p performance_results

# Run performance tests
locust -f locustfile.py \
    --host=http://localhost:5000 \
    --users=10 \
    --spawn-rate=2 \
    --run-time=60s \
    --html=performance_results/performance_report.html \
    --csv=performance_results/performance_results \
    --headless

echo "Locust performance tests complete"