package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
)



// Git-related functions

// getBranchInfo returns current branch name, latest commit hash, and JIRA ID from latest commit
func getBranchInfo() (string, string, string, error) {
	// Get current branch
	branchCmd := exec.Command("git", "branch", "--show-current")
	branchOutput, err := branchCmd.Output()
	if err != nil {
		return "", "", "", fmt.Errorf("failed to get branch name: %v", err)
	}
	branchName := strings.TrimSpace(string(branchOutput))

	// Get latest commit hash
	commitCmd := exec.Command("git", "log", "-1", "--format=%H")
	commitOutput, err := commitCmd.Output()
	if err != nil {
		return "", "", "", fmt.Errorf("failed to get latest commit: %v", err)
	}
	commitHash := strings.TrimSpace(string(commitOutput))

	// Get JIRA ID from latest commit message
	subjectCmd := exec.Command("git", "log", "-1", "--format=%s")
	subjectOutput, err := subjectCmd.Output()
	if err != nil {
		return "", "", "", fmt.Errorf("failed to get commit subject: %v", err)
	}
	subject := strings.TrimSpace(string(subjectOutput))
	
	// Use default JIRA ID regex pattern to extract valid JIRA IDs
	jiraIDRegex := "[A-Z]+-[0-9]+"
	regex, err := regexp.Compile(jiraIDRegex)
	if err != nil {
		return branchName, commitHash, "", nil
	}
	
	// Find all JIRA IDs in the commit message
	matches := regex.FindAllString(subject, -1)
	if len(matches) > 0 {
		// Return the first valid JIRA ID found
		return branchName, commitHash, matches[0], nil
	}

	return branchName, commitHash, "", nil
}

// validateCommit checks if a commit exists in the repository
func validateCommit(commit string) error {
	cmd := exec.Command("git", "rev-parse", "--verify", commit)
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("commit '%s' not found. Check fetch depth or commit existence", commit)
	}
	return nil
}

// validateHEAD checks if HEAD commit exists in the repository
func validateHEAD() error {
	cmd := exec.Command("git", "rev-parse", "--verify", "HEAD")
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("HEAD commit not found. Repository may be empty or corrupted")
	}
	return nil
}

// extractJiraIDs extracts JIRA IDs from git commit messages in a given range
func extractJiraIDs(startCommit, jiraIDRegex, currentJiraID string) ([]string, error) {
	// Get commit messages from startCommit to HEAD
	cmd := exec.Command("git", "log", "--pretty=format:%s", startCommit+"..HEAD")
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to get commit messages: %v", err)
	}

	// Parse regex
	regex, err := regexp.Compile(jiraIDRegex)
	if err != nil {
		return nil, fmt.Errorf("invalid JIRA ID regex: %v", err)
	}

	// Extract JIRA IDs from commit messages
	jiraIDs := make(map[string]bool)
	
	// Add current JIRA ID if it matches the pattern
	if currentJiraID != "" && regex.MatchString(currentJiraID) {
		jiraIDs[currentJiraID] = true
	}

	// Extract from commit messages
	lines := strings.Split(string(output), "\n")
	for _, line := range lines {
		matches := regex.FindAllString(line, -1)
		for _, match := range matches {
			jiraIDs[match] = true
		}
	}

	// Convert map to slice
	var result []string
	for jiraID := range jiraIDs {
		if jiraID != "" {
			result = append(result, jiraID)
		}
	}

	if len(result) == 0 {
		fmt.Fprintf(os.Stderr, "⚠️  No JIRA IDs found in commit range %s..HEAD\n", startCommit)
	}

	return result, nil
}



// checkGitRepository checks if we're in a git repository
func checkGitRepository() error {
	cmd := exec.Command("git", "rev-parse", "--git-dir")
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("not in a git repository")
	}
	return nil
}

// writeToFile writes data to a file
func writeToFile(filename string, data []byte) error {
	// Create directory if it doesn't exist
	dir := filepath.Dir(filename)
	if dir != "." {
		if err := os.MkdirAll(dir, 0755); err != nil {
			return fmt.Errorf("failed to create directory: %v", err)
		}
	}
	
	return os.WriteFile(filename, data, 0644)
}

