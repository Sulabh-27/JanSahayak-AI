# MASTER BUILD PROMPT — JanSahayak AI

## 1. Your Role

Act as a senior full-stack engineer, AI engineer, product designer, and QA engineer. Build a complete, polished, production-minded MVP called **JanSahayak AI — जनसहायक AI**, an AI-assisted government application review system for government officers in Madhya Pradesh, India.

This project is a hiring assignment for a Full Stack AI Engineer position at Kenpath.

The application must be functional, easy to understand, visually polished, locally relevant, and deployable. Do not create a static prototype or a dashboard with non-functional buttons.

Work autonomously: inspect the workspace, create the project structure, implement the application, run it, test important workflows, fix errors, and document how to run and deploy it.

The assignment is time-boxed. Prioritize a complete, reliable MVP over unnecessary complexity.

## 2. Product Problem

Government officers process applications for services such as income certificates. Reviewing applications manually can be time-consuming because officers need to examine application details, check document completeness, identify inconsistencies, and determine which applications need attention first.

Build an internal officer-facing application that:

1. Displays pending applications and their priorities.
2. Provides AI-assisted application summaries and document checks.
3. Identifies missing documents and inconsistencies.
4. Suggests a decision with evidence-based explanations.
5. Allows the officer to approve, reject, or return an application for corrections.
6. Records the officer's final decision and audit history.

The AI is an assistant, not the decision-maker. The officer must explicitly make the final decision.

Use fictional data only. Never use real citizen records.

## 3. Target Users and Language

Primary users: government officers reviewing income certificate applications in Madhya Pradesh.

Make Hindi the primary interface language. Use natural, professional Hindi suitable for government administration. English may appear as a secondary translation for technical terms or identifiers.

Examples:
- Dashboard: डैशबोर्ड
- Pending applications: लंबित आवेदन
- Priority: प्राथमिकता
- Application details: आवेदन विवरण
- Document verification: दस्तावेज़ सत्यापन
- AI review: AI समीक्षा
- Approve: स्वीकृत करें
- Reject: अस्वीकृत करें
- Return for corrections: सुधार हेतु वापस करें
- Decision history: निर्णय इतिहास

Use correct Unicode Devanagari rendering. Avoid awkward machine-translated Hindi.

Clearly label the application as a demonstration prototype, not an official government service.

## 4. Recommended Technology Stack

Use the following stack unless a genuine compatibility issue requires a justified alternative:

- Python 3.11 or a compatible supported version.
- Streamlit for the web UI.
- Pandas for table operations where appropriate.
- SQLite for persistent application state, decisions, and audit history.
- JSON seed data for fictional sample applications.
- Groq API with a configurable supported model for AI review.
- Pydantic for validating structured AI output, if compatible with the chosen dependencies.
- Pytest for important business-logic tests.
- python-dotenv for local environment configuration.

Keep the architecture modular. Do not put all business logic into app.py.

Do not introduce LangChain, LangGraph, MCP, vector databases, microservices, or multi-agent orchestration unless a necessary feature genuinely requires them. They are not required for this MVP.

If an API key is missing or an AI request fails, provide a clear error state and a usable deterministic demo fallback. Never present a fabricated AI result as if a live LLM generated it.

## 5. Application Architecture

Use this structure, adapting it if necessary to maintain simplicity:

jansahayak-ai/
  app.py
  config.py
  requirements.txt
  README.md
  .gitignore
  .env.example
  data/
    sample_applications.json
  services/
    __init__.py
    database.py
    validation.py
    prioritization.py
    ai_review.py
    decisions.py
    authentication.py
  components/
    __init__.py
    dashboard.py
    application_table.py
    application_review.py
    common.py
  tests/
    test_validation.py
    test_prioritization.py
    test_decisions.py
  .streamlit/
    config.toml

Create only the files that are useful. Keep imports clean and responsibilities clearly separated.

### Responsibilities

- app.py: application entry point and navigation.
- database.py: SQLite schema, initialization, seed loading, queries, transactions.
- validation.py: deterministic document and field validation.
- prioritization.py: explainable application priority calculation.
- ai_review.py: LLM integration, structured response validation, fallback behavior.
- decisions.py: approve, reject, return actions and audit records.
- authentication.py: simple demo authentication and session management.
- components/: reusable UI elements.
- tests/: business-logic and workflow tests.

Use parameterized SQL queries. Do not build SQL statements by concatenating user input.

