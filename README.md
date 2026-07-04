# Code Scanner Dashboard

A full-stack **Application Security Code Scanner Dashboard** built with **FastAPI, Bandit, Semgrep, SQLite, Chart.js, ReportLab, GitHub Actions, and Docker**.

This project helps users scan Python source code for common security issues such as hardcoded secrets, command injection, unsafe deserialization, weak cryptography, insecure subprocess usage, SQL injection patterns, disabled SSL verification, and other risky coding practices.

Users can scan the included vulnerable sample project or upload their own `.py` file and instantly view findings through a clean web dashboard.

---

## Features

```text
✅ Python security scanning using Bandit
✅ Static code analysis using Semgrep
✅ Upload and scan custom .py files
✅ Auto-delete uploaded files after scanning
✅ File type validation
✅ File size limit
✅ Risk Score calculation
✅ Vulnerability priority levels: P0, P1, P2, P3
✅ Severity dashboard: Critical, High, Medium, Low
✅ Scan history using SQLite
✅ Clear scan history option
✅ Export reports in CSV, JSON, and PDF formats
✅ Responsive UI for laptop, tablet, and mobile
✅ Dark mode support
✅ Dockerized application
✅ GitHub Actions CI security scan workflow
```

---

## Project Overview

The goal of this project is to provide a simple and practical **Secure SDLC / AppSec automation tool**.

In real-world software development, security checks should happen early in the development lifecycle. This dashboard demonstrates how security tools like **Bandit** and **Semgrep** can be integrated into a web application to scan code, classify vulnerabilities, calculate risk, and export reports.

---

## Tech Stack

```text
Backend        : FastAPI
Frontend       : HTML, CSS, JavaScript, Jinja2
Security Tools : Bandit, Semgrep
Database       : SQLite
Reports        : CSV, JSON, PDF using ReportLab
Charts         : Chart.js
Container      : Docker
CI/CD          : GitHub Actions
Language       : Python
```

---

## Architecture

```text
User
 |
 |-- Opens Dashboard
 |
FastAPI Web App
 |
 |-- Serves HTML/CSS/JS dashboard
 |-- Accepts uploaded .py file
 |-- Runs security scanners
 |
Security Scanner Layer
 |
 |-- Bandit Scan
 |-- Semgrep Scan
 |
Result Processing Layer
 |
 |-- Normalize findings
 |-- Count severity
 |-- Assign priority
 |-- Calculate risk score
 |
Storage Layer
 |
 |-- SQLite scan history
 |
Report Layer
 |
 |-- CSV Export
 |-- JSON Export
 |-- PDF Export
```

---

## Folder Structure

```text
code-scanner-dashboard/
│
├── app.py
├── scanner.py
├── database.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
│
├── sample_project/
│   └── test_vulnerable_code.py
│
├── static/
│   └── style.css
│
├── templates/
│   └── dashboard.html
│
├── .github/
│   └── workflows/
│       └── security-scan.yml
│
└── README.md
```

---

## How It Works

```text
1. User clicks Start Sample Scan or uploads a .py file.
2. FastAPI receives the request.
3. Bandit scans the target code.
4. Semgrep scans the same target code.
5. Results are combined and normalized.
6. Each issue is assigned severity and priority.
7. Risk score is calculated.
8. Findings are shown on the dashboard.
9. Scan summary is saved in SQLite.
10. User can export the report as CSV, JSON, or PDF.
```

---

## Risk Score Logic

The dashboard calculates a risk score from `0` to `100`.

```text
Critical = 10 points
High     = 7 points
Medium   = 4 points
Low      = 1 point
```

Formula:

```text
Risk Score = min((Critical × 10) + (High × 7) + (Medium × 4) + (Low × 1), 100)
```

Risk status:

```text
0        → Clean
1 - 19   → Low Risk
20 - 49  → Medium Risk
50 - 79  → High Risk
80 - 100 → Critical Risk
```

---

## Priority Mapping

```text
Critical → P0
High     → P1
Medium   → P2
Low      → P3
Unknown  → P4
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/code-scanner-dashboard.git
cd code-scanner-dashboard
```

Replace `YOUR_USERNAME` with your GitHub username.

---

### 2. Create Virtual Environment

For Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

For Linux/Mac:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run the Application

```bash
uvicorn app:app --reload
```

Open in browser:

```text
http://127.0.0.1:8000
```

---

## Usage

### Start Sample Scan

Click:

```text
Start Sample Scan
```

