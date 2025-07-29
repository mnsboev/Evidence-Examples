# JIRA Helper - Technical Documentation

This directory contains the technical implementation of the JIRA evidence gathering tool. The `main.go` application is a consolidated Go program that handles all JIRA-related operations including git commit extraction, JIRA API integration, and evidence generation.

## Quick Start

```bash
# Build the application
go build -o main main.go

# Basic usage - extract JIRA IDs and fetch details
./main <start_commit>

# Direct JIRA ticket processing
./main EV-123 EV-456 EV-789

# Extract only mode
./main --extract-only <start_commit>

# Get help
./main --help
```

## Command Line Interface

### Primary Mode: Git-based Evidence Gathering
```bash
./main [OPTIONS] <start_commit>
```

**Arguments:**
- `start_commit`: Starting commit hash (excluded from evidence filter)

**Options:**
- `-r, --regex PATTERN`: JIRA ID regex pattern (default: `[A-Z]+-[0-9]+`)
- `-o, --output FILE`: Output file for JIRA data (default: `transformed_jira_data.json`)
- `--extract-only`: Only extract JIRA IDs, don't fetch details
- `-h, --help`: Display help message

### Direct Mode: Process Specific JIRA Tickets
```bash
./main <jira_id1> [jira_id2] [jira_id3] ...
```

### Legacy Mode: Backward Compatibility
```bash
./main --extract-from-git <start_commit> <jira_id_regex>
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `JIRA_API_TOKEN` | JIRA API token for authentication | Yes | - |
| `JIRA_URL` | JIRA instance URL | Yes | - |
| `JIRA_USERNAME` | JIRA username for authentication | Yes | - |
| `JIRA_ID_REGEX` | JIRA ID regex pattern | No | `[A-Z]+-[0-9]+` |
| `OUTPUT_FILE` | Output file path | No | `transformed_jira_data.json` |
| `ATTACH_OPTIONAL_CUSTOM_MARKDOWN_TO_EVIDENCE` | Generate markdown report | No | `false` |

## Usage Examples

### Basic Evidence Gathering
```bash
export JIRA_API_TOKEN="your_token"
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your_email@domain.com"

./main abc123def456
```

### Custom Configuration
```bash
./main -r 'EV-\d+' -o my_results.json abc123def456
```

### Extract Only (for debugging)
```bash
./main --extract-only abc123def456
```

### Direct Ticket Processing
```bash
./main EV-123 EV-456 EV-789
```

## Technical Architecture

### Core Functions

#### Git Operations
- `getBranchInfo()`: Extracts current branch, commit hash, and JIRA ID from latest commit
- `validateHEAD()`: Validates that HEAD commit exists in repository
- `validateCommit()`: Validates commit existence in repository
- `extractJiraIDs()`: Extracts JIRA IDs from commit messages using regex
- `checkGitRepository()`: Validates git repository state

#### JIRA API Integration
- `fetchJiraDetails()`: Creates JIRA client and fetches ticket details
- `fetchJiraDetailsWithClient()`: Core JIRA data fetching logic
- `getDescription()`: Extracts description from JIRA description field
- `getAssignee()`: Handles assignee information
- `getTimeAsString()`: Converts JIRA time fields to strings

#### File Operations
- `writeToFile()`: Writes data to file with directory creation
- `displayUsage()`: Shows command-line help

#### Markdown Generation
- `formatWorkflow()`: Formats workflow transitions into readable strings
- `escapeMarkdown()`: Escapes special characters for markdown tables
- `generateMarkdownContent()`: Generates markdown content from JIRA data
- `generateMarkdownReport()`: Creates and writes markdown report files

### Data Structures

```go
type TransitionCheckResponse struct {
    TicketRequested []string               `json:"ticketRequested"`
    Tasks           []JiraTransitionResult `json:"tasks"`
}

type JiraTransitionResult struct {
    Key         string       `json:"key"`
    Status      string       `json:"status"`
    Description string       `json:"description"`
    Type        string       `json:"type"`
    Project     string       `json:"project"`
    Created     string       `json:"created"`
    Updated     string       `json:"updated"`
    Assignee    *string      `json:"assignee"`
    Reporter    string       `json:"reporter"`
    Priority    string       `json:"priority"`
    Transitions []Transition `json:"transitions"`
}

