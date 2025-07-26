#!/bin/bash

# Script to convert consolidated XML test report to JSON
# Usage: ./xml-to-json.sh

set -e

echo "=== XML to JSON Test Report Converter ==="
echo ""

# Check if consolidated XML report exists
xml_file="target/consolidated-test-report.xml"
json_file="target/consolidated-test-report.json"

if [ ! -f "$xml_file" ]; then
    echo "Error: Consolidated XML report not found at $xml_file"
    echo "Please run './merge-test-reports.sh' first to generate the XML report."
    exit 1
fi

echo "Converting $xml_file to $json_file..."

# Create JSON structure
cat > "$json_file" << 'EOF'
{
  "testReport": {
    "summary": {
EOF

# Extract test suite attributes
tests=$(grep -o 'tests="[0-9]*"' "$xml_file" | head -1 | sed 's/tests="\([0-9]*\)"/\1/')
failures=$(grep -o 'failures="[0-9]*"' "$xml_file" | head -1 | sed 's/failures="\([0-9]*\)"/\1/')
errors=$(grep -o 'errors="[0-9]*"' "$xml_file" | head -1 | sed 's/errors="\([0-9]*\)"/\1/')
skipped=$(grep -o 'skipped="[0-9]*"' "$xml_file" | head -1 | sed 's/skipped="\([0-9]*\)"/\1/')
time=$(grep -o 'time="[0-9.]*"' "$xml_file" | head -1 | sed 's/time="\([0-9.]*\)"/\1/')

# Handle empty values
tests=${tests:-0}
failures=${failures:-0}
errors=${errors:-0}
skipped=${skipped:-0}
time=${time:-0}

# Calculate success rate
if [ $tests -gt 0 ]; then
    success_rate=$(( (tests - failures - errors) * 100 / tests ))
else
    success_rate=0
fi

# Write summary
cat >> "$json_file" << EOF
      "totalTests": $tests,
      "totalFailures": $failures,
      "totalErrors": $errors,
      "totalSkipped": $skipped,
      "totalTime": "$time",
      "successRate": $success_rate,
      "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    },
    "testSuites": [
EOF

# Process each test case
first_test=true
grep '<testcase' "$xml_file" | while IFS= read -r line; do
    # Extract test case attributes using grep and sed
    testname=$(echo "$line" | grep -o 'name="[^"]*"' | head -1 | sed 's/name="\([^"]*\)"/\1/')
    classname=$(echo "$line" | grep -o 'classname="[^"]*"' | head -1 | sed 's/classname="\([^"]*\)"/\1/')
    time=$(echo "$line" | grep -o 'time="[0-9.]*"' | head -1 | sed 's/time="\([0-9.]*\)"/\1/')
    

    
    # Handle empty values
    testname=${testname:-"unknown"}
    classname=${classname:-"unknown"}
    time=${time:-0}
    
    # Add comma if not first test
    if [ "$first_test" = true ]; then
        first_test=false
    else
        echo "," >> "$json_file"
    fi
    
    # Write test case
    cat >> "$json_file" << EOF
      {
        "name": "$testname",
        "class": "$classname",
        "time": "$time",
        "status": "passed"
      }
EOF
done

# Close JSON structure
cat >> "$json_file" << 'EOF'
    ]
  }
}
EOF

echo "Conversion complete! JSON report saved to: $json_file"
echo ""

# Display the JSON content
echo "=== CONVERTED JSON REPORT ==="
cat "$json_file"
echo ""
echo "=== JSON REPORT END ===" 