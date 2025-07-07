import json
from datetime import datetime

def convert_report_to_markdown(input_file, output_file):
    with open(input_file, 'r') as f:
        report_data = json.load(f)

    markdown_lines = ["# Report Analysis", ""]

    # Add metadata
    markdown_lines.append(f"**Generated on**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    markdown_lines.append("\n---\n")

    # Process runs
    for run in report_data.get('runs', []):
        tool_name = run.get('tool', {}).get('driver', {}).get('name', 'Unknown Tool')
        tool_version = run.get('tool', {}).get('driver', {}).get('semanticVersion', 'Unknown Version')
        markdown_lines.append(f"## Tool: {tool_name} (Version: {tool_version})")

        # Add results in tabular format
        markdown_lines.append("\n| Rule ID | Message |")
        markdown_lines.append("|---------|---------|")
        for result in run.get('results', []):
            rule_id = result.get('ruleId', 'Unknown Rule')
            message = result.get('message', {}).get('text', 'No message provided').replace("\n", "<br>")
            markdown_lines.append(f"| {rule_id} | {message} |")

    # Write to Markdown file
    with open(output_file, 'w') as f:
        f.write('\n'.join(markdown_lines))

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python report_to_markdown.py <input_json_file> <output_markdown_file>")
        sys.exit(1)

    input_json = sys.argv[1]
    output_md = sys.argv[2]
    convert_report_to_markdown(input_json, output_md)