-- =============================================================================
-- Student Performance Analysis System - Seed / Sample Dataset
-- Deliverable D2: Sample Academic Data
-- =============================================================================

USE student_performance;

-- Disable foreign key checks for clean reload if needed
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE marks;
TRUNCATE TABLE subjects;
TRUNCATE TABLE students;
SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- 1. Insert Sample Subjects
-- -----------------------------------------------------------------------------
INSERT INTO subjects (subject_id, subject_name, max_marks, pass_marks) VALUES
(1, 'Python Programming', 100.00, 35.00),
(2, 'Database Management Systems', 100.00, 35.00),
(3, 'Applied Mathematics', 100.00, 35.00),
(4, 'Web Development', 100.00, 35.00);

-- -----------------------------------------------------------------------------
-- 2. Insert Sample Students
-- -----------------------------------------------------------------------------
INSERT INTO students (student_id, roll_no, full_name, section) VALUES
(1, 'CSE001', 'Aarav Kumar', 'A'),
(2, 'CSE002', 'Priya Sharma', 'A'),
(3, 'CSE003', 'Rahul Reddy', 'B'),
(4, 'CSE004', 'Sneha Patel', 'B'),
(5, 'CSE005', 'Arjun Rao', 'A'),
(6, 'CSE006', 'Mohammad Usman', 'C'),
(7, 'CSE007', 'Ananya Gupta', 'C'),
(8, 'CSE008', 'Vikram Singh', 'B'),
(9, 'CSE009', 'Divya Nair', 'A'),
(10, 'CSE010', 'Karan Verma', 'C');

-- -----------------------------------------------------------------------------
-- 3. Insert Assessment Marks (Internal 1)
-- -----------------------------------------------------------------------------
INSERT INTO marks (student_id, subject_id, assessment, marks_obtained) VALUES
-- Aarav Kumar (CSE001 - Sec A) - Solid Performer (Average ~85%)
(1, 1, 'Internal 1', 85.00),
(1, 2, 'Internal 1', 78.00),
(1, 3, 'Internal 1', 92.00),
(1, 4, 'Internal 1', 88.00),

-- Priya Sharma (CSE002 - Sec A) - Topper Candidate (Average ~91%)
(2, 1, 'Internal 1', 92.00),
(2, 2, 'Internal 1', 88.00),
(2, 3, 'Internal 1', 95.00),
(2, 4, 'Internal 1', 90.00),

-- Rahul Reddy (CSE003 - Sec B) - Average Performer (Average ~66%)
(3, 1, 'Internal 1', 65.00),
(3, 2, 'Internal 1', 72.00),
(3, 3, 'Internal 1', 60.00),
(3, 4, 'Internal 1', 68.00),

-- Sneha Patel (CSE004 - Sec B) - Low Performer (Failed Python, Needs Support)
(4, 1, 'Internal 1', 30.00), -- Failed (< 35)
(4, 2, 'Internal 1', 45.00),
(4, 3, 'Internal 1', 50.00),
(4, 4, 'Internal 1', 42.00),

-- Arjun Rao (CSE005 - Sec A) - Class Topper (Average ~94%)
(5, 1, 'Internal 1', 96.00),
(5, 2, 'Internal 1', 91.00),
(5, 3, 'Internal 1', 94.00),
(5, 4, 'Internal 1', 95.00),

-- Mohammad Usman (CSE006 - Sec C) - Top Performer (Average ~89%)
(6, 1, 'Internal 1', 90.00),
(6, 2, 'Internal 1', 85.00),
(6, 3, 'Internal 1', 89.00),
(6, 4, 'Internal 1', 92.00),

-- Ananya Gupta (CSE007 - Sec C) - High Performer (Average ~82%)
(7, 1, 'Internal 1', 84.00),
(7, 2, 'Internal 1', 80.00),
(7, 3, 'Internal 1', 78.00),
(7, 4, 'Internal 1', 86.00),

-- Vikram Singh (CSE008 - Sec B) - Low Performer (Failed Maths & Web Dev, Needs Support)
(8, 1, 'Internal 1', 40.00),
(8, 2, 'Internal 1', 36.00),
(8, 3, 'Internal 1', 28.00), -- Failed (< 35)
(8, 4, 'Internal 1', 32.00), -- Failed (< 35)

-- Divya Nair (CSE009 - Sec A) - Very Good Performer (Average ~77%)
(9, 1, 'Internal 1', 76.00),
(9, 2, 'Internal 1', 74.00),
(9, 3, 'Internal 1', 82.00),
(9, 4, 'Internal 1', 77.00),

-- Karan Verma (CSE010 - Sec C) - Borderline Performer (Average ~48%, Passed all)
(10, 1, 'Internal 1', 45.00),
(10, 2, 'Internal 1', 48.00),
(10, 3, 'Internal 1', 52.00),
(10, 4, 'Internal 1', 46.00);
