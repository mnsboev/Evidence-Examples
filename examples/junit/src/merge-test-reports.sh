#!/bin/bash

# Script to merge all JUnit test reports into a single consolidated report
# Usage: ./merge-test-reports.sh

set -e

echo "=== JUnit Test Report Merger ==="
echo ""

# Check if we're in the right directory
if [ ! -d "target/surefire-reports" ]; then
    echo "Error: target/surefire-reports directory not found. Please run 'mvn test' first."
    exit 1
fi

# Initialize counters
total_tests=0
total_failures=0
total_errors=0
total_skipped=0
total_time=0

echo "Processing test reports..."

# Process each XML report file
for file in target/surefire-reports/*.xml; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "  Processing: $filename"
        
        # Extract test statistics
        tests=$(grep -o 'tests="[0-9]*"' "$file" | sed 's/tests="\([0-9]*\)"/\1/')
        failures=$(grep -o 'failures="[0-9]*"' "$file" | sed 's/failures="\([0-9]*\)"/\1/')
        errors=$(grep -o 'errors="[0-9]*"' "$file" | sed 's/errors="\([0-9]*\)"/\1/')
        skipped=$(grep -o 'skipped="[0-9]*"' "$file" | sed 's/skipped="\([0-9]*\)"/\1/')
        time=$(grep -o 'time="[0-9.]*"' "$file" | head -1 | sed 's/time="\([0-9.]*\)"/\1/')
        
        # Handle empty values
        tests=${tests:-0}
        failures=${failures:-0}
        errors=${errors:-0}
        skipped=${skipped:-0}
        time=${time:-0}
        
        # Accumulate totals
        total_tests=$((total_tests + tests))
        total_failures=$((total_failures + failures))
        total_errors=$((total_errors + errors))
        total_skipped=$((total_skipped + skipped))
        
        # Handle time calculation more robustly
        if command -v bc >/dev/null 2>&1; then
            total_time=$(echo "$total_time + $time" | bc -l)
        else
            total_time=$(awk "BEGIN {print $total_time + $time}")
        fi
        
        echo "    Tests: $tests, Failures: $failures, Errors: $errors, Skipped: $skipped, Time: ${time}s"
    fi
done

echo ""
echo "=== CONSOLIDATED TEST RESULTS ==="
echo "Total Tests: $total_tests"
echo "Total Failures: $total_failures"
echo "Total Errors: $total_errors"
echo "Total Skipped: $total_skipped"
echo "Total Time: ${total_time}s"

# Calculate success rate
if [ $total_tests -gt 0 ]; then
    success_rate=$(( (total_tests - total_failures - total_errors) * 100 / total_tests ))
    echo "Success Rate: ${success_rate}%"
else
    echo "Success Rate: N/A (no tests found)"
fi

echo ""
echo "=== TEST CLASSES EXECUTED ==="
for file in target/surefire-reports/*.xml; do
    if [ -f "$file" ]; then
        classname=$(grep -o 'name="[^"]*Test"' "$file" | head -1 | sed 's/name="\([^"]*\)"/\1/')
        if [ -n "$classname" ]; then
            echo "- $classname"
        fi
    fi
done

echo ""
echo "=== DETAILED TEST RESULTS ==="
for file in target/surefire-reports/*.xml; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .xml)
        echo "--- $filename ---"
        
        # Extract and display test case results
        grep -o '<testcase[^>]*name="[^"]*"[^>]*>' "$file" | while read line; do
            testname=$(echo "$line" | grep -o 'name="[^"]*"' | sed 's/name="\([^"]*\)"/\1/')
            classname=$(echo "$line" | grep -o 'classname="[^"]*"' | sed 's/classname="\([^"]*\)"/\1/')
            time=$(echo "$line" | grep -o 'time="[0-9.]*"' | sed 's/time="\([0-9.]*\)"/\1/')
            
            if [ -n "$testname" ] && [ -n "$classname" ]; then
                time_display=${time:-0}
                echo "  ✓ $classname.$testname (${time_display}s)"
            fi
        done
        
        # Check for failures
        if grep -q '<failure' "$file"; then
            echo "  ❌ Failures found:"
            grep -A 2 '<failure' "$file" | while read line; do
                if echo "$line" | grep -q 'message='; then
                    message=$(echo "$line" | grep -o 'message="[^"]*"' | sed 's/message="\([^"]*\)"/\1/')
                    echo "    - $message"
                fi
            done
        fi
        
        echo ""
    fi
done

# Create a consolidated XML report
echo "=== GENERATING CONSOLIDATED XML REPORT ==="
consolidated_file="target/consolidated-test-report.xml"

cat > "$consolidated_file" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="Consolidated Test Report" 
             tests="$total_tests" 
             failures="$total_failures" 
             errors="$total_errors" 
             skipped="$total_skipped" 
             time="$total_time">
EOF

# Merge all test cases into the consolidated report
for file in target/surefire-reports/*.xml; do
    if [ -f "$file" ]; then
        # Extract testcase elements and append to consolidated report
        grep '<testcase' "$file" | sed 's/^/    /' >> "$consolidated_file"
    fi
done

echo "  </testsuite>" >> "$consolidated_file"
echo "</testsuites>" >> "$consolidated_file"

echo "Consolidated report saved to: $consolidated_file"
echo ""
echo "=== MERGE COMPLETE ===" 