// displayUsage shows the usage information
func displayUsage() {
	fmt.Println("JIRA Evidence Tool - Enhanced")
	fmt.Println("")
	fmt.Println("Usage:")
	fmt.Println("  ./main [OPTIONS] <start_commit>")
	fmt.Println("  ./main <jira_id1> [jira_id2] [jira_id3] ...")
	fmt.Println("")
	fmt.Println("Options:")
	fmt.Println("  -r, --regex PATTERN    JIRA ID regex pattern (default: '[A-Z]+-[0-9]+')")
	fmt.Println("  -o, --output FILE      Output file for JIRA data (default: transformed_jira_data.json)")
	fmt.Println("  --extract-only         Only extract JIRA IDs, don't fetch details")
	fmt.Println("  --extract-from-git     Extract JIRA IDs from git commits (legacy mode)")
	fmt.Println("  -h, --help             Display this help message")
	fmt.Println("")
	fmt.Println("Arguments:")
	fmt.Println("  start_commit           Starting commit hash (excluded from evidence filter)")
	fmt.Println("")
	fmt.Println("Environment Variables:")
	fmt.Println("  JIRA_API_TOKEN         JIRA API token")
	fmt.Println("  JIRA_URL              JIRA instance URL")
	fmt.Println("  JIRA_USERNAME         JIRA username")
	fmt.Println("  JIRA_ID_REGEX         JIRA ID regex pattern (can be overridden with -r)")
	fmt.Println("  OUTPUT_FILE           Output file path (can be overridden with -o)")
	fmt.Println("  ATTACH_OPTIONAL_CUSTOM_MARKDOWN_TO_EVIDENCE  Generate markdown report (true/false)")
	fmt.Println("")
	fmt.Println("Examples:")
	fmt.Println("  ./main abc123def456")
	fmt.Println("  ./main -r 'EV-\\d+' -o jira_results.json abc123def456")
	fmt.Println("  ./main --extract-only abc123def456")
	fmt.Println("  ./main EV-123 EV-456 EV-789")
}



