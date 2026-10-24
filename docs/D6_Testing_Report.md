# D6. Quality Assurance & Testing Report

## 1. Test Strategy Overview
The testing suite for the **Student Performance Analysis System** incorporates both **Unit Testing** (via Python's built-in `unittest` framework) and **Integration Testing** (via `pytest` and Flask's test client). It systematically covers:
- Standard inputs and normal workflows
- Boundary values (e.g., minimum pass mark of 35.0, maximum mark of 100.0, zero score)
- Invalid inputs (negative scores, scores exceeding max marks, missing required fields, non-numeric values)
- Referential integrity & database constraints (unique roll numbers, duplicate assessment records)
- REST API response schemas, status codes, and JSON payloads
- Isolated unit calculations independent of live MySQL
- Multi-assessment aggregation and backlog detection

---

## 2. Test Cases Specification Matrix (31 Automated Test Cases)

| Test ID | Test File | Target Component | Input / Scenario | Expected Outcome | Result |
|---|---|---|---|---|---|
| **TC-01** | `test_calculations.py` | `calculate_grade` | Standard grade boundaries (0.0 to 100.0) | Correct letter grade (A+, A, B, C, D, E, F) | **PASS** |
| **TC-02** | `test_calculations.py` | `calculate_grade` | Score = 96.0%, but holding 1 backlog | Returns `'F'` (Backlog penalty) | **PASS** |
| **TC-03** | `test_calculations.py` | `compute_student_performance_from_df` | Empty DataFrame | Returns empty list `[]` without error | **PASS** |
| **TC-04** | `test_calculations.py` | `compute_student_performance_from_df` | Student without marks records | Status: `"No Marks Yet"`, Grade: `"N/A"`, Rank: `"-"` | **PASS** |
| **TC-05** | `test_calculations.py` | `compute_student_performance_from_df` | Zero score (0.0 / 100.0) | Status: `"Fail"`, Grade: `"F"` | **PASS** |
| **TC-06** | `test_calculations.py` | `compute_student_performance_from_df` | Exact pass mark (35.0 / 100.0) | Status: `"Pass"`, Grade: `"E"` | **PASS** |
| **TC-07** | `test_calculations.py` | `compute_student_performance_from_df` | Exact maximum score (100.0 / 100.0) | Status: `"Pass"`, Grade: `"A+"` | **PASS** |
| **TC-08** | `test_calculations.py` | Multi-Assessment Aggregation | 2 assessments: 30 & 70 out of 100 | Average = 50.0/100, Pass, max total not doubled | **PASS** |
| **TC-09** | `test_calculations.py` | Differing Subject Max Marks | Subject 1 out of 50, Subject 2 out of 100 | Total max = 150, correct normalized percentage | **PASS** |
| **TC-10** | `test_calculations.py` | Toppers & Support Diagnostics | 3-student synthetic dataset | Proper rank sorting, at-risk diagnosis & advice | **PASS** |
| **TC-11** | `test_analytics.py` | `get_marks_summary` | Evaluates assessment marks array | Returns Mean, Median, StdDev, Variance, IQR | **PASS** |
| **TC-12** | `test_analytics.py` | `get_subject_summary` | Course-wise Pandas aggregation | Correct pass rate, pass count, fail count | **PASS** |
| **TC-13** | `test_analytics.py` | `get_section_summary` | Cohort-wise Pandas aggregation | Student counts, average percentage, pass rate | **PASS** |
| **TC-14** | `test_analytics.py` | `get_overall_kpis` | Summary KPIs for dashboard | Total evaluated, pass rate, top student score | **PASS** |
| **TC-15** | `test_analytics.py` | `generate_all_charts` | Matplotlib chart generation | 5 valid PNG image files generated on disk | **PASS** |
| **TC-16** | `test_app.py` | `GET /` | Load dashboard | HTTP 200, renders KPIs and visual charts | **PASS** |
| **TC-17** | `test_app.py` | `GET /students` | Load student directory | HTTP 200, renders student profiles table | **PASS** |
| **TC-18** | `test_app.py` | `GET /add-student` | Load add student form | HTTP 200, form input fields present | **PASS** |
| **TC-19** | `test_app.py` | `POST /add-student` | Missing required fields | HTTP 400 Bad Request, rejection message | **PASS** |
| **TC-20** | `test_app.py` | `GET /marks` | Load assessment ledger | HTTP 200, marks table rendered | **PASS** |
| **TC-21** | `test_app.py` | `GET /add-marks` | Load record marks form | HTTP 200, dropdowns populated | **PASS** |
| **TC-22** | `test_app.py` | `POST /add-marks` | Negative marks (`-5.0`) | HTTP 400 Bad Request, rejection message | **PASS** |
| **TC-23** | `test_app.py` | `POST /add-marks` | Marks > Max (`150` on 100 max) | HTTP 400 Bad Request, rejection message | **PASS** |
| **TC-24** | `test_app.py` | `GET /subjects` | Load subjects page | HTTP 200, course table rendered | **PASS** |
| **TC-25** | `test_app.py` | `GET /analysis` | Query `?threshold=45` | HTTP 200, renders Topper showcase & diagnostics | **PASS** |
| **TC-26** | `test_app.py` | `GET /subject-analysis` | Load course & cohort analytics | HTTP 200, renders summary tables | **PASS** |
| **TC-27** | `test_app.py` | `GET /student-report` | Valid student ID (`?student_id=1`) | HTTP 200, renders academic transcript | **PASS** |
| **TC-28** | `test_app.py` | `GET /api/health` | Health probe succeeds | HTTP 200, `{status: "healthy", connected: true}` | **PASS** |
| **TC-29** | `test_app.py` | `GET /api/health` (Mocked) | Health probe fails | HTTP 503 Service Unavailable, safe error message | **PASS** |
| **TC-30** | `test_app.py` | Student API CRUD Lifecycle | Create, retrieve, update, delete | HTTP 201 -> 200 -> 200 -> 200 -> 404 (with cleanup) | **PASS** |
| **TC-31** | `test_app.py` | Analytics API Endpoints | Summary, subjects, sections, toppers | All endpoints return HTTP 200 and valid JSON | **PASS** |

