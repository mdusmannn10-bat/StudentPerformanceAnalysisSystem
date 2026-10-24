import numpy as np
import pandas as pd
from config import Config
from db import get_connection


# =============================================================================
# DATA EXTRACTION
# =============================================================================

def get_marks_data():
    """
    Fetch all student profiles, curriculum subjects, and assessment records from MySQL.
    Orders assessment records chronologically by mark_id to ensure reliable sequence.
    Returns a normalized Pandas DataFrame with safe numeric type conversions.
    """
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                s.student_id,
                s.roll_no,
                s.full_name,
                s.section,
                sub.subject_id,
                sub.subject_name,
                sub.max_marks,
                sub.pass_marks,
                m.mark_id,
                m.assessment,
                m.marks_obtained
            FROM students s
            LEFT JOIN marks m
                ON s.student_id = m.student_id
            LEFT JOIN subjects sub
                ON m.subject_id = sub.subject_id
            ORDER BY s.roll_no, sub.subject_name, m.mark_id ASC
        """)

        rows = cursor.fetchall()
        columns = [
            "student_id", "roll_no", "full_name", "section",
            "subject_id", "subject_name", "max_marks", "pass_marks",
            "mark_id", "assessment", "marks_obtained"
        ]

        if not rows:
            return pd.DataFrame(columns=columns)

        df = pd.DataFrame(rows)

        # Convert numeric columns safely
        df["max_marks"] = pd.to_numeric(df["max_marks"], errors="coerce")
        df["pass_marks"] = pd.to_numeric(df["pass_marks"], errors="coerce")
        df["marks_obtained"] = pd.to_numeric(df["marks_obtained"], errors="coerce")

        return df

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# =============================================================================
# GRADING LOGIC
# =============================================================================

def calculate_grade(percentage, failed_count=0):
    """
    Calculate academic letter grade based on percentage and backlog status.

    Standard Grading Policy:
      - Any failed subject backlog (failed_count > 0): 'F' (Fail)
      - Percentage >= 90.0%: 'A+' (Outstanding)
      - Percentage >= 80.0%: 'A'  (Excellent)
      - Percentage >= 70.0%: 'B'  (Very Good)
      - Percentage >= 60.0%: 'C'  (Good)
      - Percentage >= 50.0%: 'D'  (Average)
      - Percentage >= 35.0%: 'E'  (Pass)
      - Below 35.0%: 'F' (Fail)
    """
    if failed_count > 0:
        return "F"
    if percentage >= 90.0:
        return "A+"
    if percentage >= 80.0:
        return "A"
    if percentage >= 70.0:
        return "B"
    if percentage >= 60.0:
        return "C"
    if percentage >= 50.0:
        return "D"
    if percentage >= 35.0:
        return "E"
    return "F"


# =============================================================================
# NUMPY DESCRIPTIVE STATISTICS
# =============================================================================

def get_marks_summary(df=None):
    """
    Calculate descriptive statistics using NumPy across all assessment records.
    Optionally accepts a custom DataFrame for testing or isolated evaluation.
    """
    if df is None:
        df = get_marks_data()

    if df.empty or "marks_obtained" not in df.columns:
        valid_marks = np.array([], dtype=float)
    else:
        valid_marks = df["marks_obtained"].dropna().to_numpy(dtype=float)

    if valid_marks.size == 0:
        return {
            "total_records": 0,
            "mean_marks": 0.0,
            "median_marks": 0.0,
            "std_dev": 0.0,
            "variance": 0.0,
            "minimum_marks": 0.0,
            "maximum_marks": 0.0,
            "q1_marks": 0.0,
            "q3_marks": 0.0,
            "iqr_marks": 0.0,
        }

    mean_val = float(np.mean(valid_marks))
    median_val = float(np.median(valid_marks))
    std_val = float(np.std(valid_marks))
    var_val = float(np.var(valid_marks))
    min_val = float(np.min(valid_marks))
    max_val = float(np.max(valid_marks))
    q1_val = float(np.percentile(valid_marks, 25))
    q3_val = float(np.percentile(valid_marks, 75))
    iqr_val = q3_val - q1_val

    return {
        "total_records": int(valid_marks.size),
        "mean_marks": round(mean_val, 2),
        "median_marks": round(median_val, 2),
        "std_dev": round(std_val, 2),
        "variance": round(var_val, 2),
        "minimum_marks": round(min_val, 2),
        "maximum_marks": round(max_val, 2),
        "q1_marks": round(q1_val, 2),
        "q3_marks": round(q3_val, 2),
        "iqr_marks": round(iqr_val, 2),
    }


# =============================================================================
# PANDAS AGGREGATION SUMMARIES
# =============================================================================

def get_subject_summary(df=None):
    """
    Summarize marks for each curriculum subject using Pandas groupby and aggregations.
    Computes assessment count, mean marks, min, max, pass/fail counts, and pass rates.
    """
    if df is None:
        df = get_marks_data()

    marks_df = df.dropna(subset=["mark_id", "subject_name"]).copy()
    if marks_df.empty:
        return []

    marks_df["is_pass"] = marks_df["marks_obtained"] >= marks_df["pass_marks"]

    grouped = marks_df.groupby(["subject_id", "subject_name"]).agg(
        assessment_count=("marks_obtained", "count"),
        average_marks=("marks_obtained", "mean"),
        highest_marks=("marks_obtained", "max"),
        lowest_marks=("marks_obtained", "min"),
        pass_count=("is_pass", lambda s: int(s.sum())),
        max_marks=("max_marks", "first"),
        pass_marks=("pass_marks", "first")
    ).reset_index()

    grouped["fail_count"] = grouped["assessment_count"] - grouped["pass_count"]
    grouped["pass_percentage"] = np.where(
        grouped["assessment_count"] > 0,
        ((grouped["pass_count"] / grouped["assessment_count"]) * 100).round(2),
        0.0
    )
    grouped["average_marks"] = grouped["average_marks"].round(2)
    grouped["highest_marks"] = grouped["highest_marks"].round(2)
    grouped["lowest_marks"] = grouped["lowest_marks"].round(2)

    return grouped.sort_values(by="subject_name").to_dict(orient="records")


def get_section_summary(df=None):
    """
    Summarize marks for each class section using Pandas groupby.
    Includes student count, total assessments, mean marks, normalized percentage, and pass rate.
    """
    if df is None:
        df = get_marks_data()

    marks_df = df.dropna(subset=["mark_id", "section"]).copy()
    marks_df = marks_df[marks_df["section"].astype(str).str.strip() != ""]

    if marks_df.empty:
        return []

    marks_df["is_pass"] = marks_df["marks_obtained"] >= marks_df["pass_marks"]
    marks_df["pct_obtained"] = (marks_df["marks_obtained"] / marks_df["max_marks"]) * 100

    grouped = marks_df.groupby("section").agg(
        student_count=("student_id", "nunique"),
        assessment_count=("marks_obtained", "count"),
        average_marks=("marks_obtained", "mean"),
        average_percentage=("pct_obtained", "mean"),
        highest_marks=("marks_obtained", "max"),
        lowest_marks=("marks_obtained", "min"),
        pass_count=("is_pass", lambda s: int(s.sum()))
    ).reset_index()

    grouped["fail_count"] = grouped["assessment_count"] - grouped["pass_count"]
    grouped["pass_percentage"] = np.where(
        grouped["assessment_count"] > 0,
        ((grouped["pass_count"] / grouped["assessment_count"]) * 100).round(2),
        0.0
    )
    grouped["average_marks"] = grouped["average_marks"].round(2)
    grouped["average_percentage"] = grouped["average_percentage"].round(2)
    grouped["highest_marks"] = grouped["highest_marks"].round(2)
    grouped["lowest_marks"] = grouped["lowest_marks"].round(2)

    return grouped.sort_values(by="section").to_dict(orient="records")


# =============================================================================
# STUDENT PERFORMANCE EVALUATION ENGINE
# =============================================================================

def compute_student_performance_from_df(df, aggregation_mode=None):
    """
    Pure analytical engine evaluating student performance from any Pandas DataFrame.
    Distinguishes individual assessment records from final subject mastery, avoiding
    double-counting of assessment maximum marks.

    Aggregation Policy for Multiple Assessments in a Subject:
      - 'AVERAGE': Final subject score is the arithmetic mean of marks across assessments.
      - 'BEST': Final subject score is the highest assessment score achieved.
      - 'LATEST': Final subject score is the chronologically latest assessment score (sorted by mark_id).
    """
    if aggregation_mode is None:
        aggregation_mode = getattr(Config, "ASSESSMENT_AGGREGATION", "AVERAGE")

    if df.empty:
        return []

    results = []

    # Group by student profile attributes
    for (student_id, roll_no, full_name, section), s_df in df.groupby(
        ["student_id", "roll_no", "full_name", "section"], dropna=False
    ):
        valid_marks_df = s_df.dropna(subset=["mark_id"])

        if valid_marks_df.empty:
            results.append({
                "student_id": int(student_id),
                "roll_no": str(roll_no),
                "full_name": str(full_name),
                "section": str(section) if section and pd.notna(section) else "-",
                "total_marks": 0.0,
                "max_total": 0.0,
                "percentage": 0.0,
                "average_marks": 0.0,
                "subjects_attempted": 0,
                "failed_count": 0,
                "failed_subjects": [],
                "subject_details": [],
                "status": "No Marks Yet",
                "grade": "N/A",
                "rank": "-"
            })
            continue

        # Evaluate subject-by-subject to prevent assessment inflation
        subject_details = []
        total_obtained = 0.0
        total_max = 0.0
        failed_subjects = []

        for (subject_id, subject_name), sub_df in valid_marks_df.groupby(["subject_id", "subject_name"]):
            sub_max = float(sub_df["max_marks"].iloc[0])
            sub_pass = float(sub_df["pass_marks"].iloc[0])
            assessments_count = len(sub_df)

            # Apply aggregation policy across multiple assessments in this subject
            if aggregation_mode == "BEST":
                sub_score = float(sub_df["marks_obtained"].max())
            elif aggregation_mode == "LATEST":
                # Ensure chronological sequence by sorting by mark_id if present
                if "mark_id" in sub_df.columns and sub_df["mark_id"].notna().any():
                    sub_score = float(sub_df.sort_values(by="mark_id")["marks_obtained"].iloc[-1])
                else:
                    sub_score = float(sub_df["marks_obtained"].iloc[-1])
            else:  # Default: AVERAGE
                sub_score = float(sub_df["marks_obtained"].mean())

            sub_score = round(sub_score, 2)
            sub_pct = round((sub_score / sub_max * 100), 2) if sub_max > 0 else 0.0
            sub_status = "Pass" if sub_score >= sub_pass else "Fail"
            sub_grade = calculate_grade(sub_pct, 1 if sub_status == "Fail" else 0)

            total_obtained += sub_score
            total_max += sub_max

            if sub_status == "Fail":
                failed_subjects.append(str(subject_name))

            subject_details.append({
                "subject_id": int(subject_id),
                "subject_name": str(subject_name),
                "marks_obtained": sub_score,
                "max_marks": sub_max,
                "pass_marks": sub_pass,
                "percentage": sub_pct,
                "status": sub_status,
                "grade": sub_grade,
                "assessments_count": assessments_count,
            })

        subjects_attempted = len(subject_details)
        percentage = round((total_obtained / total_max * 100), 2) if total_max > 0 else 0.0
        avg_marks = round(total_obtained / subjects_attempted, 2) if subjects_attempted > 0 else 0.0
        failed_count = len(failed_subjects)

        status = "Fail" if failed_count > 0 else "Pass"
        overall_grade = calculate_grade(percentage, failed_count)

        results.append({
            "student_id": int(student_id),
            "roll_no": str(roll_no),
            "full_name": str(full_name),
            "section": str(section) if section and pd.notna(section) else "-",
            "total_marks": round(total_obtained, 2),
            "max_total": round(total_max, 2),
            "percentage": percentage,
            "average_marks": avg_marks,
            "subjects_attempted": subjects_attempted,
            "failed_count": failed_count,
            "failed_subjects": failed_subjects,
            "subject_details": subject_details,
            "status": status,
            "grade": overall_grade,
            "rank": "-"
        })

    # Sort students: evaluated students first ordered by percentage descending, then unranked
    results.sort(
        key=lambda s: (s["max_total"] > 0, s["percentage"]),
        reverse=True
    )

    # Assign dense competition ranks
    current_rank = 0
    prev_percentage = None
    for idx, student in enumerate(results, start=1):
        if student["max_total"] == 0:
            student["rank"] = "-"
        else:
            if student["percentage"] != prev_percentage:
                current_rank = idx
            student["rank"] = current_rank
            prev_percentage = student["percentage"]

    return results


def get_student_performance(df=None):
    """
    Public accessor for overall student performance.
    Fetches live MySQL data if no DataFrame is provided.
    """
    if df is None:
        df = get_marks_data()
    return compute_student_performance_from_df(df)


def get_toppers(top_n=None, df=None):
    """
    Identify top-performing students who cleared all attempted subjects.
    Returns the top N students ordered by academic percentage descending.
    """
    if top_n is None:
        top_n = Config.DEFAULT_TOP_N

    students = get_student_performance(df)
    # Only passed students with recorded marks qualify for the Topper list
    passed_students = [s for s in students if s["status"] == "Pass" and s["max_total"] > 0]
    return passed_students[:top_n]


def get_students_needing_support(threshold=None, df=None):
    """
    Identify students requiring academic intervention based on a configurable threshold.
    Students below the threshold OR with backlogs in one or more subjects are flagged.
    """
    if threshold is None:
        threshold = Config.ACADEMIC_SUPPORT_THRESHOLD

    try:
        threshold = float(threshold)
    except (ValueError, TypeError):
        threshold = Config.ACADEMIC_SUPPORT_THRESHOLD

    students = get_student_performance(df)
    support_list = []

    for s in students:
        if s["max_total"] == 0:
            continue  # Exclude students without evaluations

        needs_support = False
        reasons = []

        if s["failed_count"] > 0:
            needs_support = True
            reasons.append(f"Holding backlog in {s['failed_count']} subject(s): {', '.join(s['failed_subjects'])}")

        if s["percentage"] < threshold:
            needs_support = True
            reasons.append(f"Cumulative aggregate ({s['percentage']}%) is below threshold ({threshold}%)")

        if needs_support:
            s_copy = dict(s)
            s_copy["support_reasons"] = reasons
            s_copy["recommendation"] = (
                "Immediate remedial classes and faculty mentoring recommended"
                if s["failed_count"] > 0
                else "Academic counseling and practice tutorial sessions recommended"
            )
            support_list.append(s_copy)

    # Sort ascending by percentage so the most vulnerable students appear at the top
    support_list.sort(key=lambda s: s["percentage"])
    return support_list


def get_overall_kpis(df=None):
    """
    Compute comprehensive summary KPIs for institutional dashboards.
    Returns student counts, pass rate, average, support count, toppers,
    and curriculum attention areas.
    """
    perf = get_student_performance(df)
    students_with_marks = [s for s in perf if s["max_total"] > 0]

    total_students = len(perf)
    total_evaluated = len(students_with_marks)
    total_passed = sum(1 for s in students_with_marks if s["status"] == "Pass")
    overall_pass_rate = round((total_passed / total_evaluated * 100), 2) if total_evaluated > 0 else 0.0

    overall_avg = round(
        float(np.mean([s["percentage"] for s in students_with_marks])), 2
    ) if students_with_marks else 0.0

    toppers = get_toppers(Config.DEFAULT_TOP_N, df)
    topper_name = toppers[0]["full_name"] if toppers else "N/A"
    topper_score = toppers[0]["percentage"] if toppers else 0.0

    support_list = get_students_needing_support(Config.ACADEMIC_SUPPORT_THRESHOLD, df)
    support_count = len(support_list)

    # Identify curriculum subjects needing faculty attention (pass rate < 95% or lowest pass rates)
    subject_summary = get_subject_summary(df)
    total_subjects = len(subject_summary)
    attention_subjects = [sub for sub in subject_summary if sub["pass_percentage"] < 100.0]
    # Sort attention subjects by lowest pass rate first
    attention_subjects.sort(key=lambda s: (s["pass_percentage"], s["average_marks"]))

    return {
        "total_students": total_students,
        "total_evaluated": total_evaluated,
        "total_passed": total_passed,
        "total_failed": total_evaluated - total_passed,
        "overall_pass_rate": overall_pass_rate,
        "overall_average_percentage": overall_avg,
        "top_student": topper_name,
        "top_score": topper_score,
        "toppers": toppers,
        "total_subjects": total_subjects,
        "students_needing_support_count": support_count,
        "attention_subjects": attention_subjects[:3],  # Top 3 subjects needing attention
    }