## 6. Data Model and Fictional Seed Data

Create at least 12 realistic but entirely fictional income certificate applications.

Use synthetic Indian names and obviously fictional contact details. Do not use real Aadhaar numbers, actual personal identifiers, or real citizen documents.

Each application should include:

- application_id
- fictional applicant name
- application type
- submission date
- last updated date
- application status
- assigned officer
- required document checklist
- submitted document checklist
- synthetic declared income, where relevant
- a fictional district or locality
- review notes
- deterministic validation findings

Include a variety of cases:

1. Complete application awaiting review.
2. Application missing income proof.
3. Application missing identity proof.
4. Application with an inconsistent income value between two sample records.
5. Application with all required sample documents.
6. Application awaiting review for several days.
7. Application returned for corrections.
8. Previously approved application.
9. Previously rejected application.
10. Application with multiple missing documents.
11. Application with conflicting dates.
12. Application with insufficient information to determine a recommendation.

Represent document metadata in structured JSON. Do not depend on real PDF files or external government APIs.

Make the sample dataset easy to reset and reseed without creating duplicate records.

Do not hardcode dashboard statistics. Calculate all counts from persisted application records.

## 7. Officer Dashboard

Build a polished dashboard in Hindi.

### Header

Show:
- JanSahayak AI logo or simple text-based branding.
- जनसहायक AI — आवेदन समीक्षा सहायक.
- A small badge indicating that this is a demo environment.
- Logged-in demo officer identity.
- Logout action.

### Summary cards

Calculate and display:

- कुल आवेदन
- समीक्षा हेतु लंबित
- उच्च प्राथमिकता
- दस्तावेज़ अधूरे
- निर्णय की प्रतीक्षा

Make the meaning of each metric clear. Avoid double-counting or mixing incompatible statuses.

### Applications table

Show useful columns:

- Application ID
- Applicant
- Submission date
- Days pending
- Document completeness
- Priority
- Current status
- Action to open the application

Include working features:
- Search by application ID or fictional applicant name.
- Filter by status.
- Filter by priority.
- Filter by missing-document status.
- Sort by priority and submission age.
- Open a selected application.
- Empty states when no applications match.

Use visual status indicators with accessible contrast.

### Priority model

Implement deterministic priority scoring in prioritization.py.

Possible factors:
- Days awaiting review.
- Number of missing required documents.
- Explicit configured urgency.
- Whether the application has unresolved inconsistencies.

Use explainable rules, not an opaque AI-generated priority score.

Keep missing-document severity distinct from processing urgency. For example, an application may have high urgency but still be incomplete.

Display a short explanation for why an application is marked high priority.

Do not claim that any score is an official government rule.

## 8. Application Review Screen

When an officer opens an application, display a detailed review workspace.

### A. Application details

Show all available fictional application fields, submission dates, current status, and review notes.

### B. Document checklist

Show each required document and its state:
- Available
- Missing
- Needs verification
- Not applicable, where configured

Calculate completeness from the configured document requirements and stored document metadata.

Distinguish between a missing document and a document that has not yet been verified.

Do not claim to have examined the contents of a document when only its metadata is available.

### C. Validation findings

Run deterministic checks before requesting AI analysis.

Examples:
- Required document missing.
- Income values disagree across supplied sample fields.
- Dates are inconsistent.
- Required application field is empty.
- Insufficient information to establish a finding.

Each finding should include:
- Severity.
- Human-readable explanation in Hindi.
- Evidence or field references.
- Recommended next verification step.

Avoid asserting fraud or misconduct merely because information is inconsistent.

### D. AI-assisted review

Provide a prominent button:

"AI से आवेदन की समीक्षा करें"

When clicked:
1. Retrieve the selected application from SQLite.
2. Run deterministic validation.
3. Construct a minimal, structured input for the LLM.
4. Ask the model to summarize the application in Hindi.
5. Present known missing documents and inconsistencies.
6. Generate a suggested next action.
7. Explain the reasons and evidence.
8. Validate the response structure.
9. Display the result and any uncertainty.

The AI response should contain:

- summary_hi: concise Hindi summary.
- missing_documents: list of missing required items.
- inconsistencies: list of identified discrepancies.
- suggested_action: APPROVE, REJECT, RETURN_FOR_CORRECTION, or NEEDS_MANUAL_REVIEW.
- reasons_hi: evidence-based explanations in Hindi.
- evidence: references to available application fields or validation findings.
- confidence: optional calibrated or clearly qualified confidence indicator.
- uncertainty_hi: limitations or additional checks needed.

