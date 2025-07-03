# Jenkins SLSA Evidence Example

This project demonstrates how to automate Maven builds, generate SLSA provenance, convert it to Markdown, and attach the signed provenance evidence to the Maven package in JFrog Artifactory using Jenkins Pipeline and JFrog CLI.

## Overview

The pipeline builds a Maven project, generates SLSA provenance, converts the provenance JSON to Markdown, publishes the artifact to Artifactory, and attaches the signed provenance as evidence to the Maven package. This enables traceability and compliance for your Java artifacts in CI/CD.

## Prerequisites

- JFrog CLI
- Artifactory configured as a Maven repository
- The following Jenkins credentials:
    - `ARTIFACTORY_URL` (Artifactory URL)
    - `ACCESS_TOKEN_ID` (Artifactory access token)
    - `PRIVATE_PEM` (Private key for signing evidence)
    - `KEY_ALIAS` (Key alias for signing evidence)
    - `github` (GitHub credentials for source checkout)

## Environment Variables Used

- `PACKAGE_REPO_NAME` - Maven repository name in Artifactory
- `PACKAGE_NAME` - Maven artifactId (extracted from pom.xml)
- `PACKAGE_VERSION` - Maven version (extracted from pom.xml)
- `PREDICATE_FILE_NAME` - Path to SLSA provenance JSON file
- `PREDICATE_TYPE` - Predicate type URL for SLSA
- `MARKDOWN_FILE_NAME` - Path to the generated Markdown file from provenance

## Pipeline Stages

1. **Checkout**
    - Clones the source code from GitHub.
2. **JFrog CLI Configuration**
    - Configures JFrog CLI with Artifactory credentials.
3. **Build and Publish**
    - Builds the Maven project and publishes artifacts to Artifactory.
    - Extracts artifactId and version for evidence attachment.
4. **Provenance Generation and Evidence Attachment**
    - Generates SLSA provenance.
    - Converts the provenance JSON to Markdown.
    - Attaches the signed provenance (JSON and Markdown) as evidence to the Maven package in Artifactory.

## Example Usage

Trigger the pipeline in Jenkins. The pipeline will:

- Build and publish the Maven artifact
- Generate and convert the SLSA provenance
- Attach the provenance as evidence

## Key Commands Used

- **Configure JFrog CLI:**
  ```bash
  jf c add jenkins-slsa-evidence --url=https://evidencetrial.jfrog.io --access-token=$ACCESS_TOKEN
  ```
- **Build and Publish Maven Artifact:**
  ```bash
  jf mvn clean install
  ```
- **Extract Maven Coordinates:**
  ```bash
  mvn help:evaluate -Dexpression=project.artifactId -q -DforceStdout
  mvn help:evaluate -Dexpression=project.version -q -DforceStdout
  ```
- **Convert Provenance JSON to Markdown:**
  ```bash
  python3 json-to-md.py
  ```
- **Attach Evidence:**
  ```bash
  jf evd create --package-name="$PACKAGE_NAME" --package-version="$PACKAGE_VERSION" --package-repo-name="$PACKAGE_REPO_NAME" --key="$PRIVATE_PEM" --key-alias="$KEY_ALIAS" --predicate="$PREDICATE_FILE_NAME" --predicate-type="$PREDICATE_TYPE" --markdown="$MARKDOWN_FILE_NAME"
  ```

## Limitation

**Note:** The current pipeline and evidence attachment process expects a single Maven artifact (JAR) is produced per build. It does **not** support multiple subjects or multiple JARs in a single pipeline execution. This is a known limitation and should be considered when working with this example.

## References

- [SLSA Provenance](https://slsa.dev/spec/v1.1/provenance)
- [Jenkins SLSA Plugin](https://plugins.jenkins.io/slsa/)
- [JFrog Evidence Management](https://jfrog.com/help/r/jfrog-artifactory-documentation/evidence-management)
- [JFrog CLI Documentation](https://jfrog.com/getcli/)
- [How to use JFrog CLI in Jenkins using JFrog Plugin](https://jfrog.com/help/r/artifactory-how-to-use-jfrog-cli-in-jenkins-using-jfrog-plugin/artifactory-how-to-use-jfrog-cli-in-jenkins-using-jfrog-plugin)