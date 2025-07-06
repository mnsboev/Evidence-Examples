import sys
import json

def json_to_md(json_path, md_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    spdx_version = data.get('spdxVersion', 'N/A')
    data_license = data.get('dataLicense', 'N/A')
    document_namespace = data.get('documentNamespace', 'N/A')
    creation_info = data.get('creationInfo', {})
    packages = data.get('packages', [])
    files = data.get('files', [])

    with open(md_path, 'w') as f:
        f.write(f"# SBOM Summary\n\n")
        f.write(f"**SPDX Version:** {spdx_version}\n\n")
        f.write(f"**Data License:** {data_license}\n\n")
        f.write(f"**Document Namespace:** {document_namespace}\n\n")

        f.write(f"## Creation Info\n")
        f.write(f"- License List Version: {creation_info.get('licenseListVersion', 'N/A')}\n")
        f.write(f"- Created: {creation_info.get('created', 'N/A')}\n")
        creators = creation_info.get('creators', [])
        if creators:
            f.write(f"- Creators:\n")
            for creator in creators:
                f.write(f"  - {creator}\n")
        else:
            f.write("- No creators found.\n")

        f.write(f"\n## Packages\n")
        if packages:
            f.write(f"| Index | Name | Version | Supplier |\n")
            f.write(f"|---|---|---|---|\n")
            for idx, package in enumerate(packages, start=1):
                name = package.get('name', 'N/A').replace('|', '\\|')
                version = package.get('versionInfo', 'N/A').replace('|', '\\|')
                supplier = package.get('supplier', 'N/A')
                if isinstance(supplier, dict):
                    supplier = supplier.get('name', 'N/A')
                supplier = supplier.replace('|', '\\|')
                f.write(f"| {idx} | {name} | {version} | {supplier} |\n")
        else:
            f.write("No packages found.\n")

        print(f"Markdown file generated at: {md_path}")

if __name__ == "__main__":
    input_json = sys.argv[1]
    output_md = sys.argv[2]
    json_to_md(input_json, output_md)