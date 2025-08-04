package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"reflect"
	"sort"
	"strings"
	"time"

	jira "github.com/andygrunwald/go-jira/v2/cloud"
)

/*
    JiraTransitionResponse is the json formatted predicate that will be returned to the calling build process for cresting an evidence
    its structure should be:

    {
        "ticketRequested": [ "EV-1", "EV-2" ],
        "tasks": [
            {
                "key": "EV-1",
                "status": "QA in Progress",
                "description": "<description text>",
                "type": "Task",
                "project": "EV",
                "created": "2020-01-01T12:11:56.063+0530",
                "updated": "2020-01-01T12:12:01.876+0530",
                "assignee": "<assignee name>",
                "reporter": "<reporter name>",
                "priority": "Medium",
                "transitions": [
                    {
                        "from_status": "To Do",
                        "to_status": "In Progress",
                        "author": "<>author name>",
                        "author_user_name": "<author email>",
                        "transition_time": "2020-07-28T16:39:54.620+0530"
                    }
                ]
            },
            {
                "key": "EV-2",
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

   notice that the calling client should first check that return value was 0 before using the response JSON,
   otherwise the response is an error message which cannot be parsed
*/

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

// JiraClient wraps the JIRA client and provides methods for JIRA operations
type JiraClient struct {
	client *jira.Client
}

// NewJiraClient creates a new JIRA client with authentication
func NewJiraClient() (*JiraClient, error) {
	jira_token := os.Getenv("JIRA_API_TOKEN")
	if jira_token == "" {
		return nil, fmt.Errorf("JIRA token not found, set jira_token variable")
	}
	jira_url := os.Getenv("JIRA_URL")
	if jira_url == "" {
		return nil, fmt.Errorf("JIRA URL not found, set jira_url variable")
	}
	jira_username := os.Getenv("JIRA_USERNAME")
	if jira_username == "" {
		return nil, fmt.Errorf("JIRA username not found, set JIRA_USERNAME variable")
	}

	// connect to JIRA
	tp := jira.BasicAuthTransport{
		Username: jira_username,
		APIToken: jira_token,
	}
	client, err := jira.NewClient(jira_url, tp.Client())
	if err != nil {
		return nil, fmt.Errorf("jira.NewClient error: %v", err)
	}

	return &JiraClient{client: client}, nil
}

func (jc *JiraClient) FetchJiraDetails(jiraIDs []string) TransitionCheckResponse {
	// initialize the response
	transitionCheckResponse := TransitionCheckResponse{}
	transitionCheckResponse.TicketRequested = jiraIDs

	// loop over all JIRAs sent to the function
	for _, jiraId := range jiraIDs {
		issue, _, err := jc.client.Issue.Get(context.Background(), jiraId, &jira.GetQueryOptions{Expand: "changelog"})
		if issue == nil {
			fmt.Fprintf(os.Stderr, "Got error for extracting issue with jira id: %s error %v\n", jiraId, err)
			// Skip this ticket and continue with the next one
			jiraTransitionResult := JiraTransitionResult{
				Key:         jiraId,
				Status:      "Error",
				Description: "Error: Could not retrieve issue",
				Type:        "Error",
				Project:     "",
				Created:     "",
				Updated:     "",
				Assignee:    nil,
				Reporter:    "",
				Priority:    "",
				Transitions: []Transition{},
			}
			transitionCheckResponse.Tasks = append(transitionCheckResponse.Tasks, jiraTransitionResult)
			continue
		}

		// adding the jira result to the list of results
		jiraTransitionResult := JiraTransitionResult{
			Key:         issue.Key,
			Status:      issue.Fields.Status.Name,
			Description: getDescription(issue.Fields.Description),
			Type:        issue.Fields.Type.Name,
			Project:     issue.Fields.Project.Key,
			Created:     getTimeAsString(issue.Fields.Created),
			Updated:     getTimeAsString(issue.Fields.Updated),
			Assignee:    getAssignee(issue.Fields.Assignee),
			Reporter:    issue.Fields.Reporter.DisplayName,
			Priority:    issue.Fields.Priority.Name,
			Transitions: []Transition{},
		}

		if len(issue.Changelog.Histories) > 0 {
			for _, history := range issue.Changelog.Histories {
				for _, changelogItems := range history.Items {
					if changelogItems.Field == "status" {
						transition := Transition{
							FromStatus:     changelogItems.FromString,
							ToStatus:       changelogItems.ToString,
							Author:         history.Author.DisplayName,
							AuthorEmail:    history.Author.EmailAddress,
							TransitionTime: history.Created,
						}
						jiraTransitionResult.Transitions = append(jiraTransitionResult.Transitions, transition)
					}
				}
			}
		}
		transitionCheckResponse.Tasks = append(transitionCheckResponse.Tasks, jiraTransitionResult)
	}

	return transitionCheckResponse
}

