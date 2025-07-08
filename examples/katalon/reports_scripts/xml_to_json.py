#!/usr/bin/env python3
"""
Convert JUnit XML report to JSON format
Usage: python xml_to_json.py <input_xml_file> <output_json_file>
"""

import xml.etree.ElementTree as ET
import json
import sys
import os

def parse_junit_xml(xml_file):
    """Parse JUnit XML and convert to JSON structure"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Handle different JUnit XML namespaces
        namespaces = {
            'junit': 'https://maven.apache.org/plugins/maven-surefire-plugin/FailsafeReport/1.0.0',
            'default': 'https://maven.apache.org/plugins/maven-surefire-plugin/FailsafeReport/1.0.0'
        }
        
        # Try to find testsuites element
        testsuites = root.find('.//testsuites') or root.find('.//testsuite')
        
        if testsuites is None:
            # If no testsuites found, try without namespace
            testsuites = root.find('testsuites') or root.find('testsuite')
        
        if testsuites is None:
            # If still not found, use root as testsuites
            testsuites = root
        
        result = {
            'testsuites': {
                'name': testsuites.get('name', 'Unknown'),
                'tests': int(testsuites.get('tests', 0)),
                'failures': int(testsuites.get('failures', 0)),
                'errors': int(testsuites.get('errors', 0)),
                'skipped': int(testsuites.get('skipped', 0)),
                'time': float(testsuites.get('time', 0)),
                'testsuite': []
            }
        }
        
        # Find all testsuite elements
        for testsuite in testsuites.findall('.//testsuite') or [testsuites]:
            suite_data = {
                'name': testsuite.get('name', 'Unknown'),
                'tests': int(testsuite.get('tests', 0)),
                'failures': int(testsuite.get('failures', 0)),
                'errors': int(testsuite.get('errors', 0)),
                'skipped': int(testsuite.get('skipped', 0)),
                'time': float(testsuite.get('time', 0)),
                'testcase': []
            }
            
            # Find all testcase elements
            for testcase in testsuite.findall('.//testcase') or []:
                case_data = {
                    'name': testcase.get('name', 'Unknown'),
                    'classname': testcase.get('classname', 'Unknown'),
                    'time': float(testcase.get('time', 0)),
                    'status': 'passed'
                }
                
                # Check for failures, errors, or skipped
                failure = testcase.find('failure')
                error = testcase.find('error')
                skipped = testcase.find('skipped')
                
                if failure is not None:
                    case_data['status'] = 'failed'
                    case_data['failure'] = {
                        'message': failure.get('message', ''),
                        'type': failure.get('type', ''),
                        'text': failure.text or ''
                    }
                elif error is not None:
                    case_data['status'] = 'error'
                    case_data['error'] = {
                        'message': error.get('message', ''),
                        'type': error.get('type', ''),
                        'text': error.text or ''
                    }
                elif skipped is not None:
                    case_data['status'] = 'skipped'
                    case_data['skipped'] = {
                        'message': skipped.get('message', ''),
                        'text': skipped.text or ''
                    }
                
                suite_data['testcase'].append(case_data)
            
            result['testsuites']['testsuite'].append(suite_data)
        
        return result
        
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return None
    except Exception as e:
        print(f"Error processing XML file: {e}")
        return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python xml_to_json.py <input_xml_file> <output_json_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        sys.exit(1)
    
    print(f"Converting {input_file} to {output_file}")
    
    # Parse XML and convert to JSON
    json_data = parse_junit_xml(input_file)
    
    if json_data is None:
        print("Failed to parse XML file")
        sys.exit(1)
    
    # Write JSON to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully converted XML to JSON: {output_file}")
    except Exception as e:
        print(f"Error writing JSON file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 