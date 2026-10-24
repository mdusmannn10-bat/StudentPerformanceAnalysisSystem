import unittest
import json
from unittest.mock import patch
from app import app, execute_query


class TestAppRoutesAndAPI(unittest.TestCase):
    """Integration test suite testing all Web UI routes and REST API endpoints."""

    def setUp(self):
        """Configure test client and initialize tracking for created test records."""
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.created_student_ids = []
        self.created_mark_ids = []
        self.created_subject_ids = []

    def tearDown(self):
        """Clean up any database records inserted during test execution to prevent database pollution."""
        for mid in self.created_mark_ids:
            try:
                execute_query("DELETE FROM marks WHERE mark_id = %s", (mid,), commit=True)
            except Exception:
                pass

        for sid in self.created_student_ids:
            try:
                execute_query("DELETE FROM students WHERE student_id = %s", (sid,), commit=True)
            except Exception:
                pass

        for sub_id in self.created_subject_ids:
            try:
                execute_query("DELETE FROM subjects WHERE subject_id = %s", (sub_id,), commit=True)
            except Exception:
                pass

        # Reset AUTO_INCREMENT counters back to MAX(id) + 1 so test runs never leave counter gaps
        try:
            execute_query("ALTER TABLE marks AUTO_INCREMENT = 1", commit=True)
            execute_query("ALTER TABLE students AUTO_INCREMENT = 1", commit=True)
            execute_query("ALTER TABLE subjects AUTO_INCREMENT = 1", commit=True)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # 1. Web UI Route Tests
    # -------------------------------------------------------------------------

    def test_home_dashboard_route(self):
        """Test that the dashboard loads successfully with status code 200."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Academic Performance Dashboard", response.data)

    def test_students_list_route(self):
        """Test viewing student profiles directory."""
        response = self.client.get("/students")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Student Profiles", response.data)

    def test_add_student_get(self):
        """Test GET request to add student form."""
        response = self.client.get("/add-student")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add New Student", response.data)

    def test_add_student_validation_error(self):
        """Test submitting add student with missing data returns 400 Bad Request."""
        response = self.client.post("/add-student", data={"roll_no": "", "full_name": ""})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Roll number and full name are required", response.data)

    def test_marks_list_route(self):
        """Test viewing marks ledger page."""
        response = self.client.get("/marks")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Assessment Marks Records", response.data)

    def test_add_marks_get(self):
        """Test GET request to enter marks form."""
        response = self.client.get("/add-marks")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Record Assessment Marks", response.data)

    def test_add_marks_validation_negative(self):
        """Test submitting negative marks returns 400 Bad Request."""
        response = self.client.post("/add-marks", data={
            "student_id": "1",
            "subject_id": "1",
            "assessment": "Test Negative Exam",
            "marks_obtained": "-5"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"cannot be negative", response.data)

    def test_add_marks_validation_exceeds_max(self):
        """Test submitting marks greater than allowed maximum returns 400 Bad Request."""
        response = self.client.post("/add-marks", data={
            "student_id": "1",
            "subject_id": "1",
            "assessment": "Test Overflow Exam",
            "marks_obtained": "150"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"cannot exceed", response.data)

    def test_subjects_route(self):
        """Test curriculum subjects management route."""
        response = self.client.get("/subjects")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Curriculum Subjects", response.data)

    def test_analysis_route(self):
        """Test performance analysis page with threshold query param."""
        response = self.client.get("/analysis?threshold=45")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Comprehensive Performance Analysis", response.data)
        self.assertIn(b"Topper Showcase", response.data)

    def test_subject_analysis_route(self):
        """Test subject and section analysis page."""
        response = self.client.get("/subject-analysis")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Subject-Wise Academic Performance", response.data)
        self.assertIn(b"Class Section", response.data)

    def test_student_report_route(self):
        """Test student report card generation route."""
        response = self.client.get("/student-report?student_id=1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Academic Transcript", response.data)

    # -------------------------------------------------------------------------
    # 2. REST API Tests
    # -------------------------------------------------------------------------

    def test_api_health_success(self):
        """Test /api/health endpoint returns 200 when database probe succeeds."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["database"]["connected"])

    @patch("app.test_connection")
    def test_api_health_failure(self, mock_test_conn):
        """Test /api/health endpoint returns 503 Service Unavailable when database probe fails."""
        mock_test_conn.return_value = (False, "Database service unreachable.")
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "unhealthy")
        self.assertFalse(data["database"]["connected"])

    def test_api_students_get(self):
        """Test /api/students returns list of students."""
        response = self.client.get("/api/students")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)

    def test_api_students_crud_lifecycle(self):
        """Test complete API lifecycle: Create student, retrieve, update, and delete with cleanup."""
        test_roll = "TEST_INTEG_99"
        # 1. Create
        create_resp = self.client.post("/api/students", json={
            "roll_no": test_roll,
            "full_name": "Test Integration Student",
            "section": "Z"
        })
        self.assertEqual(create_resp.status_code, 201)
        created_data = json.loads(create_resp.data)
        new_id = created_data["data"]["student_id"]
        self.created_student_ids.append(new_id)

        # 2. Retrieve
        get_resp = self.client.get(f"/api/students/{new_id}")
        self.assertEqual(get_resp.status_code, 200)
        get_data = json.loads(get_resp.data)
        self.assertEqual(get_data["data"]["roll_no"], test_roll)

        # 3. Update
        put_resp = self.client.put(f"/api/students/{new_id}", json={
            "full_name": "Test Student Updated",
            "section": "Y"
        })
        self.assertEqual(put_resp.status_code, 200)

        # 4. Delete
        del_resp = self.client.delete(f"/api/students/{new_id}")
        self.assertEqual(del_resp.status_code, 200)
        self.created_student_ids.remove(new_id)

        # 5. Verify deletion
        verify_resp = self.client.get(f"/api/students/{new_id}")
        self.assertEqual(verify_resp.status_code, 404)

    def test_api_subjects_get(self):
        """Test /api/subjects returns curriculum courses."""
        response = self.client.get("/api/subjects")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertGreater(data["count"], 0)

    def test_api_analytics_endpoints(self):
        """Test that all analytics REST endpoints return successful responses."""
        # Summary (NumPy)
        resp_sum = self.client.get("/api/analytics/summary")
        self.assertEqual(resp_sum.status_code, 200)
        data_sum = json.loads(resp_sum.data)
        self.assertIn("mean_marks", data_sum["data"])

        # Subjects (Pandas)
        resp_sub = self.client.get("/api/analytics/subjects")
        self.assertEqual(resp_sub.status_code, 200)
        data_sub = json.loads(resp_sub.data)
        self.assertTrue(data_sub["success"])

        # Sections (Pandas)
        resp_sec = self.client.get("/api/analytics/sections")
        self.assertEqual(resp_sec.status_code, 200)
        data_sec = json.loads(resp_sec.data)
        self.assertTrue(data_sec["success"])

        # Performance rankings
        resp_perf = self.client.get("/api/analytics/performance")
        self.assertEqual(resp_perf.status_code, 200)
        data_perf = json.loads(resp_perf.data)
        self.assertTrue(data_perf["success"])

        # Toppers
        resp_top = self.client.get("/api/analytics/toppers?limit=2")
        self.assertEqual(resp_top.status_code, 200)
        data_top = json.loads(resp_top.data)
        self.assertLessEqual(len(data_top["data"]), 2)

        # Support needed
        resp_supp = self.client.get("/api/analytics/support-needed?threshold=40")
        self.assertEqual(resp_supp.status_code, 200)
        data_supp = json.loads(resp_supp.data)
        self.assertTrue(data_supp["success"])


if __name__ == "__main__":
    unittest.main()
