import json
import sys

def generate_markdown_report(report):
    source_name = report.get('SourceName', 'N/A')
    detector_name = report.get('DetectorName', None)
    if not detector_name:
        return None  # Skip entries without 'DetectorName'

    detector_description = report.get('DetectorDescription', 'N/A')
    verified = report.get('Verified', False)
    raw = report.get('Raw', 'N/A')
    redacted = report.get('Redacted', 'N/A')

    extra_data = report.get('ExtraData', {})
    account = extra_data.get('account', 'N/A')
    arn = extra_data.get('arn', 'N/A')
    is_canary = extra_data.get('is_canary', 'N/A')
    message = extra_data.get('message', 'N/A')
    resource_type = extra_data.get('resource_type', 'N/A')

    markdown_report = f"""
## Report Overview: {source_name}

**Source Name:** `{source_name}`

**Detector Name:** `{detector_name}`

**Detector Description:** `{detector_description}`

**Verified:** `{verified}`

**Raw Data:** `{raw}`

**Redacted Data:** `{redacted}`

---
### Extra Data
| Key           | Value         |
| :------------ | :------------ |
| Account       | {account}     |
| ARN           | {arn}         |
| Is Canary     | {is_canary}   |
| Message       | {message}     |
| Resource Type | {resource_type} |
---
"""
    return markdown_report

def main(input_file):
    # Read JSONL input from a file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    markdown_reports = []
    for line in lines:
        report = json.loads(line)
        markdown_report = generate_markdown_report(report)
        if markdown_report:
            markdown_reports.append(markdown_report)

    # Define the output file path
    output_file = 'report_readme.md'

    # Write the Markdown reports to a file
    with open(output_file, 'w') as file:
        file.write("\n\n".join(markdown_reports))

    print(f"Markdown README generated successfully and saved to {output_file}!")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python process_trufflehog_results.py <report_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)
