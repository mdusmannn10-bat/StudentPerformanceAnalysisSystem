-- =============================================================================
-- Student Performance Analysis System - Database Schema
-- Deliverable D2: Relational Schema Definition
-- =============================================================================

CREATE DATABASE IF NOT EXISTS student_performance
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE student_performance;

-- -----------------------------------------------------------------------------
-- 1. Students Table
-- Stores student profile information including roll number, full name, and section.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    section VARCHAR(20) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 2. Subjects Table
-- Stores academic subject details including maximum permitted marks and pass marks.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL UNIQUE,
    max_marks DECIMAL(6,2) NOT NULL DEFAULT 100.00,
    pass_marks DECIMAL(6,2) NOT NULL DEFAULT 35.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_subject_max_marks CHECK (max_marks > 0),
    CONSTRAINT chk_subject_pass_marks CHECK (pass_marks >= 0 AND pass_marks <= max_marks)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 3. Marks Table
-- Stores individual assessment results referencing students and subjects.
-- Foreign keys are configured with ON DELETE CASCADE to maintain referential integrity.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    assessment VARCHAR(50) NOT NULL DEFAULT 'Internal 1',
    marks_obtained DECIMAL(6,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_marks_student FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_marks_subject FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_marks_non_negative CHECK (marks_obtained >= 0),
    CONSTRAINT uq_student_subject_assessment UNIQUE (student_id, subject_id, assessment)
) ENGINE=InnoDB;