---

## 3. Test Execution Output Evidence
Executed via:
```powershell
.venv\Scripts\pytest.exe -v
```

### Complete Test Runner Output:
```
============================= test session starts =============================
platform win32 -- Python 3.14.8, pytest-9.1.1, pluggy-1.7.0 -- .venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Mohammad Usman\Documents\StudentPerformanceAnalysisSystem
collecting ... collected 31 items

tests/test_analytics.py::TestAnalyticsModule::test_charts_generation PASSED [  3%]
tests/test_analytics.py::TestAnalyticsModule::test_marks_summary_numpy_metrics PASSED [  6%]
tests/test_analytics.py::TestAnalyticsModule::test_overall_kpis PASSED   [  9%]
tests/test_analytics.py::TestAnalyticsModule::test_section_summary_pandas PASSED [ 12%]
tests/test_analytics.py::TestAnalyticsModule::test_subject_summary_pandas PASSED [ 16%]
tests/test_app.py::TestAppRoutesAndAPI::test_add_marks_get PASSED        [ 19%]
tests/test_app.py::TestAppRoutesAndAPI::test_add_marks_validation_exceeds_max PASSED [ 22%]
tests/test_app.py::TestAppRoutesAndAPI::test_add_marks_validation_negative PASSED [ 25%]
tests/test_app.py::TestAppRoutesAndAPI::test_add_student_get PASSED      [ 29%]
tests/test_app.py::TestAppRoutesAndAPI::test_add_student_validation_error PASSED [ 32%]
tests/test_app.py::TestAppRoutesAndAPI::test_analysis_route PASSED       [ 35%]
tests/test_app.py::TestAppRoutesAndAPI::test_api_analytics_endpoints PASSED [ 38%]
tests/test_app.py::TestAppRoutesAndAPI::test_api_health_failure PASSED   [ 41%]
tests/test_app.py::TestAppRoutesAndAPI::test_api_health_success PASSED   [ 45%]
tests/test_app.py::TestAppRoutesAndAPI::test_api_students_crud_lifecycle PASSED [ 48%]
tests/test_app.py::TestAppRoutesAndAPI::test_api_students_get PASSED     [ 51%]
tests/test_app.py::TestAppRoutesAndAPI::test_api_subjects_get PASSED     [ 54%]
tests/test_app.py::TestAppRoutesAndAPI::test_home_dashboard_route PASSED [ 58%]
tests/test_app.py::TestAppRoutesAndAPI::test_marks_list_route PASSED     [ 61%]
tests/test_app.py::TestAppRoutesAndAPI::test_student_report_route PASSED [ 64%]
tests/test_app.py::TestAppRoutesAndAPI::test_students_list_route PASSED  [ 67%]
tests/test_app.py::TestAppRoutesAndAPI::test_subject_analysis_route PASSED [ 70%]
tests/test_app.py::TestAppRoutesAndAPI::test_subjects_route PASSED       [ 74%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_different_subject_max_marks PASSED [ 77%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_empty_dataframe PASSED [ 80%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_grade_boundaries_no_backlogs PASSED [ 83%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_grade_with_backlog_penalty PASSED [ 87%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_multiple_assessments_aggregation_and_no_double_counting PASSED [ 90%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_student_without_marks PASSED [ 93%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_topper_and_support_needed_logic PASSED [ 96%]
tests/test_calculations.py::TestStudentPerformanceCalculations::test_zero_marks_and_pass_mark_boundary PASSED [100%]

============================= 31 passed in 14.98s =============================
```

**Quality Status:** 31 tests passed out of 31 (100% pass rate, 0 failures, 0 warnings).
