import os
import unittest
import pandas as pd
from analytics import (
    get_marks_summary,
    get_subject_summary,
    get_section_summary,
    get_overall_kpis,
    get_student_performance,
)
from charts import (
    generate_all_charts,
    generate_subject_average_chart,
    generate_pass_fail_chart,
    generate_marks_distribution_chart,
    generate_subject_pass_rate_chart,
    generate_section_performance_chart,
)
from config import Config


class TestAnalyticsModule(unittest.TestCase):
    """Integration and aggregation tests for analytics.py and charts.py."""

    def test_marks_summary_numpy_metrics(self):
        """Verify NumPy statistical output conforms to mathematical expectations."""
        summary = get_marks_summary()
        self.assertIn("total_records", summary)
        self.assertIn("mean_marks", summary)
        self.assertIn("median_marks", summary)
        self.assertIn("std_dev", summary)
        self.assertIn("variance", summary)
        self.assertIn("q1_marks", summary)
        self.assertIn("q3_marks", summary)
        self.assertIn("iqr_marks", summary)

        if summary["total_records"] > 0:
            self.assertGreaterEqual(summary["maximum_marks"], summary["minimum_marks"])
            self.assertGreaterEqual(summary["mean_marks"], summary["minimum_marks"])
            self.assertLessEqual(summary["mean_marks"], summary["maximum_marks"])
            self.assertGreaterEqual(summary["q3_marks"], summary["q1_marks"])
            self.assertAlmostEqual(summary["iqr_marks"], summary["q3_marks"] - summary["q1_marks"], places=2)

    def test_subject_summary_pandas(self):
        """Verify Pandas subject-wise aggregation outputs valid metrics."""
        subjects = get_subject_summary()
        self.assertIsInstance(subjects, list)

        for sub in subjects:
            self.assertIn("subject_name", sub)
            self.assertIn("average_marks", sub)
            self.assertIn("pass_percentage", sub)
            self.assertIn("pass_count", sub)
            self.assertIn("fail_count", sub)
            self.assertEqual(sub["assessment_count"], sub["pass_count"] + sub["fail_count"])
            self.assertGreaterEqual(sub["pass_percentage"], 0.0)
            self.assertLessEqual(sub["pass_percentage"], 100.0)

    def test_section_summary_pandas(self):
        """Verify section-wise aggregation outputs valid metrics."""
        sections = get_section_summary()
        self.assertIsInstance(sections, list)

        for sec in sections:
            self.assertIn("section", sec)
            self.assertIn("student_count", sec)
            self.assertIn("average_marks", sec)
            self.assertIn("pass_percentage", sec)

    def test_overall_kpis(self):
        """Verify dashboard KPIs computation."""
        kpis = get_overall_kpis()
        self.assertIn("total_students", kpis)
        self.assertIn("overall_pass_rate", kpis)
        self.assertIn("overall_average_percentage", kpis)
        self.assertGreaterEqual(kpis["overall_pass_rate"], 0.0)
        self.assertLessEqual(kpis["overall_pass_rate"], 100.0)

    def test_charts_generation(self):
        """Verify that all 5 Matplotlib charts generate valid PNG files on disk."""
        charts = generate_all_charts()
        self.assertIsInstance(charts, dict)

        for chart_key, chart_rel_path in charts.items():
            if chart_rel_path:
                full_path = os.path.join(Config.BASE_DIR, "static", chart_rel_path)
                self.assertTrue(os.path.exists(full_path), f"Chart {chart_key} not found at {full_path}")
                self.assertGreater(os.path.getsize(full_path), 0, f"Chart {chart_key} is an empty file")


if __name__ == "__main__":
    unittest.main()
