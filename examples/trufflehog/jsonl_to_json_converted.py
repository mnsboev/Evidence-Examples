import json

# Input and output file paths
input_file = "trufflehog-results.jsonl"
output_file = "trufflehog.json"

# Read the JSONL file and convert it to a list of JSON objects
with open(input_file, "r") as infile:
    data = [json.loads(line) for line in infile]

# Wrap the data in a dictionary with the key "data"
output_data = {"data": data}

# Write the output to a JSON file with proper formatting
with open(output_file, "w") as outfile:
    outfile.write('{\n  "data": [\n')
    for i, item in enumerate(data):
        json.dump(item, outfile, indent=4)
        if i < len(data) - 1:
            outfile.write(',\n')
    outfile.write('\n  ]\n}')
    
print(f"Converted {input_file} to {output_file}")