type Transition struct {
    FromStatus     string `json:"from_status"`
    ToStatus       string `json:"to_status"`
    Author         string `json:"author"`
    AuthorEmail    string `json:"author_user_name"`
    TransitionTime string `json:"transition_time"`
}
```

## Building and Development

### Prerequisites
- Go 1.21 or later
- Git (for git operations)
- JIRA Cloud API access

### Build Commands
```bash
# Standard build
go build -o main main.go

# Using build script
./build.sh

# Cross-platform build
GOOS=linux GOARCH=amd64 go build -o main main.go
```

### Dependencies
```go
import (
    "context"
    "encoding/json"
    "flag"
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
    "reflect"
    "regexp"
    "strings"
    "time"

    jira "github.com/andygrunwald/go-jira/v2/cloud"
)
```

### Testing
```bash
# Run tests
go test ./...

# Test specific functionality
go test -v -run TestExtractJiraIDs
```

## Error Handling

### Git Errors
- Repository validation failures
- HEAD commit existence checks
- Commit existence checks
- Branch information extraction errors

### JIRA API Errors
- Authentication failures
- Network connectivity issues
- Invalid ticket IDs
- API rate limiting

### File System Errors
- Output file creation failures
- Directory permission issues
- JSON marshaling errors

### Error Response Format
```json
{
  "ticketRequested": ["EV-123"],
  "tasks": [
    {
      "key": "EV-123",
      "status": "Error",
      "description": "Error: Could not retrieve issue",
      "type": "Error",
      "project": "",
      "created": "",
      "updated": "",
      "assignee": null,
      "reporter": "",
      "priority": "",
      "transitions": []
    }
  ]
}
```

## Integration with CI/CD

### GitHub Actions
```yaml
- name: Fetch details from jira
  run: |
    cd examples/jira/helper
    ./main "${{ github.event.inputs.start_commit }}"
    cd -
```

### Docker Integration
```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o main main.go

FROM alpine:latest
RUN apk --no-cache add git
COPY --from=builder /app/main /main
ENTRYPOINT ["/main"]
```

## Performance Considerations

### Git Operations
- Uses `git log` with specific format for efficiency
- Validates commits before processing
- Handles large commit ranges gracefully

### JIRA API
- Processes tickets sequentially to avoid rate limiting
- Graceful error handling for individual ticket failures
- Continues processing even if some tickets fail

### Memory Usage
- Streams JSON output to avoid large memory allocations
- Uses maps for deduplication of JIRA IDs
- Efficient string handling for large commit histories

## Troubleshooting

### Common Issues

1. **Git Repository Not Found**
   ```
   Error: not in a git repository
   ```
   **Solution**: Ensure you're running the command from a git repository

2. **JIRA Authentication Failed**
   ```
   JIRA token not found, set jira_token variable
   ```
   **Solution**: Set the required environment variables

3. **Invalid Regex Pattern**
   ```
   Error: invalid JIRA ID regex
   ```
   **Solution**: Check your regex pattern syntax

4. **Commit Not Found**
   ```
   ❌ commit 'abc123' not found
   ```
   **Solution**: Verify the commit hash exists and fetch depth is sufficient

5. **HEAD Commit Not Found**
   ```
   ❌ HEAD commit not found. Repository may be empty or corrupted
   ```
   **Solution**: Ensure the repository has at least one commit and is not corrupted

### Debug Mode
```bash
# Enable verbose output
export DEBUG=true
./main <start_commit>

# Extract only to debug git operations
./main --extract-only <start_commit>
```

## Contributing

### Code Style
- Follow Go conventions and `gofmt`
- Add comments for exported functions
- Include error handling for all external calls

### Testing
- Add unit tests for new functions
- Test error conditions
- Validate JSON output format

### Dependencies
- Keep dependencies minimal
- Use specific versions in `go.mod`
- Document any new dependencies

## License

This tool is part of the Evidence-Examples repository and follows the same licensing terms. 