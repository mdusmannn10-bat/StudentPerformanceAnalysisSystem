# D1. Project Proposal & Requirements Specification

## 1. Project Title
**Student Performance Analysis System**  
*Academic Data Analytics and Performance Evaluation Engine*

---

## 2. Problem Statement
Educational institutions generate large volumes of assessment records across multiple academic semesters and subjects. However, academic administrators and faculty often face significant hurdles:
- **Manual Computation Overhead:** Manually calculating total marks, averages, percentages, grades, and class ranks is time-consuming and error-prone.
- **Delayed Academic Intervention:** Identifying struggling students who need remedial coaching or academic counseling often happens too late—typically after final examination failures.
- **Lack of Cohort & Subject Visibility:** Faculty lack instant visual and statistical insights regarding which subjects have low pass rates, high difficulty, or significant grade variance across sections.
- **Fragmented Records:** Without a normalized relational database, academic records suffer from duplication, referential integrity violations, and inconsistent grading metrics.

The **Student Performance Analysis System** addresses these challenges by delivering an automated, Flask-powered web application and RESTful backend integrated with a normalized MySQL database, automated statistical calculations (NumPy), aggregations (Pandas), and visualization generation (Matplotlib).

---

## 3. Objectives
1. **Academic Record Lifecycle Management:** Provide complete CRUD (Create, Read, Update, Delete) management for student profiles, curriculum subjects, and assessment marks.
2. **Standardized Grading & Ranking Engine:** Automate calculation of totals, averages, percentages, letter grades (A+ to F), and institutional ranks based on explicitly defined, transparent rules.
3. **Cohort & Subject Analytics:** Leverage Pandas to compute subject-wise pass rates, min/max scores, and class section performance comparisons.
4. **Descriptive Statistical Modeling:** Leverage NumPy to compute distribution metrics: mean, median, standard deviation, interquartile range (Q1, Q3), and variance.
5. **Early Warning & Intervention:** Provide a configurable threshold-based diagnostic tool to pinpoint students at academic risk or holding subject backlogs with concrete remedial action recommendations.
6. **Publication-Ready Visual Reporting:** Automatically generate and render publication-quality Matplotlib charts (bar charts, donut charts, distribution histograms).
7. **Dual Interface Accessibility:** Deliver both a responsive web interface for academic coordinators and a JSON REST API for programmatic integration.

---

## 4. Scope and Boundaries
### In Scope:
- Multi-section student management (e.g., Section A, Section B, Section C).
- Configurable curriculum courses with customizable maximum and passing thresholds.
- Internal assessment records and multi-subject mark ledgers.
- Statistical summarization via NumPy and Pandas.
- Configurable academic support threshold filter (e.g., `< 40%` or `< 50%` or failing any subject).
- High-resolution Matplotlib charts saved as assets and served on dashboards.
- Comprehensive REST APIs for all entities and analytical metrics.
- Printable individual student report card / transcript.

### Out of Scope:
- Real-time automated proctoring or online examination submission.
- Payment gateway integration for tuition fee processing.
- Long-term machine learning grade prediction (scoped for Advanced project tier).

---

## 5. Stakeholder & User Roles
| Role | Responsibilities | Primary Interface |
|---|---|---|
| **Academic Administrator** | Sets up subjects, creates student accounts, manages sections, and inspects institutional KPIs. | Web Dashboard, Subject Management |
| **Faculty / Evaluator** | Records, modifies, and reviews assessment marks; reviews class section performance and subject pass rates. | Marks Ledger, Class Analysis |
| **Academic Counselor** | Inspects the At-Risk / Support Needed list to schedule remedial coaching and student mentoring. | Performance & Topper Analysis |
| **Student** | Views personal academic transcript, subject breakdown, letter grade, and rank. | Student Report Card |
| **System Integrator** | Connects external institutional software or mobile apps via RESTful APIs. | JSON REST Endpoints |

---

## 6. Functional Requirements
- **FR-1 Student Profile CRUD:** Ability to add, view, search, edit, and delete student records with unique roll numbers.
- **FR-2 Marks Ledger CRUD:** Ability to record, update, view, and delete assessment marks with strict range checking (`0 <= marks <= max_marks`).
- **FR-3 Subject Management:** Ability to define courses with positive maximum marks and non-negative pass marks (`pass_marks <= max_marks`).
- **FR-4 Descriptive Analytics:** Compute mean, median, standard deviation, and IQR across all marks.
- **FR-5 Performance & Ranking:** Calculate total marks, average, percentage, letter grade, and dense competition rank.
- **FR-6 Topper Showcase:** Automatically surface top $N$ passing students ordered by percentage.
- **FR-7 At-Risk Intervention:** Filter and display students falling below a configurable threshold or possessing subject backlogs.
- **FR-8 Analytical Visualizations:** Serve at least 3 distinct Matplotlib charts displaying subject averages, pass/fail ratios, and score distribution.

---

## 7. Assumptions and Constraints
1. **Academic Honesty & Data Privacy:** All records used in demonstrations represent synthetic, institution-approved sample data.
2. **Environment Configuration:** Database credentials are securely loaded from `.env` and never hardcoded.
3. **Database Engine:** MySQL 8.0+ running InnoDB with Foreign Key constraints and `ON DELETE CASCADE`.
4. **Python Version:** Python 3.10+ with Flask, Pandas, NumPy, and Matplotlib.