func main() {
	// Parse command line flags
	var (
		jiraIDRegex = flag.String("r", "", "JIRA ID regex pattern")
		outputFile  = flag.String("o", "", "Output file for JIRA data")
		extractOnly = flag.Bool("extract-only", false, "Only extract JIRA IDs, don't fetch details")
		extractFromGit = flag.Bool("extract-from-git", false, "Extract JIRA IDs from git commits (legacy mode)")
		help        = flag.Bool("h", false, "Display help message")
		helpLong    = flag.Bool("help", false, "Display help message")
	)
	flag.Parse()

	// Handle help flags
	if *help || *helpLong {
		displayUsage()
		return
	}

	// Handle legacy extract-from-git mode
	if *extractFromGit {
		args := flag.Args()
		if len(args) < 2 {
			fmt.Println("Usage: ./main --extract-from-git <start_commit> <jira_id_regex>")
			os.Exit(1)
		}

		startCommit := args[0]
		regex := args[1]

		// Get branch info
		branchName, commitHash, currentJiraID, err := getBranchInfo()
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error getting branch info: %v\n", err)
			os.Exit(1)
		}

		fmt.Printf("BRANCH_NAME: %s\n", branchName)
		fmt.Printf("JIRA ID: %s\n", currentJiraID)
		fmt.Printf("START_COMMIT: %s\n", commitHash)

		// Validate HEAD
		if err := validateHEAD(); err != nil {
			fmt.Fprintf(os.Stderr, "❌ %v\n", err)
			os.Exit(0) // Exit gracefully as per original behavior
		}

		// Validate commit
		if err := validateCommit(startCommit); err != nil {
			fmt.Fprintf(os.Stderr, "❌ %v\n", err)
			os.Exit(0) // Exit gracefully as per original behavior
		}

		// Extract JIRA IDs
		jiraIDs, err := extractJiraIDs(startCommit, regex, currentJiraID)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error extracting JIRA IDs: %v\n", err)
			os.Exit(1)
		}

		if len(jiraIDs) == 0 {
			fmt.Println("No JIRA IDs found")
			os.Exit(0)
		}

		// Print comma-separated JIRA IDs
		fmt.Println(strings.Join(jiraIDs, ","))
		return
	}

	// Get remaining arguments
	args := flag.Args()

	// Check if we have a start_commit argument
	if len(args) == 0 {
		fmt.Println("Error: start_commit is required")
		displayUsage()
		os.Exit(1)
	}

	startCommit := args[0]

	// Check if we have arguments for direct JIRA ID processing (only if not in extract-only mode)
	if !*extractOnly && len(args) > 0 && !strings.HasPrefix(args[0], "-") {
		// Check if the argument matches the JIRA ID pattern
		pattern := "[A-Z]+-[0-9]+"
		if *jiraIDRegex != "" {
			pattern = *jiraIDRegex
		}
		regex, err := regexp.Compile(pattern)
		if err == nil && regex.MatchString(args[0]) {
			// Direct JIRA ID processing mode
			processJiraIDs(args)
			return
		}
		// If it doesn't match the pattern, treat it as a start commit
	}

	// Set default values from environment variables if not provided
	if *jiraIDRegex == "" {
		*jiraIDRegex = os.Getenv("JIRA_ID_REGEX")
		if *jiraIDRegex == "" {
			*jiraIDRegex = "[A-Z]+-[0-9]+"
		}
	}

	if *outputFile == "" {
		*outputFile = os.Getenv("OUTPUT_FILE")
		if *outputFile == "" {
			*outputFile = "transformed_jira_data.json"
		}
	}

	// Check if we're in a git repository
	if err := checkGitRepository(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("=== JIRA Details Fetching Process ===")
	fmt.Printf("Start Commit: %s\n", startCommit)
	fmt.Printf("JIRA ID Regex: %s\n", *jiraIDRegex)
	fmt.Printf("Output File: %s\n", *outputFile)
	fmt.Println("")

	// Step 1: Extract JIRA IDs from git commits
	fmt.Println("Step 1: Extracting JIRA IDs from git commits...")

	// Get branch info
	branchName, commitHash, currentJiraID, err := getBranchInfo()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error getting branch info: %v\n", err)
		os.Exit(1)
	}

	// Display branch information
	fmt.Printf("Branch: %s\n", branchName)
	fmt.Printf("Latest Commit: %s\n", commitHash)

	// Validate HEAD
	if err := validateHEAD(); err != nil {
		fmt.Fprintf(os.Stderr, "❌ %v\n", err)
		os.Exit(0) // Exit gracefully as per original behavior
	}

	// Validate commit
	if err := validateCommit(startCommit); err != nil {
		fmt.Fprintf(os.Stderr, "❌ %v\n", err)
		os.Exit(0) // Exit gracefully as per original behavior
	}

	// Extract JIRA IDs
	jiraIDs, err := extractJiraIDs(startCommit, *jiraIDRegex, currentJiraID)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error extracting JIRA IDs: %v\n", err)
		os.Exit(1)
	}

	if len(jiraIDs) == 0 {
		fmt.Println("No JIRA IDs found in commit range")
		os.Exit(0)
	}

	fmt.Printf("Found JIRA IDs: %s\n", strings.Join(jiraIDs, ", "))

	// If extract-only mode, just return the JIRA IDs
	if *extractOnly {
		fmt.Println(strings.Join(jiraIDs, ","))
		return
	}

	// Step 2: Fetch JIRA details
	fmt.Println("")
	fmt.Println("Step 2: Fetching JIRA details...")

	// Create JIRA client and process JIRA IDs
	jiraClient, err := NewJiraClient()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error creating JIRA client: %v\n", err)
		os.Exit(1)
	}

	// Process JIRA IDs and get results
	response := jiraClient.FetchJiraDetails(jiraIDs)

	// Step 3: Write results to file
	fmt.Println("")
	fmt.Println("Step 3: Writing results...")

	jsonBytes, err := json.MarshalIndent(response, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error marshaling JSON: %v\n", err)
		os.Exit(1)
	}

	if err := writeToFile(*outputFile, jsonBytes); err != nil {
		fmt.Fprintf(os.Stderr, "Error writing to file: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("JIRA data saved to: %s\n", *outputFile)

	// Step 4: Generate markdown report if requested
	attachMarkdown := os.Getenv("ATTACH_OPTIONAL_CUSTOM_MARKDOWN_TO_EVIDENCE")
	if attachMarkdown == "true" {
		if err := GenerateMarkdownReport(response, *outputFile); err != nil {
			fmt.Fprintf(os.Stderr, "Warning: Failed to generate markdown report: %v\n", err)
			// Don't exit on markdown generation failure
		}
	} else {
		fmt.Println("Step 4: Skipping markdown report generation (ATTACH_OPTIONAL_CUSTOM_MARKDOWN_TO_EVIDENCE != 'true')")
	}

	fmt.Println("")
	fmt.Println("=== Process completed successfully ===")
}

// processJiraIDs handles direct JIRA ID processing (original functionality)
func processJiraIDs(jiraIDs []string) {
	// Create a new Jira client
	jiraClient, err := NewJiraClient()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error creating JIRA client: %v\n", err)
		os.Exit(1)
	}

	// Get response
	response := jiraClient.FetchJiraDetails(jiraIDs)

	// marshal the response to JSON
	jsonBytes, err := json.Marshal(response)
	if err != nil {
		fmt.Println("Error marshaling JSON", err)
		os.Exit(1)
	}

	// return response to caller through stdout
	os.Stdout.Write(jsonBytes)
}


