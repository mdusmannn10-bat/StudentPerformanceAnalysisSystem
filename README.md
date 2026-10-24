# 🎓 Student Performance Analysis System

> **A robust Python Flask & MySQL Data Analytics Application for Academic Records Management, Statistical Modeling (NumPy), Cohort & Subject Aggregation (Pandas), and Automated Visual Reporting (Matplotlib).**

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/Flask-3.1.3-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/MySQL-8.0%2B-orange.svg)](https://www.mysql.com/)
[![Test Suite](https://img.shields.io/badge/pytest-36%20passed%20%28100%25%29-brightgreen.svg)](https://docs.pytest.org/)
[![Status](https://img.shields.io/badge/Status-Submission%20Ready-success.svg)](#)

---

## 📋 Table of Contents
1. [Project Overview & Objectives](#1-project-overview--objectives)
2. [Key Features & Implemented Capabilities](#2-key-features--implemented-capabilities)
3. [Required Software & Prerequisites](#3-required-software--prerequisites)
4. [Project Directory Structure](#4-project-directory-structure)
5. [Windows & VS Code Setup Guide](#5-windows--vs-code-setup-guide)
   - [Virtual Environment Setup](#51-step-1-create-and-activate-virtual-environment)
   - [Dependency Installation](#52-step-2-install-dependencies)
   - [MySQL Database Initialization](#53-step-3-initialize-mysql-database)
   - [Environment Configuration](#54-step-4-configure-environment-variables)
6. [Application Startup Commands](#6-application-startup-commands)
7. [Web Application Navigation & Routes](#7-web-application-navigation--routes)
8. [REST API Documentation & Examples](#8-rest-api-documentation--examples)
9. [Data Analysis Methodology & Formulas](#9-data-analysis-methodology--formulas)
10. [Visualizations & Chart Descriptions](#10-visualizations--chart-descriptions)
11. [Automated Test Suite & Verification Results](#11-automated-test-suite--verification-results)
12. [Known Academic Limitations](#12-known-academic-limitations)
13. [Troubleshooting Guide (Windows & MySQL)](#13-troubleshooting-guide-windows--mysql)
14. [Deliverables Mapping (D1 – D8)](#14-deliverables-mapping-d1--d8)

---

## 1. Project Overview & Objectives

In academic institutions, evaluating student performance across multiple courses, cohorts, and examination iterations often relies on disconnected spreadsheets or manual record-keeping. This leads to computational errors, double-counting of maximum marks, delayed identification of struggling students, and lack of visual clarity for department chairs.

The **Student Performance Analysis System** (**Project 1** in the *Python Flask Data Analytics Projects* curriculum) solves these institutional bottlenecks:
- **Centralized Persistence:** Relational database in MySQL with primary/foreign keys, constraints, and cascading integrity.
- **Accurate Mathematical Modeling:** Clearly separates individual assessment results from final subject-level mastery and cumulative student performance, eliminating double-counted maximum marks.
- **Automated Grading & Rankings:** Standardized 7-tier letter grading scale (`A+` through `F`) with automatic backlog penalty and dense competition ranking.
- **Statistical Analytics:** NumPy-powered descriptive metrics (mean, median, standard deviation, variance, interquartile range).
- **Cohort Analysis:** Pandas-powered subject pass rates and section comparisons (Sections A, B, C).
- **At-Risk Diagnostic Tool:** Dynamic, threshold-configurable identification of students requiring mentoring with actionable remedial advice.
- **Publication-Grade Visualizations:** Five headless Matplotlib charts saved as image assets and embedded on dashboards.
- **Dual Accessibility:** Responsive Web UI for academic staff + JSON REST APIs for external integration.

---

## 2. Key Features & Implemented Capabilities

- **Student Lifecycle CRUD:** Add new students, view directory, filter by section, search by name or roll number, edit profiles, and delete records (with automatic marks cascade).
- **Marks Ledger CRUD:** Enter assessment scores with validation (`0 <= marks <= max_marks`), filter by student or subject, edit scores, and delete records.
- **Curriculum Subject Management:** Define courses with customizable maximum scores and passing marks.
- **Three-Tier Evaluation Model:** Distinguishes assessment scores &rarr; subject averages &rarr; overall student percentage.
- **Toppers Hall of Fame:** Displays top achievers with gold, silver, and bronze rank badges.
- **Academic Support Diagnostic:** Flags students scoring below a configurable threshold (e.g., $40\%$ or $50\%$) or holding subject backlogs, diagnosing exact failure causes.
- **Printable Student Transcript:** Official report card layout with `@media print` support for browser printing or saving as PDF.
- **JSON REST API Suite:** Standardized REST endpoints for programmatic automation and external testing via Postman or cURL.

---

## 3. Required Software & Prerequisites

Before setting up the project on Windows:
1. **Operating System:** Windows 10 or Windows 11 (64-bit).
2. **Python:** Python 3.10, 3.11, 3.12, or 3.14 (Ensure *"Add python.exe to PATH"* is checked during Python installation).
3. **Database:** MySQL Server 8.0+ (or MySQL Workbench / XAMPP with MySQL).
4. **Code Editor:** Visual Studio Code (VS Code) recommended with Python extension installed.

---

## 4. Project Directory Structure

```
StudentPerformanceAnalysisSystem/
│
├── config.py                 # Centralized configuration & environment loader
├── db.py                     # Safe MySQL connection manager & health check probe
├── analytics.py              # NumPy descriptive stats & Pandas aggregation engine
├── charts.py                 # Matplotlib visualization generation engine
├── app.py                    # Flask application, web controllers & REST API routes
│
├── schema.sql                # Complete MySQL DDL schema script
├── seed_data.sql             # Representative sample academic dataset
├── .env                      # Local environment credentials (excluded from Git/ZIP)
├── .env.example              # Template environment configuration file
├── .gitignore                # Git exclusions (credentials, caches, venv)
├── requirements.txt          # Python dependencies specification
│
├── static/
│   ├── css/
│   │   └── style.css         # Responsive styling & printable transcript stylesheet
│   └── charts/               # Generated Matplotlib chart images (.png)
│       ├── subject_average.png
│       ├── pass_fail.png
│       ├── marks_distribution.png
│       ├── subject_pass_rate.png
│       └── section_performance.png
│
├── templates/                # Jinja2 HTML templates
│   ├── layout.html           # Base layout with navigation and flash messages
│   ├── index.html            # Main dashboard with KPIs and chart gallery
│   ├── students.html         # Student directory, search, filter, and management
│   ├── add_student.html      # Enroll new student form
│   ├── edit_student.html     # Edit student profile form
│   ├── marks.html            # Assessment marks ledger with filters
│   ├── add_marks.html        # Record marks form
│   ├── edit_marks.html       # Edit marks form
│   ├── subjects.html         # Curriculum courses and add subject form
│   ├── analysis.html         # Rankings, Topper showcase & At-risk diagnostics
│   ├── subject_analysis.html # Subject-wise and section-wise analysis tables
│   └── student_report.html   # Individual academic transcript & printable report card
│
├── tests/                    # Automated testing suite (36 tests)
│   ├── __init__.py
│   ├── test_calculations.py  # Independent unit tests for grading & formulas (8 tests)
│   ├── test_analytics.py     # Analytics module & chart generation tests (5 tests)
│   ├── test_app.py           # Web routes & REST API integration tests (18 tests)
│   └── test_ui_routes.py     # Frontend page restructuring & navigation tab tests (5 tests)
│
└── docs/                     # Academic deliverables documentation (D1 - D8)
    ├── D1_Proposal_and_Requirements.md
    ├── D2_Database_Design.md
    ├── D4_D5_Analytics_and_Visualizations.md
    ├── D6_Testing_Report.md
    └── D7_D8_Final_Report_and_Demonstration.md
```

---

## 5. Windows & VS Code Setup Guide

Open **PowerShell** or **Command Prompt** in the project directory:
```powershell
cd "c:\Users\Mohammad Usman\Documents\StudentPerformanceAnalysisSystem"
```

### 5.1. Step 1: Create and Activate Virtual Environment
Create an isolated Python virtual environment:
```powershell
python -m venv .venv
```
Activate the environment in PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```
*(If PowerShell displays an `Execution_Policies` restriction, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then run the activate command again).*

Alternatively, you can run Python directly through the virtual environment executable without activating:
```powershell
.venv\Scripts\python.exe --version
```

### 5.2. Step 2: Install Dependencies
Install all required packages from `requirements.txt`:
```powershell
.venv\Scripts\pip.exe install -r requirements.txt
```

### 5.3. Step 3: Initialize MySQL Database
Make sure your MySQL service is running on your machine.
Open MySQL command line or MySQL Workbench and run:
```sql
CREATE DATABASE IF NOT EXISTS student_performance;
```
Now populate the schema and sample data using the provided SQL files:
```powershell
# Using MySQL CLI (enter your MySQL password when prompted):
mysql -u root -p student_performance < schema.sql
mysql -u root -p student_performance < seed_data.sql
```
*(Alternatively, open `schema.sql` followed by `seed_data.sql` inside MySQL Workbench and click the Execute button).*

### 5.4. Step 4: Configure Environment Variables
Create a file named `.env` in the root folder (or copy `.env.example`):
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_NAME=student_performance

SECRET_KEY=student-performance-system-secure-key-2026
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

SUPPORT_THRESHOLD=40.0
TOP_N=3
ASSESSMENT_AGGREGATION=AVERAGE
```
> ⚠️ **Security Notice:** Never commit `.env` containing your real MySQL password to Git. `.env` is already listed in `.gitignore`.

---

## 6. Application Startup Commands

### Method A: Direct Execution (Recommended for Windows)
```powershell
.venv\Scripts\python.exe app.py
```

### Method B: With Activated Virtual Environment
```powershell
.venv\Scripts\activate
python app.py
```

Upon successful startup, terminal output will display:
```
Database connectivity confirmed: Connected to MySQL Server 8.0.x
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```
Open your browser and navigate to: **`http://127.0.0.1:5000/`**

---

## 7. Web Application Navigation & Page Architecture

The application is structured into four intuitive primary pages, adhering to modern academic administration UX principles:

| Page | Primary Route | Page Name | Primary Capabilities |
|---|---|---|---|
| **Page A** | `/` | **Main Dashboard** | Executive institutional summary: 5 live KPI cards (Total Students, Total Subjects, Cohort Average %, Pass Rate %, Support Required count), Top Performers spotlight, Attention Courses alert, recent assessment activity preview, and quick shortcuts. |
| **Page B** | `/students` | **Student Management** | Searchable & filterable directory (by name, roll number, section), evaluated status badges, student enrollment form (`/add-student`), edit profile (`/edit-student/<id>`), and delete confirmation. |
| **Page B (Detail)** | `/student/<id>`, `/student-report` | **Student Profile & Transcript** | Dedicated student performance dossier: demographic cards, cumulative stats, letter grade, at-risk diagnosis, subject-by-subject assessment breakdown table, and one-click printable report card (`@media print`). |
| **Page C** | `/analysis`, `/analytics` | **Analytics & Reports Hub** | Centralized analytical reporting hub with 4 interactive, tabbed workspaces: <br>• **Tab 1 (Visual Analytics):** All 5 publication-ready Matplotlib charts with descriptions and interpretation notes.<br>• **Tab 2 (Rankings & Toppers):** Top-3 podium cards and dense institutional competition ranking table.<br>• **Tab 3 (Academic Support):** Dynamic threshold filter ($40\%$, $50\%$, $60\%$) diagnosing at-risk students, specific failed subjects, and remediation strategies.<br>• **Tab 4 (Summaries):** Curriculum course summaries and cohort (Section A, B, C) comparison tables. |
| **Page D** | `/subjects` | **Curriculum Subjects** | Course catalog, maximum and passing mark thresholds, active assessment counts, and new subject creation modal. |
| **Page D (Ledger)** | `/marks` | **Marks Ledger** | Centralized ledger of all assessment records with student/subject filtering, range validation (`0 <= marks <= max_marks`), add marks (`/add-marks`), edit (`/edit-marks/<id>`), and delete. |

---

## 8. REST API Documentation & Examples

All API endpoints return standard JSON responses with HTTP status codes:
- `200 OK`: Successful retrieval/operation.
- `201 Created`: Successful resource creation.
- `400 Bad Request`: Validation failure or duplicate constraint violation.
- `404 Not Found`: Requested ID does not exist.
- `503 Service Unavailable`: Database unreachable (Health check).

### 8.1. System Health Check
- **`GET /api/health`**
  ```powershell
  curl http://127.0.0.1:5000/api/health
  ```
  **Response (`200 OK`):**
  ```json
  {
    "database": {
      "connected": true,
      "message": "Connected to MySQL Server 8.0.46"
    },
    "status": "healthy",
    "system": "Student Performance Analysis System"
  }
  ```

### 8.2. Student Management Endpoints
- **`GET /api/students`** &ndash; List all students.
- **`POST /api/students`** &ndash; Create a student profile.
  ```json
  // Request Body:
  {"roll_no": "CSE011", "full_name": "Rohith Varma", "section": "A"}
  ```
- **`GET /api/students/<int:id>`** &ndash; Retrieve single student details.
- **`PUT /api/students/<int:id>`** &ndash; Update student profile.
- **`DELETE /api/students/<int:id>`** &ndash; Delete student (automatically cascades associated marks).

### 8.3. Assessment Marks Endpoints
- **`GET /api/marks?student_id=1&subject_id=2`** &ndash; Query marks records with optional filters.
- **`POST /api/marks`** &ndash; Insert new marks record.
  ```json
  // Request Body:
  {"student_id": 1, "subject_id": 1, "assessment": "Internal 1", "marks_obtained": 88.5}
  ```
- **`PUT /api/marks/<int:id>`** &ndash; Update marks obtained or assessment name.
- **`DELETE /api/marks/<int:id>`** &ndash; Delete marks entry.

### 8.4. Analytics Endpoints
- **`GET /api/analytics/summary`** &ndash; NumPy descriptive statistics:
  ```json
  {
    "success": true,
    "data": {
      "total_records": 40,
      "mean_marks": 70.9,
      "median_marks": 78.0,
      "std_dev": 21.43,
      "variance": 459.29,
      "minimum_marks": 28.0,
      "maximum_marks": 96.0,
      "q1_marks": 49.5,
      "q3_marks": 89.25,
      "iqr_marks": 39.75
    }
  }
  ```
- **`GET /api/analytics/subjects`** &ndash; Course-wise pass rates and averages.
- **`GET /api/analytics/sections`** &ndash; Cohort-wise averages and pass percentages.
- **`GET /api/analytics/performance`** &ndash; Class rankings, letter grades, and pass/fail statuses.
- **`GET /api/analytics/toppers?limit=3`** &ndash; Top $N$ passed students.
- **`GET /api/analytics/support-needed?threshold=40.0`** &ndash; Students below threshold or holding backlogs.
- **`POST /api/charts/refresh`** &ndash; Triggers dynamic regeneration of all five charts.

---

## 9. Data Analysis Methodology & Formulas

### 9.1. Three-Tier Evaluation Model
1. **Assessment Level:** Granular record ($m_{i,s,a}$). Status = `Pass` if $m_{i,s,a} \ge \text{PassMarks}_s$.
2. **Subject Level (Course Mastery):** When multiple assessments are recorded for subject $s$, final subject marks are aggregated as the arithmetic mean ($\bar{m}_{i,s}$). The subject is passed if $\bar{m}_{i,s} \ge \text{PassMarks}_s$.
3. **Overall Student Level:**
   $$\text{Total Marks Obtained} = \sum_{\text{distinct subjects } s} \bar{m}_{i,s}$$
   $$\text{Total Maximum Marks} = \sum_{\text{distinct subjects } s} \text{MaxMarks}_s$$
   $$\text{Overall Percentage} = \left(\frac{\text{Total Marks Obtained}}{\text{Total Maximum Marks}}\right) \times 100$$

### 9.2. Letter Grading Scale
$$\text{Grade} = \begin{cases} 
\text{F} & \text{if student failed } \ge 1 \text{ subject (Backlog penalty)} \\
\text{A+} & \text{if Percentage} \ge 90.0\% \\
\text{A} & \text{if } 80.0\% \le \text{Percentage} < 90.0\% \\
\text{B} & \text{if } 70.0\% \le \text{Percentage} < 80.0\% \\
\text{C} & \text{if } 60.0\% \le \text{Percentage} < 70.0\% \\
\text{D} & \text{if } 50.0\% \le \text{Percentage} < 60.0\% \\
\text{E} & \text{if } 35.0\% \le \text{Percentage} < 50.0\% \\
\text{F} & \text{if Percentage} < 35.0\%
\end{cases}$$

### 9.3. Pass / Fail Status
A student receives an overall status of **Pass** if and only if they cleared **every** attempted subject. If any subject average is below the passing mark, the student receives a status of **Fail** and their backlogs are detailed.

---

## 10. Visualizations & Chart Descriptions

All charts are generated by [`charts.py`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/charts.py) using **Matplotlib** with headless `Agg` rendering:

1. **Subject-Wise Average Academic Performance (`subject_average.png`):** Bar chart auto-scaled to actual course maximum marks with passing benchmark line.
2. **Overall Student Clearance vs. Failure Ratio (`pass_fail.png`):** Styled donut chart showing cumulative clearance vs. failure proportions.
3. **Assessment Marks Frequency Distribution (`marks_distribution.png`):** 10-bin histogram displaying score clustering, with vertical Mean ($\mu$) and Median ($\tilde{x}$) indicator lines.
4. **Subject-Wise Examination Pass Percentages (`subject_pass_rate.png`):** Bar chart highlighting course clearance rates across subjects.
5. **Class Section Academic Performance Comparison (`section_performance.png`):** Multi-color bar chart comparing cohort averages across sections.

---

## 11. Automated Test Suite & Verification Results

The test suite contains **36 automated test cases** covering calculation formulas, edge cases, error validation, UI route loading, tab switching, and REST APIs.

Run tests using:
```powershell
.venv\Scripts\pytest.exe -v
```

### Verified Test Run Output:
```
============================= test session starts =============================
platform win32 -- Python 3.14.8, pytest-9.1.1, pluggy-1.7.0 -- .venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Mohammad Usman\Documents\StudentPerformanceAnalysisSystem
collected 36 items

tests/test_analytics.py::TestAnalyticsModule::test_charts_generation PASSED [  2%]
tests/test_analytics.py::TestAnalyticsModule::test_marks_summary_numpy_metrics PASSED [  5%]
tests/test_analytics.py::TestAnalyticsModule::test_overall_kpis PASSED   [  8%]
tests/test_analytics.py::TestAnalyticsModule::test_section_summary_pandas PASSED [ 11%]
tests/test_analytics.py::TestAnalyticsModule::test_subject_summary_pandas PASSED [ 13%]
tests/test_app.py::TestAppRoutesAndAPI::test_add_marks_get PASSED        [ 16%]
tests/test_app.py::TestAppRoutesAndAPI::test_add_marks_validation_exceeds_max PASSED [ 19%]
tests/test_app.py::TestAppRoutesAndAPI::test_add_marks_validation_negative PASSED [ 22%]
tests/test_app.py::TestAppRoutesAndAPI::test_add_student_get PASSED      [ 25%]
tests/test_app.py::TestAppRoutesAndAPI::test_add_student_validation_error PASSED [ 27%]
tests/test_app.py::TestAppRoutesAndAPI::test_analysis_route PASSED       [ 30%]
tests/test_app.py::TestAppRoutesAndAPI::test_api_analytics_endpoints PASSED [ 33%]
tests/test_app.py::TestAppRoutesAndAPI::test_api_health_failure PASSED   [ 36%]
tests/test_app.py::TestAppRoutesAndAPI::test_api_health_success PASSED   [ 38%]
tests/test_app.py::TestAppRoutesAndAPI::test_api_students_crud_lifecycle PASSED [ 41%]
tests/test_app.py::TestAppRoutesAndAPI::test_api_students_get PASSED     [ 44%]
tests/test_app.py::TestAppRoutesAndAPI::test_api_subjects_get PASSED     [ 47%]
tests/test_app.py::TestAppRoutesAndAPI::test_home_dashboard_route PASSED [ 50%]
tests/test_app.py::TestAppRoutesAndAPI::test_marks_list_route PASSED     [ 52%]
tests/test_app.py::TestAppRoutesAndAPI::test_student_report_route PASSED [ 55%]
tests/test_app.py::TestAppRoutesAndAPI::test_students_list_route PASSED  [ 58%]
tests/test_app.py::TestAppRoutesAndAPI::test_subject_analysis_route PASSED [ 61%]
tests/test_app.py::TestAppRoutesAndAPI::test_subjects_route PASSED       [ 63%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_different_subject_max_marks PASSED [ 66%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_empty_dataframe PASSED [ 69%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_grade_boundaries_no_backlogs PASSED [ 72%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_grade_with_backlog_penalty PASSED [ 75%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_multiple_assessments_aggregation_and_no_double_counting PASSED [ 77%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_student_without_marks PASSED [ 80%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_topper_and_support_needed_logic PASSED [ 83%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_zero_marks_and_pass_mark_boundary PASSED [ 86%]
tests/test_ui_routes.py::TestUIRoutesAndTabs::test_analytics_and_reports_hub_tabs PASSED [ 88%]
tests/test_ui_routes.py::TestUIRoutesAndTabs::test_main_dashboard_page PASSED [ 91%]
tests/test_ui_routes.py::TestUIRoutesAndTabs::test_student_management_directory PASSED [ 94%]
tests/test_ui_routes.py::TestUIRoutesAndTabs::test_student_report_card_routes PASSED [ 97%]
tests/test_ui_routes.py::TestUIRoutesAndTabs::test_subjects_and_marks_pages PASSED [100%]

============================= 36 passed in 21.83s =============================
```

---

## 12. Known Academic Limitations

1. **Subject Weightage:** In the current version, all subjects contribute equally to total percentage based on their raw maximum marks. Course credit weighting (e.g. 4-credit vs 2-credit courses) is not applied.
2. **Batch Assessment Upload:** Marks are currently recorded individually or via REST API. Batch CSV bulk import is a planned enhancement for the next version.
3. **Predictive Analytics:** Current calculations are descriptive. Machine learning predictive forecasting of semester results belongs to the advanced project tier.

---

## 13. Troubleshooting Guide (Windows & MySQL)

### Issue 1: `mysql.connector.errors.ProgrammingError: 1045 (28000): Access denied for user 'root'@'localhost'`
- **Cause:** Incorrect MySQL root password in `.env`.
- **Solution:** Open `.env` and verify `DB_PASSWORD=your_actual_password`. Ensure no trailing spaces exist.

### Issue 2: `mysql.connector.errors.DatabaseError: 1049 (42000): Unknown database 'student_performance'`
- **Cause:** Database not yet created in MySQL.
- **Solution:** Open MySQL and run `CREATE DATABASE student_performance;` then re-import `schema.sql`.

### Issue 3: `Execution of scripts is disabled on this system` (PowerShell)
- **Cause:** Windows PowerShell script execution policy prevents running `.venv\Scripts\Activate.ps1`.
- **Solution:** Run PowerShell as Administrator and execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, or simply run `.venv\Scripts\python.exe app.py` directly without activating.

---

## 14. Deliverables Mapping (D1 – D8)

| Code | Official Deliverable | Repository Path |
|---|---|---|
| **D1** | Proposal and Requirements | [`docs/D1_Proposal_and_Requirements.md`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/docs/D1_Proposal_and_Requirements.md) |
| **D2** | Database Design & SQL Scripts | [`docs/D2_Database_Design.md`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/docs/D2_Database_Design.md), [`schema.sql`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/schema.sql), [`seed_data.sql`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/seed_data.sql) |
| **D3** | Flask Backend & REST APIs | [`app.py`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/app.py), [`config.py`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/config.py), [`db.py`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/db.py) |
| **D4** | Data Analysis (Pandas & NumPy) | [`analytics.py`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/analytics.py), [`docs/D4_D5_Analytics_and_Visualizations.md`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/docs/D4_D5_Analytics_and_Visualizations.md) |
| **D5** | Visualizations (Matplotlib Charts)| [`charts.py`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/charts.py), [`static/charts/`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/static/charts/) |
| **D6** | Testing Report & Evidence | [`tests/`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/tests/), [`docs/D6_Testing_Report.md`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/docs/D6_Testing_Report.md) |
| **D7** | Documentation & User Guide | [`README.md`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/README.md), [`docs/`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/docs/) |
| **D8** | Final Demonstration Plan | [`docs/D7_D8_Final_Report_and_Demonstration.md`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/docs/D7_D8_Final_Report_and_Demonstration.md) |
