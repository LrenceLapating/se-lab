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