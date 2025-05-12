# Contributing Guideline - Internal Repository

## Branch Naming Convention

Refer to the Developer Services Branching Policy and Git User [Guide](https://confluence.silabs.com/pages/viewpage.action?pageId=315870645).

Use lowercase letters and hyphens (`-`) as delimiters.  
Google search treats a hyphen as a word separator, which helps improve the visibility of public repositories.  
We should structure our internal repository as if it were a public one.

Branch name should be short and clear. If possible it can be the JIRA ticket name.
Also it is recommended to include the JIRA ticket number. 
Example:
```
IOT_DS-123-update-sdk-version
```

## Commit Message Format

We use [smart commits](https://support.atlassian.com/bitbucket-cloud/docs/use-smart-commits/) to sync GitHub commits with our JIRA server.  
This requires the JIRA ticket number in the commit message.  
The first line is the commit message, and the next lines provide the description.  
The commit message should be short and clear, and it must contain the JIRA ticket number.  
You can add more details in the description.

**Command Line:**
```
git commit -m "IOT_DS-1234 initial version of SDK 4.4.3 is committed" -m "Not final version. Several compiler warnings need to be addressed."
```

**VS Code:**  
The first line is the commit message, and the next lines are the commit description.

## Pull Request Guideline

Refer to the general pull request [guideline](https://opensource.guide/how-to-contribute/#opening-a-pull-request) from GitHub.

### As a Developer

What to consider when raising a Pull Request:

1. **Pull Request Naming**  
   By default, GitHub uses the branch name as the pull request title. If the branch naming guideline was followed, no changes are needed here.

2. **Check the Reviewer List**  
   GitHub assigns reviewers based on the [CODEOWNERS](CODEOWNERS) file.  
   Add more reviewers if needed. Do not remove reviewers from the PR. Ask the repository owner for updates to the code owners.

3. **Evaluate the Action Workflow Results**  
   The following workflows are included in every repository:
   - **[Coding Convention Check](workflows/00-Check-Code-Convention.yml)**: Analyzes the code formatting and fails if any rules are broken.
   - **[Firmware Build](workflows/02-Build-Firmware.yml)**: Builds the firmware inside the [Dockerfile](../Dockerfile).  
   - **[Secret Scanner](workflows/04-TruffleHog-Security-Scan.yml)**: Runs the TruffleHog security scanner to look for API keys and committed secrets.
   - **[SonarQube Analysis](workflows/zz-sonarqube-analysis.yml)**: Runs SonarQube analysis on the project. Refer to the related [Confluence page](https://confluence.silabs.com/display/IoTApps/SQA+-+SonarQube+howTo).

### As a Reviewer

What to consider when reviewing a Pull Request:

- All builds must pass successfully.
- The code must follow the Silicon Labs [coding guidelines](https://github.com/SiliconLabsSoftware/agreements-and-guidelines/blob/main/coding_standard.md).
- Write clear comments. Describe the issue and explain why you disagree (e.g., mistakes, errors, violations of conventions, performance risks, security issues, etc.).
- If any comments must be addressed mandatorily, mark the pull request as “Draft.”
