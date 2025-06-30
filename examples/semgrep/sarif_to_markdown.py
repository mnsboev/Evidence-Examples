import json
from datetime import datetime

def convert_sarif_to_markdown(input_file, output_file):
    """
    Converts a SARIF file to a Markdown file with tabular formatting for results.

    Args:
        input_file (str): Path to the input SARIF file.
        output_file (str): Path to the output Markdown file.
    """
    with open(input_file, 'r') as f:
        sarif_data = json.load(f)

    markdown_lines = ["# SARIF Analysis Report", ""]

    # Add metadata
    markdown_lines.append(f"**Generated on**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    markdown_lines.append("\n---\n")

    # Process runs
    for run in sarif_data.get('runs', []):
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
        print("Usage: python sarif_to_markdown.py <input_sarif_file> <output_markdown_file>")
        sys.exit(1)

    input_sarif = sys.argv[1]
    output_md = sys.argv[2]
    convert_sarif_to_markdown(input_sarif, output_md)