This scans the intentionally vulnerable file inside:

```text
sample_project/test_vulnerable_code.py
```

This file is included only for testing how the scanner works.

---

### Upload and Scan a Python File

Click:

```text
Upload & Scan
```

Then upload any `.py` file.

Rules:

```text
Only .py files are supported
Maximum file size: 2 MB
Uploaded file is deleted automatically after scanning
```

---

### Export Reports

Click:

```text
Export
```

Available formats:

```text
CSV Report
JSON Report
PDF Report
```

---

### Clear Scan History

Click:

```text
Clear History
```

This removes all saved scan records from the SQLite database.

---

## Docker Setup

The project can also run inside Docker.

### 1. Build Docker Image

```bash
docker build -t secure-code-scanner .
```

### 2. Run Docker Container

```bash
docker run --rm -p 8000:8000 secure-code-scanner
```

Open:

```text
http://127.0.0.1:8000
```

---

## GitHub Actions CI

This project includes a GitHub Actions workflow:

```text
.github/workflows/security-scan.yml
```

It runs automatically on:

```text
push
pull_request
manual workflow dispatch
```

The CI pipeline performs:

```text
Bandit scan
Semgrep scan
Security report generation
Artifact upload
```

The intentionally vulnerable `sample_project/` is excluded from CI scanning because it is only used for demo testing.

---

## Security Tools Used

### Bandit

Bandit is used to find Python security issues such as:

```text
Hardcoded passwords
Use of eval
Use of exec
Unsafe subprocess usage
Shell injection risks
Weak cryptographic functions
Insecure temporary file usage
```

### Semgrep

Semgrep is used for pattern-based static analysis and can detect:

```text
Command injection patterns
SQL injection patterns
Dangerous API usage
Framework-specific security issues
Unsafe code practices
```

---

## API Routes

```text
GET  /              → Dashboard home
GET  /scan          → Scan sample project
POST /upload        → Upload and scan .py file
GET  /export/csv    → Export CSV report
GET  /export/json   → Export JSON report
GET  /export/pdf    → Export PDF report
GET  /clear-history → Clear scan history
```

---

## Requirements

```text
fastapi
uvicorn
jinja2
bandit
semgrep
reportlab
requests
pyyaml
flask
python-multipart
```

---

## Example Vulnerabilities Detected

```text
Hardcoded password
Hardcoded API key
Command injection
subprocess with shell=True
Use of eval()
Use of exec()
Unsafe pickle deserialization
Unsafe yaml.load()
SQL injection pattern
Weak MD5 hashing
Weak SHA1 hashing
Insecure random token generation
SSL verification disabled
Flask debug mode enabled
Insecure temporary file creation
Assert used for security check
```

---

## Screenshots

Add screenshots after uploading the project.

Suggested folder:

```text
assets/
```

Suggested screenshots:

```text
assets/dashboard-light.png
assets/dashboard-dark.png
assets/mobile-view.png
assets/export-report.png
assets/upload-scan.png
```

Example Markdown:

```markdown
![Dashboard](assets/dashboard-light.png)
![Dark Mode](assets/dashboard-dark.png)
![Mobile View](assets/mobile-view.png)
```

---

## Development Commands

Run locally:

```bash
uvicorn app:app --reload
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Build Docker image:

```bash
docker build -t secure-code-scanner .
```

Run Docker container:

```bash
docker run --rm -p 8000:8000 secure-code-scanner
```

Check Docker images:

```bash
docker images
```

Check running containers:

```bash
docker ps
```

Stop a running container:

```bash
docker stop <container_id>
```

---

## Important Notes

```text
This project is for educational and demonstration purposes.
The included sample_project contains intentionally vulnerable code.
Do not use the sample vulnerable code in production.
Uploaded files are deleted after scanning for better privacy.
```

---

## Future Improvements

```text
Support ZIP project upload
Support JavaScript/TypeScript scanning
Add authentication
Add user-based scan history
Add vulnerability remediation suggestions
Add SARIF export
Add Docker Compose
Deploy to cloud
```

---

## Author

```text
Kommu Hari Kishan
B.Tech Mathematics and Computing
IIT Patna
```

---

## Project Status

```text
Completed:
Dashboard
Bandit integration
Semgrep integration
Upload and scan
Risk score
Priority system
Export reports
Scan history
Clear history
Responsive UI
Dark mode
Docker
GitHub Actions CI
```

---

## License

This project is open-source and available for learning, portfolio, and demonstration purposes.
