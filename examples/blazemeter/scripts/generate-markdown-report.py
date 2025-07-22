import json
import os
import sys
from datetime import datetime

def generate_markdown_report(json_data, artifact_name, test_id):
    markdown_output = "# BlazeMeter Performance Test Report\n\n"
    markdown_output += f"**Artifact Name:** {artifact_name}  \n"
    markdown_output += f"**Test ID:** {test_id}  \n"
    markdown_output += f"**Execution Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  \n\n"
    
    summary_data = None
    if json_data and 'result' in json_data and isinstance(json_data['result'], list):
        for item in json_data['result']:
            if item.get('labelName') == 'ALL':
                summary_data = item
                break
        if not summary_data and json_data['result']:
            summary_data = json_data['result'][0] 

    if not summary_data:
        markdown_output += "## No Performance Summary Data Found\n\n"
        markdown_output += "The aggregate report did not contain expected summary data.\n"
        return markdown_output

    markdown_output += "## Test Summary\n\n"
    markdown_output += "| Metric                | Value      |\n"
    markdown_output += "| :-------------------- | :--------- |\n"
    markdown_output += f"| **Total Samples** | {summary_data.get('samples', 'N/A')} |\n"
    markdown_output += f"| **Avg Response Time** | {summary_data.get('avgResponseTime', 'N/A'):.2f} ms |\n"
    markdown_output += f"| **Median Response** | {summary_data.get('medianResponseTime', 'N/A')} ms |\n"
    markdown_output += f"| **90th Percentile** | {summary_data.get('90line', 'N/A')} ms |\n"
    markdown_output += f"| **95th Percentile** | {summary_data.get('95line', 'N/A')} ms |\n"
    markdown_output += f"| **99th Percentile** | {summary_data.get('99line', 'N/A')} ms |\n"
    markdown_output += f"| **Min Response Time** | {summary_data.get('minResponseTime', 'N/A')} ms |\n"
    markdown_output += f"| **Max Response Time** | {summary_data.get('maxResponseTime', 'N/A')} ms |\n"
    markdown_output += f"| **Avg Latency** | {summary_data.get('avgLatency', 'N/A'):.2f} ms |\n"
    markdown_output += f"| **Std Deviation** | {summary_data.get('stDev', 'N/A'):.2f} |\n"
    markdown_output += f"| **Total Duration** | {summary_data.get('duration', 'N/A')} seconds |\n"
    markdown_output += f"| **Avg Throughput** | {summary_data.get('avgThroughput', 'N/A'):.2f} req/s |\n"
    markdown_output += f"| **Error Count** | {summary_data.get('errorsCount', 'N/A')} |\n"
    markdown_output += f"| **Error Rate** | {summary_data.get('errorsRate', 'N/A'):.2f}% |\n"
    markdown_output += f"| **Concurrency** | {summary_data.get('concurrency', 'N/A')} |\n"
    markdown_output += "\n"

    return markdown_output

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate-markdown-report.py <path_to_blazemeter_report.json> <artifact_name> <test_id>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    artifact_name = sys.argv[2]
    test_id = sys.argv[3]

    if not os.path.exists(json_file_path):
        print(f"Error: File not found at {json_file_path}")
        sys.exit(1)

    try:
        with open(json_file_path, 'r') as f:
            blazemeter_report_json = json.load(f)
        markdown_report = generate_markdown_report(blazemeter_report_json, artifact_name, test_id)
        print(markdown_report)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file {json_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
