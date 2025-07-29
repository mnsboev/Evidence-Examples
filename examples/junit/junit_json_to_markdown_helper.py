import json
import sys
from datetime import datetime


def calculate_test_statistics(test_report):
    """Calculate test statistics from the test report"""
    summary = test_report.get('testReport', {}).get('summary', {})
    
    total_tests = summary.get('totalTests', 0)
    total_failures = summary.get('totalFailures', 0)
    total_errors = summary.get('totalErrors', 0)
    total_skipped = summary.get('totalSkipped', 0)
    success_rate = summary.get('successRate', 0)
    total_time = summary.get('totalTime', 0)
    
    return {
        'total_tests': total_tests,
        'total_failures': total_failures,
        'total_errors': total_errors,
        'total_skipped': total_skipped,
        'success_rate': success_rate,
        'total_time': total_time
    }


def get_test_status_color(status):
    """Get color indicator for test status"""
    if status == 'passed':
        return 'PASS'
    elif status == 'failed':
        return 'FAIL'
    elif status == 'skipped':
        return 'SKIP'
    else:
        return 'UNKNOWN'


def group_tests_by_class(test_suites):
    """Group tests by their class name"""
    grouped_tests = {}
    
    for test in test_suites:
        class_name = test.get('class', 'Unknown')
        if class_name not in grouped_tests:
            grouped_tests[class_name] = []
        grouped_tests[class_name].append(test)
    
    return grouped_tests


def generate_markdown_report(junit_output):
    """Generate a comprehensive markdown report from JUnit test results"""
    
    # Extract test report data
    test_report = junit_output.get('testReport', {})
    summary = test_report.get('summary', {})
    test_suites = test_report.get('testSuites', [])
    
    # Calculate statistics
    stats = calculate_test_statistics(junit_output)
    
    # Get timestamp
    timestamp = summary.get('timestamp', datetime.now().isoformat())
    
    # Generate the markdown report
    markdown_report = f"""# JUnit Test Results Report

**Generated:** `{timestamp}`

**Total Tests:** `{stats['total_tests']}`

**Total Failures:** `{stats['total_failures']}`

**Total Errors:** `{stats['total_errors']}`

**Total Skipped:** `{stats['total_skipped']}`

**Success Rate:** `{stats['success_rate']}%`

**Total Execution Time:** `{stats['total_time']}s`

---

## Test Summary

| Metric | Count |
| :----- | :---- |
| Total Tests | {stats['total_tests']} |
| Passed | {stats['total_tests'] - stats['total_failures'] - stats['total_errors']} |
| Failed | {stats['total_failures']} |
| Errors | {stats['total_errors']} |
| Skipped | {stats['total_skipped']} |
| Success Rate | {stats['success_rate']}% |

---

## Test Results by Class

"""
    
    # Group tests by class
    grouped_tests = group_tests_by_class(test_suites)
    
    for class_name, tests in grouped_tests.items():
        markdown_report += f"### {class_name}\n\n"
        markdown_report += "| Test Name | Status | Execution Time |\n"
        markdown_report += "| :-------- | :----- | :------------- |\n"
        
        for test in tests:
            test_name = test.get('name', 'Unknown')
            status = test.get('status', 'unknown')
            time = test.get('time', '0')
            status_icon = get_test_status_color(status)
            
            markdown_report += f"| {test_name} | {status_icon} {status} | {time}s |\n"
        
        markdown_report += "\n"
    
    # Add overall status summary
    if stats['success_rate'] == 100:
        overall_status = "All tests passed successfully!"
    elif stats['success_rate'] >= 80:
        overall_status = "Most tests passed with some failures."
    else:
        overall_status = "Significant test failures detected."
    
    markdown_report += f"""
---

## Overall Status

{overall_status}

**Recommendations:**
"""
    
    if stats['total_failures'] > 0 or stats['total_errors'] > 0:
        markdown_report += f"""
- Review and fix {stats['total_failures'] + stats['total_errors']} failing tests
- Investigate test failures in the affected classes
- Consider adding more test coverage for failing scenarios
"""
    
    if stats['total_skipped'] > 0:
        markdown_report += f"""
- Review {stats['total_skipped']} skipped tests to ensure they are intentionally skipped
- Consider enabling skipped tests if conditions are met
"""
    
    if stats['success_rate'] == 100:
        markdown_report += """
- All tests are passing! Consider adding more test coverage for edge cases
- Review test execution time for optimization opportunities
"""
    
    markdown_report += "\n---\n"
    return markdown_report


def main(input_file):
    """Main function to process JUnit JSON and generate markdown report"""
    try:
        # Read JSON input from a file
        with open(input_file, 'r') as file:
            junit_output = json.load(file)

        # Generate the Markdown report
        markdown_report = generate_markdown_report(junit_output)

        # Define the output file path
        output_file = 'junit-results.md'

        # Write the Markdown report to a file
        with open(output_file, 'w') as file:
            file.write(markdown_report)

        print(f"Markdown report generated successfully and saved to {output_file}!")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{input_file}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python junit_json_to_markdown_helper.py <input_file>")
        print("Example: python junit_json_to_markdown_helper.py target/consolidated-test-report.json")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file) 