Use an appropriate typed schema. Reject malformed model output and handle parsing errors safely.

Important rules:
- The LLM must not invent missing facts.
- The LLM must not invent official policy or eligibility thresholds.
- The LLM must not claim to have verified a document it has not seen.
- A missing document must be reported using the deterministic validator's findings.
- If evidence is insufficient, prefer NEEDS_MANUAL_REVIEW.
- A recommendation is not a final decision.
- Do not use model confidence as a substitute for evidence.
- A rejection recommendation must never be based solely on missing information.
- The officer must always make the final decision.

If no API key is configured, enable a clearly labeled demo review mode based on deterministic checks. Show "डेमो समीक्षा — लाइव AI विश्लेषण नहीं" rather than implying a real model call occurred.

### E. AI output UI

Display the summary, issues, supporting evidence, uncertainty, and recommendation in distinct sections.

Do not render raw JSON directly to the officer unless there is an optional technical/debug view.

Make it easy to compare:
- AI recommendation.
- Rule-based findings.
- Officer's final decision.

## 9. Human Decision Workflow

Provide three primary actions:

1. स्वीकृत करें
2. अस्वीकृत करें
3. सुधार हेतु वापस करें

Require a reason or officer remark before recording a decision.

Use a confirmation step before committing the action.

### Approval
- Require an explicit officer confirmation.
- Record the final status as approved.
- Save the officer's reason.

### Rejection
- Require a mandatory reason.
- Clearly show a confirmation step.
- Record the final status as rejected.
- Do not imply that an AI recommendation itself constitutes sufficient legal grounds.

### Return for corrections
- Require an explanation of missing information or corrections needed.
- Allow the officer to record a list of requested corrections.
- Record the status as returned for corrections.

On successful action:
- Persist the new status in SQLite.
- Persist the officer identity.
- Record the timestamp.
- Record the officer's reason.
- Record the AI recommendation separately, if one exists.
- Record whether the officer followed or overrode the recommendation.
- Append an audit event.
- Refresh the dashboard metrics.
- Display a clear Hindi success message.

Do not allow a stale screen to silently overwrite a newer decision.

Keep all writes transactional. Avoid duplicate decision records when an action is submitted twice.

## 10. Audit History

Create a simple application history panel showing:
- Event timestamp.
- Application status change.
- Officer action.
- Officer remarks.
- AI recommendation at the time, if available.

Keep audit events append-only from the normal UI. Do not offer an ordinary delete-history button.

Clearly distinguish an AI-generated suggestion from an officer-authorized action.

## 11. UI and Visual Design

Build a professional administrative application, not a generic chatbot.

Design direction:
- Clean, modern enterprise dashboard.
- Light neutral background.
- Deep navy or restrained indigo for primary elements.
- Subtle saffron and green accents where appropriate.
- Consistent spacing and typography.
- Responsive layout.
- Compact but readable information density.
- Clear distinction between warnings, missing information, successful checks, and final decisions.
- Hindi text must not be clipped or overflow.
- Use cards sparingly and prioritize readability.

Use a sidebar for navigation and filters where appropriate.

Pages or sections:
1. डैशबोर्ड
2. लंबित आवेदन
3. समीक्षा इतिहास
4. सहायता एवं जानकारी

Use Streamlit components and custom CSS only where needed. Avoid fragile DOM manipulation and excessive CSS overrides.

Do not use placeholder charts that do not represent real stored data. Every chart or metric must have a clear purpose.

## 12. Authentication and Security

Provide a simple demo-only officer login suitable for the assignment.

Requirements:
- Use a configurable demo username and password.
- Never commit real passwords or API keys.
- Store secrets in environment variables or deployment secrets.
- Provide .env.example with placeholder values only.
- Use session state appropriately.
- Do not display credentials in the UI.
- Do not treat client-side UI state alone as authorization.
- Make it clear in the README that demo authentication is not production-grade identity management.
- Never use real citizen data.

If a complete authentication system would jeopardize the deadline, implement a minimal session-based demo login and document the limitation rather than pretending it is enterprise-secure.

## 13. Error Handling and Reliability