// Helper function to extract description text from JIRA description field
func getDescription(desc interface{}) string {
	if desc == nil {
		return ""
	}

	// Handle the Atlassian Document Format (ADF) structure
	if descMap, ok := desc.(map[string]interface{}); ok {
		if content, exists := descMap["content"]; exists {
			if contentArray, ok := content.([]interface{}); ok {
				var result strings.Builder
				for _, item := range contentArray {
					if itemMap, ok := item.(map[string]interface{}); ok {
						if itemType, exists := itemMap["type"]; exists && itemType == "paragraph" {
							if itemContent, exists := itemMap["content"]; exists {
								if itemContentArray, ok := itemContent.([]interface{}); ok {
									for _, textItem := range itemContentArray {
										if textMap, ok := textItem.(map[string]interface{}); ok {
											if textType, exists := textMap["type"]; exists && textType == "text" {
												if text, exists := textMap["text"]; exists {
													if textStr, ok := text.(string); ok {
														result.WriteString(textStr)
													}
												}
											}
										}
									}
								}
							}
						}
					}
				}
				return result.String()
			}
		}
	}

	// Fallback to string representation
	return fmt.Sprintf("%v", desc)
}

// Helper function to get assignee display name or nil if not assigned
func getAssignee(assignee *jira.User) *string {
	if assignee == nil {
		return nil
	}
	return &assignee.DisplayName
}

// Helper function to get time as string from JIRA time field
func getTimeAsString(timeField interface{}) string {
	if timeField == nil {
		return ""
	}

	// Try to marshal to JSON and then unmarshal as string
	jsonBytes, err := json.Marshal(timeField)
	if err == nil {
		var timeStr string
		if json.Unmarshal(jsonBytes, &timeStr) == nil {
			return timeStr
		}
	}

	// Use reflection to check the actual type
	val := reflect.ValueOf(timeField)
	if val.Kind() == reflect.String {
		return val.String()
	}

	// Try to access the Time field if it's a struct
	if val.Kind() == reflect.Struct {
		timeField := val.FieldByName("Time")
		if timeField.IsValid() && timeField.CanInterface() {
			if t, ok := timeField.Interface().(time.Time); ok {
				return t.Format("2006-01-02T15:04:05.000-0700")
			}
		}
	}

	// Fallback to string representation
	return fmt.Sprintf("%v", timeField)
}

// formatWorkflow formats workflow transitions into a readable string
func formatWorkflow(transitions []Transition) string {
	if len(transitions) == 0 {
		return "No transitions available"
	}

	// Sort transitions by time (newest first) and reverse to get chronological order
	sortedTransitions := make([]Transition, len(transitions))
	copy(sortedTransitions, transitions)
	sort.Slice(sortedTransitions, func(i, j int) bool {
		return sortedTransitions[i].TransitionTime > sortedTransitions[j].TransitionTime
	})

	// Extract status names in chronological order
	statuses := make(map[string]bool)
	var statusList []string

	// Process transitions in reverse order to get chronological sequence
	for i := len(sortedTransitions) - 1; i >= 0; i-- {
		transition := sortedTransitions[i]
		fromStatus := transition.FromStatus
		toStatus := transition.ToStatus

		if fromStatus != "" && !statuses[fromStatus] {
			statuses[fromStatus] = true
			statusList = append(statusList, fromStatus)
		}
		if toStatus != "" && !statuses[toStatus] {
			statuses[toStatus] = true
			statusList = append(statusList, toStatus)
		}
	}

	// If no transitions, return current status
	if len(statusList) == 0 {
		return "No workflow data"
	}

	return strings.Join(statusList, " → ")
}

// escapeMarkdown escapes pipe characters for markdown table
func escapeMarkdown(text string) string {
	return strings.ReplaceAll(text, "|", "\\|")
}

// generateMarkdownContent generates markdown content from JIRA data
func generateMarkdownContent(data TransitionCheckResponse) string {
	tasks := data.Tasks
	ticketCount := len(tasks)

	// Header
	content := "# Jira Tickets Summary\n"
	content += fmt.Sprintf("Found %d associated tickets.\n\n", ticketCount)

	// Table header
	content += "| Key | Summary | Type | Priority | Workflow |\n"
	content += "|-----|---------|------|----------|----------|\n"

	// Process each task
	for _, task := range tasks {
		key := task.Key
		description := task.Description
		taskType := task.Type
		priority := task.Priority
		transitions := task.Transitions

		// Format workflow
		workflow := formatWorkflow(transitions)

		// Handle error cases
		if taskType == "Error" {
			description = task.Description
			if description == "" {
				description = "Error retrieving ticket data"
			}
			taskType = "Error"
			priority = "N/A"
			workflow = "N/A"
		}

		// Escape pipe characters in content for markdown table
		key = escapeMarkdown(key)
		description = escapeMarkdown(description)
		taskType = escapeMarkdown(taskType)
		priority = escapeMarkdown(priority)
		workflow = escapeMarkdown(workflow)

		// Add row to table
		content += fmt.Sprintf("| %s | %s | %s | %s | %s |\n", key, description, taskType, priority, workflow)
	}

	return content
}

// GenerateMarkdownReport generates and writes markdown report
func GenerateMarkdownReport(data TransitionCheckResponse, outputFile string) error {
	fmt.Println("Step 4: Generating markdown report...")

	content := generateMarkdownContent(data)

	// Determine markdown file path
	markdownFile := "transformed_jira_data.md"
	if outputFile != "transformed_jira_data.json" {
		// If custom output file is specified, use similar name for markdown
		baseName := strings.TrimSuffix(outputFile, filepath.Ext(outputFile))
		markdownFile = baseName + ".md"
	}

	// Write markdown file
	if err := writeToFile(markdownFile, []byte(content)); err != nil {
		return fmt.Errorf("error writing markdown file: %v", err)
	}

	fmt.Printf("Markdown report saved to: %s\n", markdownFile)
	return nil
}
