# Semgrep Security Scan Evidence Example

This repository provides a working example of a GitHub Actions workflow that automates Static Application Security Testing (SAST) on a JavaScript project using Semgrep. It then attaches the resulting SARIF report as signed, verifiable evidence to the package in JFrog Artifactory.

This workflow is an excellent example of a "shift-left" security practice, providing fast, customizable code analysis and creating an auditable security record for every build.

## Overview

The workflow scans JavaScript code with Semgrep for security issues, publishes the package to Artifactory, and attaches the Semgrep scan results as evidence to the package. This enables traceability and compliance for security scanning in your CI/CD pipeline.

### **Key Features**

* **Containerized Scanning**: Runs the entire job inside the official `semgrep/semgrep` Docker container for a consistent and secure environment.  
* **Automated SAST**: Leverages the powerful and fast Semgrep engine to scan source code for security vulnerabilities, bugs, and policy violations.  
* **SARIF Output**: Generates an industry-standard SARIF file detailing the scan's findings.  
* **Optional Markdown Summary**: Includes a helper script to generate a human-readable Markdown report from the SARIF data.  
* **Signed Evidence Attachment**: Attaches the SARIF report as a predicate to the corresponding npm package in Artifactory, cryptographically signing it for integrity.

## Prerequisites

- JFrog CLI 2.65.0 or above (installed automatically in the workflow)
- Artifactory configured as a repository
- The following GitHub repository variables:
    - `ARTIFACTORY_URL` (Artifactory base URL)
    - `EVIDENCE_KEY_ALIAS` (Key alias for signing evidence)
- The following GitHub repository secrets:
    - `ARTIFACTORY_ACCESS_TOKEN` (Artifactory access token)
    - `PRIVATE_KEY` (Private key for signing evidence)

## Environment Variables Used

- `ATTACH_OPTIONAL_CUSTOM_MARKDOWN_TO_EVIDENCE` - Whether to attach a custom markdown report to the evidence

## Workflow

```mermaid
graph TD
    A[Workflow Dispatch Trigger] --> B[Setup JFrog CLI]
    B --> C[Checkout Repository]
    C --> D[Publish JavaScript Package to Artifactory]
    D --> E[Run Semgrep Security Scan]
    E --> F{Attach Optional Custom Markdown Report?}
    F -->|Yes| G[Generate Custom Markdown Report]
    F -->|No| H[Skip Markdown Report]
    G --> I[Attach Evidence Using JFrog CLI]
    H --> I[Attach Evidence Using JFrog CLI]
```    

## Example Usage

You can trigger the workflow manually from the GitHub Actions tab. The workflow will:

- Scan the JavaScript code
- Publish the package to Artifactory
- Attach the Semgrep scan results as evidence

## Key Commands Used

- **Publish JavaScript Package:**
  The workflow begins by configuring `npm` to use Artifactory via the JFrog CLI. It then publishes the JavaScript package located in the `examples/semgrep/js` directory.
  
  ```bash
  jf npm-config --repo-resolve=javascript-remote --repo-deploy=javascript-local \
    --server-id-deploy=setup-jfrog-cli-server \
    --server-id-resolve=setup-jfrog-cli-server
  jf npm publish --build-name=js-semgrep-sample-build --build-number=${{ github.run_number }}
  jf rt bp js-semgrep-sample-build ${{ github.run_number }}
  ```
- **Run Semgrep Scan:**
  This step runs the `semgrep scan` command directly against the source code. It uses the `--config auto` flag to automatically detect the language and apply a curated set of rules. The results are saved as a `semgrep-results.sarif` file.
  
  ```bash
  semgrep scan -q --sarif --config auto ./examples/semgrep/js > semgrep-results.sarif
  ```
- **Attach Evidence:**
  This final step uses `jf evd create` to attach the scan results to the npm package that was published earlier. The SARIF file serves as the official, machine-readable predicate, while the optional Markdown report provides a summary for easy viewing in the Artifactory UI.
  
  ```bash
  jf evd create \
    --package-name js-semgrep-sample-build \
    --package-version "0.0.1" \
    --package-repo-name javascript-local \
    --key "${{ secrets.PRIVATE_KEY }}" \
    --key-alias "${{ vars.EVIDENCE_KEY_ALIAS }}" \
    --predicate "results-javascript/javascript.sarif" \
    --predicate-type "http://semgrep.com/security-scan/v1" \
    ${{ env.ATTACH_OPTIONAL_CUSTOM_MARKDOWN_TO_EVIDENCE == 'true' && '--markdown "results-javascript/javascript-report.md"' || '' }}
  ```

## References

- [Semgrep Documentation](https://semgrep.dev/docs/)
- [JFrog Evidence Management](https://jfrog.com/help/r/jfrog-artifactory-documentation/evidence-management)
- [JFrog CLI Documentation](https://jfrog.com/getcli/)