Handle:
- Missing API key.
- LLM timeout.
- API rate limits.
- Invalid model response.
- SQLite errors.
- Invalid application IDs.
- Empty filters.
- No matching applications.
- Duplicate decision submission.
- Missing or malformed seed data.

Show understandable Hindi error messages wherever practical.

Do not silently swallow exceptions. Log useful technical details without logging secrets or unnecessary personal data.

Keep the core dashboard and decision workflow usable when the LLM is unavailable.

## 14. Testing Requirements

Create and run tests for:

- Required document completeness.
- Missing-document detection.
- Inconsistent sample fields.
- Priority scoring and ordering.
- Empty or invalid application records.
- Approval with a reason.
- Rejection without a reason.
- Return for corrections with remarks.
- Audit-history creation.
- Dashboard metrics after a decision.
- Duplicate action handling.
- Invalid LLM output.
- Deterministic demo fallback.

Use synthetic fixtures and a temporary SQLite database for tests.

Do not require a real LLM API key to run the automated test suite.

Fix all failing tests before declaring completion.

## 15. README and Documentation

Write a clear, professional README.md containing:

1. Project name and overview.
2. Problem statement.
3. Intended users and why the tool is useful.
4. Main features.
5. Screenshots section, if screenshots can be captured.
6. Architecture diagram using Mermaid.
7. Technology stack and design decisions.
8. Data model and sample-data policy.
9. How deterministic validation works.
10. How AI-assisted review works.
11. Human-in-the-loop safeguards.
12. Setup instructions for Windows and common shells.
13. Environment variables.
14. How to run the application.
15. How to run tests.
16. Demo login setup.
17. Deployment instructions.
18. Known limitations and future improvements.

Explain why a deterministic rules layer is used for validation and prioritization, while an LLM is used for summaries and evidence-based explanations.

Clearly state that sample validation rules are illustrative and do not establish official government eligibility requirements.

## 16. Deployment Readiness

Prepare the application for deployment on Streamlit Community Cloud or another suitable platform.

Requirements:
- Provide requirements.txt.
- Include all necessary source files in the repository.
- Configure the application entry point.
- Document secrets setup.
- Ensure the app starts without a developer's local files or local absolute paths.
- Initialize the database and sample data safely on first run.
- Avoid reliance on an in-memory database for persistent decisions.
- Include a demo reset mechanism if practical, with confirmation before resetting.
- Do not expose credentials or API keys in logs or source code.

Do not claim that the app is live or deployed unless deployment has actually succeeded.

## 17. Implementation Order

Follow this order:

Phase 1: Inspect the workspace and create the application skeleton.

Phase 2: Create the fictional sample dataset, SQLite schema, and seed initialization.

Phase 3: Implement deterministic validation and priority scoring.

Phase 4: Build the Hindi dashboard, application list, filters, and detail view.

Phase 5: Implement the AI review service with structured output, API error handling, and clearly labeled demo fallback.

Phase 6: Implement final decision actions, persistence, and audit history.

Phase 7: Write and run automated tests.

Phase 8: Run the application locally, test critical workflows, inspect the UI, and fix problems.

Phase 9: Complete the README and deployment configuration.

Do not stop after generating the file structure or a design mockup.

## 18. Definition of Done

The project is complete only when:

- The app starts successfully.
- The Hindi dashboard displays fictional sample applications.
- Metrics are computed from actual stored data.
- Search and filters work.
- Priority ordering is explainable.
- Application details show real validation results from the sample records.
- AI review works with a configured supported API.
- Demo mode is clearly labeled and works without an API key.
- The AI response is schema-validated.
- Approve, reject, and return actions persist correctly.
- Required officer remarks are enforced.
- The audit history records decisions.
- The dashboard reflects updated statuses.
- Automated tests pass.
- The README explains local setup and deployment.
- No real citizen data or committed secrets exist.

## 19. Working Instructions

Start by inspecting the existing workspace. Preserve useful existing code if present.

Make practical decisions independently and explain significant trade-offs in the README.

Do not ask me to approve every minor implementation choice.

If a requirement cannot be completed, explain the limitation honestly and prioritize the most important working functionality.

After implementation, provide a concise completion report listing:
- Features implemented.
- Project structure.
- Commands used to run the app and tests.
- Test results.
- Environment variables required.
- Any known limitations.
- Exact steps I must perform manually to publish the GitHub repository and deploy the live app.

Begin implementation now. Build and verify the working application, not merely a plan.
