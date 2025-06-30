import json

def format_digests(digests):
    if not isinstance(digests, dict):
        return ""
    sha1 = digests.get("sha1")
    sha256 = digests.get("sha256")
    if sha1 and sha256:
        return f"sha1: {sha1}, sha256: {sha256}"
    elif sha1:
        return f"sha1: {sha1}"
    elif sha256:
        return f"sha256: {sha256}"
    return ""

def main():
    with open('decoded-payload.json', 'r') as f:
        data = json.load(f)

    lines = []
    lines.append("# SLSA Provenance Statement")
    lines.append(f"- **predicateType**: `{data.get('predicateType', '')}`")
    lines.append(f"- **_type**: `{data.get('_type', '')}`\n")

    # Subject
    lines.append("## Subject")
    for subj in data.get("subject", []):
        lines.append(f"- **Name**: `{subj.get('name', '')}`")
        digests = format_digests(subj.get("digests", {}))
        if digests:
            lines.append(f"- **Digests**: `{digests}`")
    lines.append("")

    # Predicate
    pred = data.get("predicate", {})
    lines.append("## Predicate\n")
    lines.append("### Build Type")
    lines.append(f"- `{pred.get('buildType', '')}`\n")

    lines.append("### Builder")
    builder = pred.get("builder", {})
    lines.append(f"- **ID**: `{builder.get('id', '')}`\n")

    # Invocation
    invocation = pred.get("invocation", {})
    lines.append("### Invocation\n")
    config = invocation.get("configSource", {})
    lines.append("#### Config Source")
    lines.append(f"- **URI**: `{config.get('uri', '')}`")
    lines.append(f"- **Entry Point**: `{config.get('entryPoint', '')}`")
    digests = format_digests(config.get("digests", {}))
    if digests:
        lines.append(f"- **Digests**: `{digests}`")
    lines.append("")

    env = invocation.get("environment", {})
    lines.append("#### Environment")
    lines.append(f"- **Build URL**: `{env.get('build_url', '')}`")
    lines.append(f"- **Job URL**: `{env.get('job_url', '')}`")
    lines.append(f"- **Node Name**: `{env.get('node_name', '')}`\n")

    # Metadata
    metadata = pred.get("metadata", {})
    lines.append("### Metadata")
    lines.append(f"- **Build Invocation ID**: `{metadata.get('buildInvocationId', '')}`")
    lines.append(f"- **Build Started On**: `{metadata.get('buildStartedOn', '')}`")
    lines.append(f"- **Build Finished On**: `{metadata.get('buildFinishedOn', '')}`")
    lines.append(f"- **Reproducible**: `{str(metadata.get('reproducible', ''))}`\n")

    completeness = metadata.get("completeness", {})
    lines.append("#### Completeness")
    lines.append(f"- **Parameters Complete**: `{str(completeness.get('parametersComplete', ''))}`")
    lines.append(f"- **Environment Complete**: `{str(completeness.get('environmentComplete', ''))}`")
    lines.append(f"- **Materials Complete**: `{str(completeness.get('materialsComplete', ''))}`\n")

    # Materials
    lines.append("### Materials")
    for mat in pred.get("materials", []):
        lines.append(f"- **URI**: `{mat.get('uri', '')}`")
        digests = format_digests(mat.get("digests", {}))
        if digests:
            lines.append(f"- **Digests**: `{digests}`")

    with open('JenkinsSLSA.md', 'w') as f:
        f.write('\n'.join(lines))

if __name__ == "__main__":
    main()
