-- Create the database
CREATE DATABASE IF NOT EXISTS labclass_db;
USE labclass_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'Student', 'Academic Coordinator', 'Lab InCharge', 'Faculty/Staff', 'System Administrator'
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    requires_approval BOOLEAN NOT NULL DEFAULT TRUE,
    date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL
);

-- Add system administrator account
INSERT INTO users (id, full_name, email, password, role, is_approved, requires_approval) 
VALUES ('admin', 'System Administrator', 'admin@uic.edu', '$2b$12$I42gD8WSUhcNyYDEhJKuaeVkTH/YmIYrK6j/TqwrC4RUaEIjLnzpy', 'System Administrator', TRUE, FALSE);
-- This password is 'admin123' hashed with bcrypt

-- Role-based permissions
CREATE TABLE IF NOT EXISTS role_permissions (
    role VARCHAR(50) PRIMARY KEY,
    permissions JSON NOT NULL
);

-- Insert default role permissions
INSERT INTO role_permissions (role, permissions) VALUES 
('Student', '{"view_schedule": true, "view_profile": true}'),
('Academic Coordinator', '{"view_schedule": true, "manage_schedule": true, "view_profile": true}'),
('Lab InCharge', '{"view_schedule": true, "view_lab_schedule": true, "view_profile": true}'),
('Faculty/Staff', '{"view_schedule": true, "view_profile": true}'),
('System Administrator', '{"view_schedule": true, "manage_schedule": true, "manage_users": true, "view_profile": true, "approve_users": true}');

-- User sessions table for authentication
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Audit log for tracking system events
CREATE TABLE IF NOT EXISTS audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36),
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Semesters table
CREATE TABLE IF NOT EXISTS semesters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample semesters
INSERT INTO semesters (name, is_active) VALUES 
('1st Sem 2025-2026', TRUE),
('2nd Sem 2025-2026', FALSE),
('Summer 2026', FALSE),
('1st Sem 2026-2027', FALSE),
('2nd Sem 2026-2027', FALSE),
('Summer 2027', FALSE);

-- Course offerings table
CREATE TABLE IF NOT EXISTS course_offerings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    semester_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE CASCADE
);

-- Lab rooms
CREATE TABLE IF NOT EXISTS lab_rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    capacity INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert default lab rooms
INSERT INTO lab_rooms (name) VALUES
('L201'), ('L202'), ('L203'), ('L204'), ('L205'), ('IOT');

-- Schedules table
CREATE TABLE IF NOT EXISTS schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    details TEXT,
    semester_id INT NOT NULL,
    section VARCHAR(20) NOT NULL,
    course_code VARCHAR(20) NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    day VARCHAR(10) NOT NULL,
    lab_room_id INT NOT NULL,
    instructor_name VARCHAR(100) NOT NULL,
    start_time VARCHAR(10) NOT NULL,
    end_time VARCHAR(10) NOT NULL,
    duration INT NOT NULL,
    schedule_types VARCHAR(20) NOT NULL,
    color VARCHAR(7) DEFAULT '#DD385A',
    created_by VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE CASCADE,
    FOREIGN KEY (lab_room_id) REFERENCES lab_rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Create index for faster filtering
CREATE INDEX idx_schedules_semester ON schedules(semester_id);
CREATE INDEX idx_schedules_lab_room ON schedules(lab_room_id); 