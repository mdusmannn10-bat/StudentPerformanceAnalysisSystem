import logging
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from analytics import (
    calculate_grade,
    get_marks_summary,
    get_overall_kpis,
    get_section_summary,
    get_student_performance,
    get_students_needing_support,
    get_subject_summary,
    get_toppers,
)
from charts import generate_all_charts
from config import Config
from db import get_connection, test_connection

# Configure server logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config["DEBUG"] = Config.DEBUG


# =============================================================================
# DATABASE QUERY WRAPPER
# =============================================================================

def execute_query(query, params=None, fetch_all=True, commit=False):
    """
    Safely execute a parameterized SQL query with automatic connection management.
    Never exposes internal database handles.
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if commit:
            connection.commit()
            return cursor.lastrowid
        return cursor.fetchall() if fetch_all else cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# =============================================================================
# WEB APPLICATION ROUTES
# =============================================================================

@app.route("/")
def home():
    """
    Page A: Main Dashboard.
    Provides concise executive KPI cards, highlights (toppers & attention areas),
    recent assessment updates, and direct shortcuts.
    """
    try:
        kpis = get_overall_kpis()

        subj_count_row = execute_query("SELECT COUNT(*) AS total FROM subjects", fetch_all=False)
        total_subjects = subj_count_row["total"] if subj_count_row else 0

        marks_count_row = execute_query("SELECT COUNT(*) AS total FROM marks", fetch_all=False)
        total_marks = marks_count_row["total"] if marks_count_row else 0

        toppers = get_toppers(Config.DEFAULT_TOP_N)

        recent_marks = execute_query("""
            SELECT m.mark_id, m.student_id, m.assessment, m.marks_obtained,
                   s.roll_no, s.full_name, sub.subject_name, sub.max_marks, sub.pass_marks
            FROM marks m
            JOIN students s ON m.student_id = s.student_id
            JOIN subjects sub ON m.subject_id = sub.subject_id
            ORDER BY m.mark_id DESC
            LIMIT 5
        """)

        return render_template(
            "index.html",
            kpis=kpis,
            total_subjects=total_subjects,
            total_marks=total_marks,
            toppers=toppers,
            recent_marks=recent_marks or [],
        )
    except Exception as error:
        logger.exception("Failed to load dashboard")
        return "Unable to load dashboard. Please verify that MySQL is running and check server logs.", 500


@app.route("/students")
def manage_students():
    """
    Page B: Student Management Directory.
    Features search, cohort section filtering, evaluations count, academic status badges,
    and action links to transcripts, editing, and deletion.
    """
    section_filter = request.args.get("section", "").strip()
    search_query = request.args.get("q", "").strip()

    sql = """
        SELECT s.student_id, s.roll_no, s.full_name, s.section,
               COUNT(m.mark_id) AS total_assessments
        FROM students s
        LEFT JOIN marks m ON s.student_id = m.student_id
        WHERE 1=1
    """
    params = []
    if section_filter:
        sql += " AND s.section = %s"
        params.append(section_filter)
    if search_query:
        sql += " AND (s.full_name LIKE %s OR s.roll_no LIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    sql += " GROUP BY s.student_id, s.roll_no, s.full_name, s.section ORDER BY s.roll_no"

    students = execute_query(sql, tuple(params))
    sections = execute_query("SELECT DISTINCT section FROM students WHERE section IS NOT NULL AND section != '' ORDER BY section")

    # Augment student records with evaluated academic standing
    all_perf = get_student_performance()
    eval_map = {s["student_id"]: s for s in all_perf}
    for st in students:
        ev = eval_map.get(st["student_id"])
        if ev and ev["max_total"] > 0:
            st["percentage"] = ev["percentage"]
            st["eval_status"] = ev["status"]
            st["grade"] = ev["grade"]
        else:
            st["percentage"] = 0.0
            st["eval_status"] = "No Marks Yet"
            st["grade"] = "N/A"

    return render_template(
        "students.html",
        students=students,
        sections=[s["section"] for s in sections],
        selected_section=section_filter,
        search_query=search_query,
    )


@app.route("/add-student", methods=["GET", "POST"])
def add_student():
    """Enroll a new student profile."""
    if request.method == "GET":
        return render_template("add_student.html", error=None)

    roll_no = request.form.get("roll_no", "").strip()
    full_name = request.form.get("full_name", "").strip()
    section = request.form.get("section", "").strip().upper() or None

    if not roll_no or not full_name:
        return render_template("add_student.html", error="Roll number and full name are required."), 400

    try:
        execute_query(
            "INSERT INTO students (roll_no, full_name, section) VALUES (%s, %s, %s)",
            (roll_no, full_name, section),
            commit=True,
        )
        flash(f"Student '{full_name}' ({roll_no}) enrolled successfully!", "success")
        return redirect(url_for("manage_students"))
    except Exception as error:
        logger.exception("Failed to add student")
        if getattr(error, "errno", None) == 1062:
            msg = f"Roll number '{roll_no}' already exists. Please provide a unique roll number."
        else:
            msg = "An error occurred while saving student records. Please try again."
        return render_template("add_student.html", error=msg), 400


@app.route("/edit-student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    """Modify an existing student profile."""
    student = execute_query("SELECT * FROM students WHERE student_id = %s", (student_id,), fetch_all=False)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("manage_students"))

    if request.method == "GET":
        return render_template("edit_student.html", student=student, error=None)

    roll_no = request.form.get("roll_no", "").strip()
    full_name = request.form.get("full_name", "").strip()
    section = request.form.get("section", "").strip().upper() or None

    if not roll_no or not full_name:
        return render_template("edit_student.html", student=student, error="Roll number and full name are required."), 400

    try:
        execute_query(
            "UPDATE students SET roll_no = %s, full_name = %s, section = %s WHERE student_id = %s",
            (roll_no, full_name, section, student_id),
            commit=True,
        )
        flash(f"Student '{full_name}' updated successfully!", "success")
        return redirect(url_for("manage_students"))
    except Exception as error:
        logger.exception("Failed to update student")
        if getattr(error, "errno", None) == 1062:
            msg = f"Roll number '{roll_no}' is already in use by another student."
        else:
            msg = "An error occurred while updating student records. Please try again."
        return render_template("edit_student.html", student=student, error=msg), 400


@app.route("/delete-student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    """Delete a student and cascade-remove all associated marks."""
    student = execute_query("SELECT * FROM students WHERE student_id = %s", (student_id,), fetch_all=False)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("manage_students"))

    try:
        execute_query("DELETE FROM students WHERE student_id = %s", (student_id,), commit=True)
        generate_all_charts()
        flash(f"Student '{student['full_name']}' ({student['roll_no']}) deleted successfully.", "info")
    except Exception as error:
        logger.exception("Failed to delete student")
        flash("Unable to delete student. Please try again.", "danger")

    return redirect(url_for("manage_students"))


@app.route("/marks")
def manage_marks():
    """Page D: Marks Ledger. View and filter assessment scores."""
    student_id = request.args.get("student_id", "").strip()
    subject_id = request.args.get("subject_id", "").strip()

    sql = """
        SELECT m.mark_id, m.assessment, m.marks_obtained,
               s.student_id, s.roll_no, s.full_name, s.section,
               sub.subject_id, sub.subject_name, sub.max_marks, sub.pass_marks
        FROM marks m
        JOIN students s ON m.student_id = s.student_id
        JOIN subjects sub ON m.subject_id = sub.subject_id
        WHERE 1=1
    """
    params = []
    if student_id:
        sql += " AND m.student_id = %s"
        params.append(student_id)
    if subject_id:
        sql += " AND m.subject_id = %s"
        params.append(subject_id)

    sql += " ORDER BY s.roll_no, sub.subject_name, m.mark_id ASC"

    marks_records = execute_query(sql, tuple(params))
    students = execute_query("SELECT student_id, roll_no, full_name FROM students ORDER BY roll_no")
    subjects = execute_query("SELECT subject_id, subject_name FROM subjects ORDER BY subject_name")

    for rec in marks_records:
        rec["status"] = "Pass" if rec["marks_obtained"] >= rec["pass_marks"] else "Fail"

    return render_template(
        "marks.html",
        marks=marks_records,
        students=students,
        subjects=subjects,
        selected_student=student_id,
        selected_subject=subject_id,
    )


@app.route("/add-marks", methods=["GET", "POST"])
def add_marks():
    """Record assessment marks for an enrolled student and curriculum subject."""
    students = execute_query("SELECT student_id, roll_no, full_name FROM students ORDER BY full_name")
    subjects = execute_query("SELECT subject_id, subject_name, max_marks, pass_marks FROM subjects ORDER BY subject_name")

    if request.method == "GET":
        return render_template("add_marks.html", students=students, subjects=subjects, error=None)

    student_id = request.form.get("student_id", "").strip()
    subject_id = request.form.get("subject_id", "").strip()
    assessment = request.form.get("assessment", "Internal 1").strip()
    marks_text = request.form.get("marks_obtained", "").strip()

    if not all([student_id, subject_id, assessment, marks_text]):
        return render_template(
            "add_marks.html", students=students, subjects=subjects, error="Please complete all required fields."
        ), 400

    try:
        student_id_val = int(student_id)
        subject_id_val = int(subject_id)
        marks_val = float(marks_text)
    except ValueError:
        return render_template(
            "add_marks.html", students=students, subjects=subjects, error="Please enter valid student, subject, and numeric marks."
        ), 400

    if marks_val < 0:
        return render_template("add_marks.html", students=students, subjects=subjects, error="Marks cannot be negative."), 400

    subject = execute_query("SELECT max_marks, pass_marks FROM subjects WHERE subject_id = %s", (subject_id_val,), fetch_all=False)
    if not subject:
        return render_template("add_marks.html", students=students, subjects=subjects, error="Selected subject does not exist."), 400

    max_allowed = float(subject["max_marks"])
    if marks_val > max_allowed:
        return render_template(
            "add_marks.html", students=students, subjects=subjects, error=f"Marks cannot exceed maximum allowed ({max_allowed})."
        ), 400

    student = execute_query("SELECT student_id FROM students WHERE student_id = %s", (student_id_val,), fetch_all=False)
    if not student:
        return render_template("add_marks.html", students=students, subjects=subjects, error="Selected student does not exist."), 400

    try:
        execute_query(
            "INSERT INTO marks (student_id, subject_id, assessment, marks_obtained) VALUES (%s, %s, %s, %s)",
            (student_id_val, subject_id_val, assessment, marks_val),
            commit=True,
        )
        generate_all_charts()
        flash("Marks recorded successfully!", "success")
        return redirect(url_for("manage_marks"))
    except Exception as error:
        logger.exception("Failed to record marks")
        if getattr(error, "errno", None) == 1062:
            msg = "Marks for this student, subject, and assessment already exist. Please choose a different assessment name or edit the existing record."
        else:
            msg = "An error occurred while saving marks. Please try again."
        return render_template("add_marks.html", students=students, subjects=subjects, error=msg), 400


@app.route("/edit-marks/<int:mark_id>", methods=["GET", "POST"])
def edit_marks(mark_id):
    """Modify an existing assessment marks entry."""
    mark = execute_query("""
        SELECT m.mark_id, m.assessment, m.marks_obtained,
               s.student_id, s.roll_no, s.full_name,
               sub.subject_id, sub.subject_name, sub.max_marks, sub.pass_marks
        FROM marks m
        JOIN students s ON m.student_id = s.student_id
        JOIN subjects sub ON m.subject_id = sub.subject_id
        WHERE m.mark_id = %s
    """, (mark_id,), fetch_all=False)

    if not mark:
        flash("Marks record not found.", "danger")
        return redirect(url_for("manage_marks"))

    if request.method == "GET":
        return render_template("edit_marks.html", mark=mark, error=None)

    assessment = request.form.get("assessment", "").strip()
    marks_text = request.form.get("marks_obtained", "").strip()

    if not assessment or not marks_text:
        return render_template("edit_marks.html", mark=mark, error="Assessment and marks are required."), 400

    try:
        marks_val = float(marks_text)
    except ValueError:
        return render_template("edit_marks.html", mark=mark, error="Marks must be a valid number."), 400

    if marks_val < 0 or marks_val > float(mark["max_marks"]):
        return render_template(
            "edit_marks.html", mark=mark, error=f"Marks must be between 0 and {mark['max_marks']}."
        ), 400

    try:
        execute_query(
            "UPDATE marks SET assessment = %s, marks_obtained = %s WHERE mark_id = %s",
            (assessment, marks_val, mark_id),
            commit=True,
        )
        generate_all_charts()
        flash("Marks record updated successfully!", "success")
        return redirect(url_for("manage_marks"))
    except Exception as error:
        logger.exception("Failed to update marks")
        if getattr(error, "errno", None) == 1062:
            msg = "Another record with this assessment name already exists for this student and subject."
        else:
            msg = "An error occurred while updating the marks record."
        return render_template("edit_marks.html", mark=mark, error=msg), 400


@app.route("/delete-marks/<int:mark_id>", methods=["POST"])
def delete_marks(mark_id):
    """Delete an individual assessment marks record."""
    try:
        execute_query("DELETE FROM marks WHERE mark_id = %s", (mark_id,), commit=True)
        generate_all_charts()
        flash("Marks record deleted successfully.", "info")
    except Exception as error:
        logger.exception("Failed to delete marks record")
        flash("Unable to delete marks record.", "danger")

    return redirect(url_for("manage_marks"))


@app.route("/subjects", methods=["GET", "POST"])
def manage_subjects():
    """Page D: Curriculum courses management and subject registration."""
    error = None
    if request.method == "POST":
        subject_name = request.form.get("subject_name", "").strip()
        max_marks_text = request.form.get("max_marks", "100").strip()
        pass_marks_text = request.form.get("pass_marks", "35").strip()

        if not subject_name:
            error = "Subject name is required."
        else:
            try:
                max_marks = float(max_marks_text)
                pass_marks = float(pass_marks_text)
                if max_marks <= 0:
                    error = "Maximum marks must be greater than zero."
                elif pass_marks < 0 or pass_marks > max_marks:
                    error = "Pass marks must be between 0 and maximum marks."
                else:
                    execute_query(
                        "INSERT INTO subjects (subject_name, max_marks, pass_marks) VALUES (%s, %s, %s)",
                        (subject_name, max_marks, pass_marks),
                        commit=True,
                    )
                    flash(f"Subject '{subject_name}' added successfully!", "success")
                    return redirect(url_for("manage_subjects"))
            except ValueError:
                error = "Please enter valid numeric values for maximum and passing marks."
            except Exception as e:
                logger.exception("Failed to create subject")
                if getattr(e, "errno", None) == 1062:
                    error = f"A subject named '{subject_name}' already exists."
                else:
                    error = "An error occurred while creating the subject."

    subjects = execute_query("""
        SELECT sub.subject_id, sub.subject_name, sub.max_marks, sub.pass_marks,
               COUNT(m.mark_id) AS assessment_count
        FROM subjects sub
        LEFT JOIN marks m ON sub.subject_id = m.subject_id
        GROUP BY sub.subject_id, sub.subject_name, sub.max_marks, sub.pass_marks
        ORDER BY sub.subject_name
    """)

    return render_template("subjects.html", subjects=subjects, error=error)


@app.route("/analysis")
@app.route("/analytics")
def analysis():
    """
    Page C: Analytics & Reports.
    Dedicated hub housing all five analytical visualizations, class competition rankings,
    Topper showcase, At-Risk diagnostic tool with configurable threshold, and summary tables.
    """
    try:
        threshold = request.args.get("threshold", str(Config.ACADEMIC_SUPPORT_THRESHOLD))
        try:
            threshold_val = float(threshold)
        except ValueError:
            threshold_val = Config.ACADEMIC_SUPPORT_THRESHOLD

        active_tab = request.args.get("tab", "charts").strip().lower()

        results = get_student_performance()
        toppers = get_toppers(Config.DEFAULT_TOP_N)
        needing_support = get_students_needing_support(threshold_val)
        charts = generate_all_charts()
        subjects = get_subject_summary()
        sections = get_section_summary()

        return render_template(
            "analysis.html",
            results=results,
            toppers=toppers,
            needing_support=needing_support,
            threshold=threshold_val,
            charts=charts,
            subjects=subjects,
            sections=sections,
            active_tab=active_tab,
        )
    except Exception as error:
        logger.exception("Failed to load performance analysis")
        return "Unable to compute performance analysis. Please try again.", 500


@app.route("/subject-analysis")
def subject_analysis():
    """
    Legacy and direct route for course-wise and cohort-wise performance metrics.
    Renders subject_analysis.html or supports seamless deep-linking.
    """
    try:
        subjects = get_subject_summary()
        sections = get_section_summary()
        charts = generate_all_charts()

        return render_template(
            "subject_analysis.html",
            subjects=subjects,
            sections=sections,
            charts=charts,
        )
    except Exception as error:
        logger.exception("Failed to load subject analysis")
        return "Unable to load subject and cohort analysis.", 500


@app.route("/student-report")
@app.route("/student/<int:student_id>")
def student_report(student_id=None):
    """
    Dedicated Student Profile & Performance Report Card.
    Features student demographics, cumulative standing, course breakdown,
    at-risk intervention alerts, and official print formatting.
    """
    try:
        students = execute_query("SELECT student_id, roll_no, full_name, section FROM students ORDER BY roll_no")
        selected_student_id = str(student_id) if student_id else request.args.get("student_id", "").strip()

        report = None
        if selected_student_id:
            try:
                sid_val = int(selected_student_id)
            except ValueError:
                return "Invalid student selection.", 400

            student = execute_query(
                "SELECT * FROM students WHERE student_id = %s", (sid_val,), fetch_all=False
            )
            if not student:
                return "Student not found.", 404

            # Query all assessment marks for the student
            marks_rows = execute_query("""
                SELECT sub.subject_id, sub.subject_name, sub.max_marks, sub.pass_marks,
                       m.assessment, m.marks_obtained
                FROM marks m
                JOIN subjects sub ON m.subject_id = sub.subject_id
                WHERE m.student_id = %s
                ORDER BY sub.subject_name, m.mark_id ASC
            """, (sid_val,))

            # Use student performance evaluation for consistent overall grade and rank
            all_perf = get_student_performance()
            student_eval = next((s for s in all_perf if s["student_id"] == sid_val), None)

            if student_eval and student_eval["max_total"] > 0:
                report = {
                    "student_id": student["student_id"],
                    "full_name": student["full_name"],
                    "roll_no": student["roll_no"],
                    "section": student["section"] or "-",
                    "total_marks": student_eval["total_marks"],
                    "max_total": student_eval["max_total"],
                    "percentage": student_eval["percentage"],
                    "average_marks": student_eval["average_marks"],
                    "status": student_eval["status"],
                    "grade": student_eval["grade"],
                    "rank": student_eval["rank"],
                    "failed_subjects": student_eval["failed_subjects"],
                    "marks": [
                        {
                            "subject_name": r["subject_name"],
                            "assessment": r["assessment"],
                            "marks_obtained": float(r["marks_obtained"]),
                            "max_marks": float(r["max_marks"]),
                            "pass_marks": float(r["pass_marks"]),
                            "status": "Pass" if float(r["marks_obtained"]) >= float(r["pass_marks"]) else "Fail",
                        }
                        for r in marks_rows
                    ],
                }
            else:
                report = {
                    "student_id": student["student_id"],
                    "full_name": student["full_name"],
                    "roll_no": student["roll_no"],
                    "section": student["section"] or "-",
                    "total_marks": 0.0,
                    "max_total": 0.0,
                    "percentage": 0.0,
                    "average_marks": 0.0,
                    "status": "No Marks Yet",
                    "grade": "N/A",
                    "rank": "-",
                    "failed_subjects": [],
                    "marks": [],
                }

        return render_template(
            "student_report.html",
            students=students,
            selected_student_id=selected_student_id,
            report=report,
        )
    except Exception as error:
        logger.exception("Failed to generate student report")
        return "Unable to generate student report.", 500


# =============================================================================
# REST API ENDPOINTS
# =============================================================================

@app.route("/api/health", methods=["GET"])
def api_health():
    """Health check endpoint validating database connectivity."""
    connected, message = test_connection()
    status_code = 200 if connected else 503
    return jsonify({
        "status": "healthy" if connected else "unhealthy",
        "database": {"connected": connected, "message": message},
        "system": "Student Performance Analysis System"
    }), status_code


@app.route("/api/students", methods=["GET", "POST"])
def api_students():
    """List all students or create a new student record."""
    if request.method == "GET":
        students = execute_query("SELECT student_id, roll_no, full_name, section FROM students ORDER BY roll_no")
        return jsonify({"success": True, "count": len(students), "data": students}), 200

    data = request.get_json(silent=True) or request.form.to_dict()
    roll_no = data.get("roll_no", "").strip()
    full_name = data.get("full_name", "").strip()
    section = data.get("section", "").strip().upper() or None

    if not roll_no or not full_name:
        return jsonify({"success": False, "error": "roll_no and full_name are required"}), 400

    try:
        new_id = execute_query(
            "INSERT INTO students (roll_no, full_name, section) VALUES (%s, %s, %s)",
            (roll_no, full_name, section),
            commit=True,
        )
        return jsonify({
            "success": True,
            "message": "Student created successfully",
            "data": {"student_id": new_id, "roll_no": roll_no, "full_name": full_name, "section": section}
        }), 201
    except Exception as e:
        logger.exception("API error creating student")
        if getattr(e, "errno", None) == 1062:
            return jsonify({"success": False, "error": f"roll_no '{roll_no}' already exists"}), 400
        return jsonify({"success": False, "error": "An internal error occurred while creating the student."}), 500


@app.route("/api/students/<int:student_id>", methods=["GET", "PUT", "DELETE"])
def api_student_detail(student_id):
    """Retrieve, update, or delete an individual student record."""
    student = execute_query("SELECT * FROM students WHERE student_id = %s", (student_id,), fetch_all=False)
    if not student:
        return jsonify({"success": False, "error": f"Student with ID {student_id} not found"}), 404

    if request.method == "GET":
        return jsonify({"success": True, "data": student}), 200

    if request.method == "PUT":
        data = request.get_json(silent=True) or request.form.to_dict()
        roll_no = data.get("roll_no", student["roll_no"]).strip()
        full_name = data.get("full_name", student["full_name"]).strip()
        section = data.get("section", student["section"]).strip().upper() if data.get("section") else None

        if not roll_no or not full_name:
            return jsonify({"success": False, "error": "roll_no and full_name cannot be empty"}), 400

        try:
            execute_query(
                "UPDATE students SET roll_no = %s, full_name = %s, section = %s WHERE student_id = %s",
                (roll_no, full_name, section, student_id),
                commit=True,
            )
            return jsonify({
                "success": True,
                "message": "Student updated successfully",
                "data": {"student_id": student_id, "roll_no": roll_no, "full_name": full_name, "section": section}
            }), 200
        except Exception as e:
            logger.exception("API error updating student")
            if getattr(e, "errno", None) == 1062:
                return jsonify({"success": False, "error": f"roll_no '{roll_no}' already exists"}), 400
            return jsonify({"success": False, "error": "An internal error occurred while updating the student."}), 500

    if request.method == "DELETE":
        try:
            execute_query("DELETE FROM students WHERE student_id = %s", (student_id,), commit=True)
            return jsonify({"success": True, "message": f"Student {student_id} deleted successfully"}), 200
        except Exception:
            logger.exception("API error deleting student")
            return jsonify({"success": False, "error": "An internal error occurred while deleting the student."}), 500


@app.route("/api/subjects", methods=["GET", "POST"])
def api_subjects():
    """List all subjects or register a new curriculum course."""
    if request.method == "GET":
        subjects = execute_query("SELECT * FROM subjects ORDER BY subject_name")
        return jsonify({"success": True, "count": len(subjects), "data": subjects}), 200

    data = request.get_json(silent=True) or request.form.to_dict()
    subject_name = data.get("subject_name", "").strip()
    max_marks = data.get("max_marks", 100)
    pass_marks = data.get("pass_marks", 35)

    if not subject_name:
        return jsonify({"success": False, "error": "subject_name is required"}), 400

    try:
        max_marks = float(max_marks)
        pass_marks = float(pass_marks)
        if max_marks <= 0 or pass_marks < 0 or pass_marks > max_marks:
            return jsonify({"success": False, "error": "Invalid marks constraints (0 <= pass_marks <= max_marks and max_marks > 0)"}), 400

        new_id = execute_query(
            "INSERT INTO subjects (subject_name, max_marks, pass_marks) VALUES (%s, %s, %s)",
            (subject_name, max_marks, pass_marks),
            commit=True,
        )
        return jsonify({
            "success": True,
            "message": "Subject created successfully",
            "data": {"subject_id": new_id, "subject_name": subject_name, "max_marks": max_marks, "pass_marks": pass_marks}
        }), 201
    except ValueError:
        return jsonify({"success": False, "error": "Marks must be numeric"}), 400
    except Exception as e:
        logger.exception("API error creating subject")
        if getattr(e, "errno", None) == 1062:
            return jsonify({"success": False, "error": f"Subject '{subject_name}' already exists"}), 400
        return jsonify({"success": False, "error": "An internal error occurred while registering the subject."}), 500


@app.route("/api/marks", methods=["GET", "POST"])
def api_marks():
    """Query marks ledger or record a new assessment score."""
    if request.method == "GET":
        student_id = request.args.get("student_id")
        subject_id = request.args.get("subject_id")
        sql = """
            SELECT m.mark_id, m.student_id, s.roll_no, s.full_name,
                   m.subject_id, sub.subject_name, sub.max_marks, sub.pass_marks,
                   m.assessment, m.marks_obtained
            FROM marks m
            JOIN students s ON m.student_id = s.student_id
            JOIN subjects sub ON m.subject_id = sub.subject_id
            WHERE 1=1
        """
        params = []
        if student_id:
            sql += " AND m.student_id = %s"
            params.append(student_id)
        if subject_id:
            sql += " AND m.subject_id = %s"
            params.append(subject_id)

        sql += " ORDER BY s.roll_no, sub.subject_name"
        marks = execute_query(sql, tuple(params))
        for m in marks:
            m["marks_obtained"] = float(m["marks_obtained"])
            m["max_marks"] = float(m["max_marks"])
            m["pass_marks"] = float(m["pass_marks"])
            m["status"] = "Pass" if m["marks_obtained"] >= m["pass_marks"] else "Fail"

        return jsonify({"success": True, "count": len(marks), "data": marks}), 200

    data = request.get_json(silent=True) or request.form.to_dict()
    student_id = data.get("student_id")
    subject_id = data.get("subject_id")
    assessment = data.get("assessment", "Internal 1").strip()
    marks_obtained = data.get("marks_obtained")

    if not all([student_id, subject_id, marks_obtained is not None]):
        return jsonify({"success": False, "error": "student_id, subject_id, and marks_obtained are required"}), 400

    try:
        student_id = int(student_id)
        subject_id = int(subject_id)
        marks_obtained = float(marks_obtained)
    except ValueError:
        return jsonify({"success": False, "error": "Invalid numeric values provided"}), 400

    if marks_obtained < 0:
        return jsonify({"success": False, "error": "marks_obtained cannot be negative"}), 400

    subject = execute_query("SELECT max_marks FROM subjects WHERE subject_id = %s", (subject_id,), fetch_all=False)
    if not subject:
        return jsonify({"success": False, "error": f"Subject with ID {subject_id} not found"}), 404

    if marks_obtained > float(subject["max_marks"]):
        return jsonify({"success": False, "error": f"marks_obtained cannot exceed subject maximum ({subject['max_marks']})"}), 400

    student = execute_query("SELECT student_id FROM students WHERE student_id = %s", (student_id,), fetch_all=False)
    if not student:
        return jsonify({"success": False, "error": f"Student with ID {student_id} not found"}), 404

    try:
        new_id = execute_query(
            "INSERT INTO marks (student_id, subject_id, assessment, marks_obtained) VALUES (%s, %s, %s, %s)",
            (student_id, subject_id, assessment, marks_obtained),
            commit=True,
        )
        return jsonify({
            "success": True,
            "message": "Marks recorded successfully",
            "data": {
                "mark_id": new_id,
                "student_id": student_id,
                "subject_id": subject_id,
                "assessment": assessment,
                "marks_obtained": marks_obtained,
            }
        }), 201
    except Exception as e:
        logger.exception("API error recording marks")
        if getattr(e, "errno", None) == 1062:
            return jsonify({"success": False, "error": "Marks for this assessment already exist for this student and subject"}), 400
        return jsonify({"success": False, "error": "An internal error occurred while recording marks."}), 500


@app.route("/api/marks/<int:mark_id>", methods=["GET", "PUT", "DELETE"])
def api_mark_detail(mark_id):
    """Retrieve, update, or delete a specific marks record."""
    mark = execute_query("""
        SELECT m.mark_id, m.student_id, m.subject_id, m.assessment, m.marks_obtained,
               sub.max_marks, sub.pass_marks
        FROM marks m
        JOIN subjects sub ON m.subject_id = sub.subject_id
        WHERE m.mark_id = %s
    """, (mark_id,), fetch_all=False)

    if not mark:
        return jsonify({"success": False, "error": f"Mark record with ID {mark_id} not found"}), 404

    if request.method == "GET":
        mark["marks_obtained"] = float(mark["marks_obtained"])
        mark["max_marks"] = float(mark["max_marks"])
        mark["pass_marks"] = float(mark["pass_marks"])
        return jsonify({"success": True, "data": mark}), 200

    if request.method == "PUT":
        data = request.get_json(silent=True) or request.form.to_dict()
        assessment = data.get("assessment", mark["assessment"]).strip()
        marks_obtained = data.get("marks_obtained", mark["marks_obtained"])

        try:
            marks_obtained = float(marks_obtained)
        except ValueError:
            return jsonify({"success": False, "error": "marks_obtained must be numeric"}), 400

        if marks_obtained < 0 or marks_obtained > float(mark["max_marks"]):
            return jsonify({"success": False, "error": f"marks_obtained must be between 0 and {mark['max_marks']}"}), 400

        try:
            execute_query(
                "UPDATE marks SET assessment = %s, marks_obtained = %s WHERE mark_id = %s",
                (assessment, marks_obtained, mark_id),
                commit=True,
            )
            return jsonify({
                "success": True,
                "message": "Marks record updated",
                "data": {"mark_id": mark_id, "assessment": assessment, "marks_obtained": marks_obtained}
            }), 200
        except Exception:
            logger.exception("API error updating marks record")
            return jsonify({"success": False, "error": "An internal error occurred while updating the marks record."}), 500

    if request.method == "DELETE":
        try:
            execute_query("DELETE FROM marks WHERE mark_id = %s", (mark_id,), commit=True)
            return jsonify({"success": True, "message": f"Mark record {mark_id} deleted"}), 200
        except Exception:
            logger.exception("API error deleting marks record")
            return jsonify({"success": False, "error": "An internal error occurred while deleting the marks record."}), 500


@app.route("/api/analytics/summary", methods=["GET"])
def api_analytics_summary():
    """Retrieve descriptive statistics calculated across all assessment marks via NumPy."""
    summary = get_marks_summary()
    return jsonify({"success": True, "data": summary}), 200


@app.route("/api/analytics/subjects", methods=["GET"])
def api_analytics_subjects():
    """Retrieve subject-wise aggregation and pass percentages via Pandas."""
    summary = get_subject_summary()
    return jsonify({"success": True, "count": len(summary), "data": summary}), 200


@app.route("/api/analytics/sections", methods=["GET"])
def api_analytics_sections():
    """Retrieve section-wise (cohort) aggregation and pass rates via Pandas."""
    summary = get_section_summary()
    return jsonify({"success": True, "count": len(summary), "data": summary}), 200


@app.route("/api/analytics/performance", methods=["GET"])
def api_analytics_performance():
    """Retrieve class-wide student performance rankings, percentages, grades, and status."""
    performance = get_student_performance()
    return jsonify({"success": True, "count": len(performance), "data": performance}), 200


@app.route("/api/analytics/toppers", methods=["GET"])
def api_analytics_toppers():
    """Retrieve top-performing students."""
    limit = request.args.get("limit", str(Config.DEFAULT_TOP_N))
    try:
        limit_val = int(limit)
    except ValueError:
        limit_val = Config.DEFAULT_TOP_N
    toppers = get_toppers(limit_val)
    return jsonify({"success": True, "count": len(toppers), "data": toppers}), 200


@app.route("/api/analytics/support-needed", methods=["GET"])
def api_analytics_support():
    """Retrieve students requiring academic intervention based on a configurable threshold."""
    threshold = request.args.get("threshold", str(Config.ACADEMIC_SUPPORT_THRESHOLD))
    try:
        threshold_val = float(threshold)
    except ValueError:
        threshold_val = Config.ACADEMIC_SUPPORT_THRESHOLD

    needing_support = get_students_needing_support(threshold_val)
    return jsonify({
        "success": True,
        "threshold": threshold_val,
        "count": len(needing_support),
        "data": needing_support
    }), 200


@app.route("/api/charts/refresh", methods=["POST"])
def api_refresh_charts():
    """Trigger manual regeneration of all analytical charts."""
    charts = generate_all_charts()
    return jsonify({"success": True, "message": "Charts regenerated successfully", "charts": charts}), 200


if __name__ == "__main__":
    # Server startup diagnostics
    ok, diag = test_connection()
    if ok:
        logger.info("Database connectivity confirmed: %s", diag)
    else:
        logger.warning("DATABASE WARNING: %s", diag)
        logger.warning("Please check your .env configuration and ensure MySQL is running.")

    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
