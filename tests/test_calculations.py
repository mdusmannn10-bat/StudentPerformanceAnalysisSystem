import unittest
import pandas as pd
from analytics import (
    calculate_grade,
    compute_student_performance_from_df,
    get_marks_summary,
    get_subject_summary,
    get_section_summary,
    get_toppers,
    get_students_needing_support,
)


class TestStudentPerformanceCalculations(unittest.TestCase):
    """
    Independent unit tests for student performance formulas, boundary conditions,
    and multi-assessment aggregation rules. Completely independent of live MySQL.
    """

    # -------------------------------------------------------------------------
    # 1. Letter Grade Boundary Tests
    # -------------------------------------------------------------------------

    def test_grade_boundaries_no_backlogs(self):
        """Test exact grading boundaries with zero failed subjects."""
        # A+ boundary (>= 90.0)
        self.assertEqual(calculate_grade(100.0, 0), "A+")
        self.assertEqual(calculate_grade(90.0, 0), "A+")
        # A boundary (80.0 to 89.99)
        self.assertEqual(calculate_grade(89.99, 0), "A")
        self.assertEqual(calculate_grade(80.0, 0), "A")
        # B boundary (70.0 to 79.99)
        self.assertEqual(calculate_grade(79.99, 0), "B")
        self.assertEqual(calculate_grade(70.0, 0), "B")
        # C boundary (60.0 to 69.99)
        self.assertEqual(calculate_grade(69.99, 0), "C")
        self.assertEqual(calculate_grade(60.0, 0), "C")
        # D boundary (50.0 to 59.99)
        self.assertEqual(calculate_grade(59.99, 0), "D")
        self.assertEqual(calculate_grade(50.0, 0), "D")
        # E boundary (35.0 to 49.99)
        self.assertEqual(calculate_grade(49.99, 0), "E")
        self.assertEqual(calculate_grade(35.0, 0), "E")
        # F boundary (< 35.0)
        self.assertEqual(calculate_grade(34.99, 0), "F")
        self.assertEqual(calculate_grade(0.0, 0), "F")

    def test_grade_with_backlog_penalty(self):
        """Test that any failed subject forces an overall 'F' grade even with high percentages."""
        self.assertEqual(calculate_grade(96.0, failed_count=1), "F")
        self.assertEqual(calculate_grade(85.0, failed_count=2), "F")
        self.assertEqual(calculate_grade(40.0, failed_count=1), "F")

    # -------------------------------------------------------------------------
    # 2. Empty & Edge Case Datasets
    # -------------------------------------------------------------------------

    def test_empty_dataframe(self):
        """Test behavior when the dataset is completely empty."""
        empty_df = pd.DataFrame(columns=[
            "student_id", "roll_no", "full_name", "section",
            "subject_id", "subject_name", "max_marks", "pass_marks",
            "mark_id", "assessment", "marks_obtained"
        ])
        results = compute_student_performance_from_df(empty_df)
        self.assertEqual(results, [])

        summary = get_marks_summary(empty_df)
        self.assertEqual(summary["total_records"], 0)
        self.assertEqual(summary["mean_marks"], 0.0)

    def test_student_without_marks(self):
        """Test student registered in database but with no marks recorded."""
        df = pd.DataFrame([{
            "student_id": 99, "roll_no": "NO_MARKS", "full_name": "Ghost Student", "section": "A",
            "subject_id": None, "subject_name": None, "max_marks": None, "pass_marks": None,
            "mark_id": None, "assessment": None, "marks_obtained": None
        }])
        results = compute_student_performance_from_df(df)
        self.assertEqual(len(results), 1)
        student = results[0]
        self.assertEqual(student["status"], "No Marks Yet")
        self.assertEqual(student["grade"], "N/A")
        self.assertEqual(student["percentage"], 0.0)
        self.assertEqual(student["rank"], "-")

    def test_zero_marks_and_pass_mark_boundary(self):
        """Test students scoring exactly 0 and scoring exactly the pass threshold (35)."""
        df = pd.DataFrame([
            {"student_id": 1, "roll_no": "R01", "full_name": "Zero Scorer", "section": "A",
             "subject_id": 1, "subject_name": "Math", "max_marks": 100, "pass_marks": 35,
             "mark_id": 1, "assessment": "Internal 1", "marks_obtained": 0.0},
            {"student_id": 2, "roll_no": "R02", "full_name": "Pass Boundary", "section": "A",
             "subject_id": 1, "subject_name": "Math", "max_marks": 100, "pass_marks": 35,
             "mark_id": 2, "assessment": "Internal 1", "marks_obtained": 35.0},
            {"student_id": 3, "roll_no": "R03", "full_name": "Centum Scorer", "section": "A",
             "subject_id": 1, "subject_name": "Math", "max_marks": 100, "pass_marks": 35,
             "mark_id": 3, "assessment": "Internal 1", "marks_obtained": 100.0},
        ])
        results = compute_student_performance_from_df(df)
        res_by_roll = {s["roll_no"]: s for s in results}

        # Zero Scorer
        zero_s = res_by_roll["R01"]
        self.assertEqual(zero_s["percentage"], 0.0)
        self.assertEqual(zero_s["status"], "Fail")
        self.assertEqual(zero_s["grade"], "F")

        # Pass Boundary Scorer (35/100 -> Pass, Grade E)
        pass_s = res_by_roll["R02"]
        self.assertEqual(pass_s["percentage"], 35.0)
        self.assertEqual(pass_s["status"], "Pass")
        self.assertEqual(pass_s["grade"], "E")

        # Centum Scorer (100/100 -> Pass, Grade A+)
        cent_s = res_by_roll["R03"]
        self.assertEqual(cent_s["percentage"], 100.0)
        self.assertEqual(cent_s["status"], "Pass")
        self.assertEqual(cent_s["grade"], "A+")

    # -------------------------------------------------------------------------
    # 3. Multiple Assessments for Same Subject (No Double-Counting)
    # -------------------------------------------------------------------------

    def test_multiple_assessments_aggregation_and_no_double_counting(self):
        """
        Verify that multiple assessments for a subject:
        1. Do NOT inflate total maximum marks (subject max remains 100, not 200).
        2. Average the assessments: (30 + 70) / 2 = 50 -> Passed the subject.
        3. Do not treat individual failed assessment (30) as an overall student failure.
        """
        df = pd.DataFrame([
            {"student_id": 10, "roll_no": "M01", "full_name": "Multi Assessment Student", "section": "B",
             "subject_id": 1, "subject_name": "Python", "max_marks": 100, "pass_marks": 35,
             "mark_id": 101, "assessment": "Internal 1", "marks_obtained": 30.0},
            {"student_id": 10, "roll_no": "M01", "full_name": "Multi Assessment Student", "section": "B",
             "subject_id": 1, "subject_name": "Python", "max_marks": 100, "pass_marks": 35,
             "mark_id": 102, "assessment": "Internal 2", "marks_obtained": 70.0},
        ])
        results = compute_student_performance_from_df(df, aggregation_mode="AVERAGE")
        self.assertEqual(len(results), 1)
        s = results[0]

        # Total obtained = (30 + 70)/2 = 50.0
        self.assertEqual(s["total_marks"], 50.0)
        # Max total = 100.0 (NOT 200.0!)
        self.assertEqual(s["max_total"], 100.0)
        self.assertEqual(s["percentage"], 50.0)
        self.assertEqual(s["status"], "Pass")
        self.assertEqual(s["grade"], "D")
        self.assertEqual(s["failed_count"], 0)

    # -------------------------------------------------------------------------
    # 4. Differing Subject Maximum Marks
    # -------------------------------------------------------------------------

    def test_different_subject_max_marks(self):
        """
        Verify calculation when subjects have different maximum marks:
        Subject 1: Lab out of 50 (Pass mark: 18) -> Scored 40/50 (80%)
        Subject 2: Theory out of 100 (Pass mark: 35) -> Scored 80/100 (80%)
        Total Obtained: 120 / 150 -> 80.0%, Grade A.
        """
        df = pd.DataFrame([
            {"student_id": 20, "roll_no": "D01", "full_name": "Different Max Marks Student", "section": "A",
             "subject_id": 1, "subject_name": "Lab", "max_marks": 50, "pass_marks": 18,
             "mark_id": 201, "assessment": "Lab Exam", "marks_obtained": 40.0},
            {"student_id": 20, "roll_no": "D01", "full_name": "Different Max Marks Student", "section": "A",
             "subject_id": 2, "subject_name": "Theory", "max_marks": 100, "pass_marks": 35,
             "mark_id": 202, "assessment": "Final Exam", "marks_obtained": 80.0},
        ])
        results = compute_student_performance_from_df(df)
        s = results[0]

        self.assertEqual(s["total_marks"], 120.0)
        self.assertEqual(s["max_total"], 150.0)
        self.assertEqual(s["percentage"], 80.0)
        self.assertEqual(s["status"], "Pass")
        self.assertEqual(s["grade"], "A")

    # -------------------------------------------------------------------------
    # 5. Rankings, Toppers, and Support-Needed Diagnostics
    # -------------------------------------------------------------------------

    def test_topper_and_support_needed_logic(self):
        """Test topper extraction and threshold-based at-risk diagnostics."""
        df = pd.DataFrame([
            # Student 1: 95% -> Topper 1
            {"student_id": 1, "roll_no": "T1", "full_name": "Top Achiever", "section": "A",
             "subject_id": 1, "subject_name": "Math", "max_marks": 100, "pass_marks": 35,
             "mark_id": 1, "assessment": "Internal 1", "marks_obtained": 95.0},
            # Student 2: 85% -> Topper 2
            {"student_id": 2, "roll_no": "T2", "full_name": "Second Achiever", "section": "A",
             "subject_id": 1, "subject_name": "Math", "max_marks": 100, "pass_marks": 35,
             "mark_id": 2, "assessment": "Internal 1", "marks_obtained": 85.0},
            # Student 3: 30% -> Failed Math (<35), Needs Support
            {"student_id": 3, "roll_no": "T3", "full_name": "Struggling Student", "section": "B",
             "subject_id": 1, "subject_name": "Math", "max_marks": 100, "pass_marks": 35,
             "mark_id": 3, "assessment": "Internal 1", "marks_obtained": 30.0},
        ])

        toppers = get_toppers(2, df)
        self.assertEqual(len(toppers), 2)
        self.assertEqual(toppers[0]["roll_no"], "T1")
        self.assertEqual(toppers[1]["roll_no"], "T2")

        support = get_students_needing_support(threshold=40.0, df=df)
        self.assertEqual(len(support), 1)
        self.assertEqual(support[0]["roll_no"], "T3")
        self.assertIn("Math", support[0]["failed_subjects"])
        self.assertIn("remedial", support[0]["recommendation"].lower())


if __name__ == "__main__":
    unittest.main()
