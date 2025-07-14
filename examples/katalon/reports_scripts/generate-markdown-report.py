#!/usr/bin/env python3
"""
Generate markdown report from JUnit JSON data
Usage: python generate-markdown-report.py <input_json_file> <output_markdown_file> <package_url>
"""

import json
import sys
import os
from datetime import datetime

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds:.3f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.3f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        return f"{hours}h {remaining_minutes}m {remaining_seconds:.3f}s"

def generate_markdown_report(json_data, package_url):
    """Generate markdown report from JSON data"""
    
    # Extract test suite information
    testsuites = json_data.get('testsuites', {})
    suite_name = testsuites.get('name', 'Unknown Test Suite')
    total_tests = testsuites.get('tests', 0)
    total_failures = testsuites.get('failures', 0)
    total_errors = testsuites.get('errors', 0)
    total_time = testsuites.get('time', 0)
    
    # Calculate success rate
    total_passed = total_tests - total_failures - total_errors
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    # Generate markdown content
    markdown = f"""# Katalon Studio Test Execution Report

## Test Suite Summary

**Suite Name:** {suite_name}  
**Execution Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Package URL:** {package_url}

### Overall Results

| Metric | Value |
|--------|-------|
| **Total Tests** | {total_tests} |
| **Passed** | {total_passed} |
| **Failed** | {total_failures} |
| **Errors** | {total_errors} |
| **Success Rate** | {success_rate:.1f}% |
| **Total Duration** | {format_duration(total_time)} |

"""
    
    # Process each test suite
    for suite in testsuites.get('testsuite', []):
        suite_name = suite.get('name', 'Unknown')
        suite_tests = suite.get('tests', 0)
        suite_failures = suite.get('failures', 0)
        suite_errors = suite.get('errors', 0)
        suite_time = suite.get('time', 0)
        
        markdown += f"""## Test Suite: {suite_name}

**Duration:** {format_duration(suite_time)}  
**Tests:** {suite_tests} | **Passed:** {suite_tests - suite_failures - suite_errors} | **Failed:** {suite_failures} | **Errors:** {suite_errors}

### Test Results

| Test Case | Class | Duration | Status |
|-----------|-------|----------|--------|
"""
        
        # Process test cases and add to table
        for testcase in suite.get('testcase', []):
            case_name = testcase.get('name', 'Unknown')
            case_class = testcase.get('classname', 'Unknown')
            case_time = testcase.get('time', 0)
            case_status = testcase.get('status', 'unknown')
            
            markdown += f"| {case_name} | `{case_class}` | {format_duration(case_time)} | {case_status.upper()} |\n"
        
        markdown += "\n"
        
        # Add failure/error details if any
        for testcase in suite.get('testcase', []):
            case_name = testcase.get('name', 'Unknown')
            case_status = testcase.get('status', 'unknown')
            
            if case_status == "failed" and "failure" in testcase:
                failure = testcase["failure"]
                markdown += f"""### Failure Details: {case_name}

```
Type: {failure.get('type', 'Unknown')}
Message: {failure.get('message', 'No message')}
{failure.get('text', 'No details')}
```

"""
            elif case_status == "error" and "error" in testcase:
                error = testcase["error"]
                markdown += f"""### Error Details: {case_name}

```
Type: {error.get('type', 'Unknown')}
Message: {error.get('message', 'No message')}
{error.get('text', 'No details')}
```

"""
    
    # Add footer
    markdown += f"""
---

*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*  
"""
    
    return markdown

def main():
    if len(sys.argv) != 4:
        print("Usage: python generate-markdown-report.py <input_json_file> <output_markdown_file> <package_url>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    package_url = sys.argv[3]
    
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        sys.exit(1)
    
    print(f"Generating markdown report from {input_file}")
    
    try:
        # Read JSON data
        with open(input_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Generate markdown
        markdown_content = generate_markdown_report(json_data, package_url)
        
        # Write markdown file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Successfully generated markdown report: {output_file}")
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating markdown report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 