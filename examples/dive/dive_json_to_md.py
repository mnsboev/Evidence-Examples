import json
import sys

def generate_markdown_report(dive_output):
    image_info = dive_output.get('image', {})

    size_bytes = image_info.get('sizeBytes', 'N/A')
    inefficient_bytes = image_info.get('inefficientBytes', 'N/A')
    efficiency_score = image_info.get('efficiencyScore', 'N/A')

    markdown_report = f"""
## Dive Analysis Report

**Image Size:** `{size_bytes} bytes`

**Inefficient Bytes:** `{inefficient_bytes} bytes`

**Efficiency Score:** `{efficiency_score}`

---
### File References
This section lists the files contributing to inefficiencies in the image.

| File Path | Count | Size (Bytes) |
| :-------- | :---- | :----------- |
"""

    file_references = image_info.get('fileReference', [])
    for file_ref in file_references:
        file_path = file_ref.get('file', 'N/A')
        count = file_ref.get('count', 'N/A')
        size = file_ref.get('sizeBytes', 'N/A')
        markdown_report += f"| {file_path} | {count} | {size} |\n"

    markdown_report += "\n---"
    return markdown_report

def main(input_file):
    # Read JSON input from a file
    with open(input_file, 'r') as file:
        dive_output = json.load(file)

    # Generate the Markdown report
    markdown_report = generate_markdown_report(dive_output)

    # Define the output file path
    output_file = 'dive-analysis.md'

    # Write the Markdown report to a file
    with open(output_file, 'w') as file:
        file.write(markdown_report)

    print(f"Markdown report generated successfully and saved to {output_file}!")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python dive_json_to_md.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)
