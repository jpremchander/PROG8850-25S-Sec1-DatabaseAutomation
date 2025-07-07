-- PROG8850 Assignment 3 - Database Setup
-- Create database and users table

CREATE DATABASE IF NOT EXISTS loginapp;
USE loginapp;

-- Create user for the application
CREATE USER IF NOT EXISTS 'loginappuser'@'%' IDENTIFIED BY 'LoginAppDbPwd@2025';
GRANT ALL PRIVILEGES ON loginapp.* TO 'loginappuser'@'%';
FLUSH PRIVILEGES;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_created_at (created_at)
);

-- Insert sample data
INSERT IGNORE INTO users (username, password) VALUES 
('testuser1', 'password123'),
('testuser2', 'password456'),
('admin', 'admin123');

-- Show table structure and data
DESCRIBE users;
SELECT * FROM users;
