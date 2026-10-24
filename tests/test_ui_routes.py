import unittest
from app import app


class TestUIRoutesAndTabs(unittest.TestCase):
    """Verifies that all restructured frontend pages, routes, aliases, and tabs render with 200 OK."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_main_dashboard_page(self):
        """Page A: Verify main dashboard loads with 5 KPI summary cards and shortcuts."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Academic Performance Dashboard", res.data)
        self.assertIn(b"Total Students", res.data)
        self.assertIn(b"Total Subjects", res.data)
        self.assertIn(b"Average Performance", res.data)
        self.assertIn(b"Overall Pass Rate", res.data)
        self.assertIn(b"Support Required", res.data)

    def test_student_management_directory(self):
        """Page B: Verify student directory and filter functionality."""
        res = self.client.get("/students")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Student Profiles & Directory", res.data)
        self.assertIn(b"CSE001", res.data)

        # Test search query filter
        res_search = self.client.get("/students?q=Aarav")
        self.assertEqual(res_search.status_code, 200)
        self.assertIn(b"Aarav Kumar", res_search.data)

        # Test section filter
        res_sec = self.client.get("/students?section=A")
        self.assertEqual(res_sec.status_code, 200)
        self.assertIn(b"Section A", res_sec.data)

    def test_student_report_card_routes(self):
        """Page B (Detail): Dedicated transcript card accessible via ID parameter or query."""
        res_id = self.client.get("/student/1")
        self.assertEqual(res_id.status_code, 200)
        self.assertIn(b"Individual Student Performance Report", res_id.data)
        self.assertIn(b"Aarav Kumar", res_id.data)
        self.assertIn(b"Print Performance Report", res_id.data)

        res_query = self.client.get("/student-report?student_id=1")
        self.assertEqual(res_query.status_code, 200)
        self.assertIn(b"Aarav Kumar", res_query.data)

    def test_analytics_and_reports_hub_tabs(self):
        """Page C: Analytics hub with all 4 interactive tabs."""
        # Main analytics route
        res = self.client.get("/analysis")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Comprehensive Performance Analysis & Reports", res.data)
        self.assertIn(b"Visual Analytics (5 Charts)", res.data)

        # Alias route /analytics
        res_alias = self.client.get("/analytics")
        self.assertEqual(res_alias.status_code, 200)
        self.assertIn(b"Visual Analytics (5 Charts)", res_alias.data)

        # Tab query: Rankings
        res_rankings = self.client.get("/analysis?tab=rankings")
        self.assertEqual(res_rankings.status_code, 200)
        self.assertIn(b"Topper Showcase & Spotlight", res_rankings.data)

        # Tab query: Support with custom threshold
        res_support = self.client.get("/analysis?tab=support&threshold=50")
        self.assertEqual(res_support.status_code, 200)
        self.assertIn(b"Academic Support Diagnostic", res_support.data)

        # Tab query: Summaries
        res_sum = self.client.get("/analysis?tab=summaries")
        self.assertEqual(res_sum.status_code, 200)
        self.assertIn(b"Curriculum Course Performance Summary", res_sum.data)

    def test_subjects_and_marks_pages(self):
        """Page D: Curriculum subjects and marks ledger."""
        res_subj = self.client.get("/subjects")
        self.assertEqual(res_subj.status_code, 200)
        self.assertIn(b"Curriculum Subjects", res_subj.data)

        res_marks = self.client.get("/marks")
        self.assertEqual(res_marks.status_code, 200)
        self.assertIn(b"Assessment Marks Records", res_marks.data)

        # Filter marks by student
        res_marks_filtered = self.client.get("/marks?student_id=1")
        self.assertEqual(res_marks_filtered.status_code, 200)


if __name__ == "__main__":
    unittest.main()
