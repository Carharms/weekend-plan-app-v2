-- DB Outline for weekend-plan-app
-- MySQL version: ??

-- Create DB and use DB
CREATE DATABASE IF NOT EXISTS weekend_tasks;
USE weekend_tasks;

-- Create weekend_tasks table
CREATE TABLE IF NOT EXISTS weekend_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event VARCHAR(255) NOT NULL,
    day ENUM('Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time TIME NOT NULL,
    description VARCHAR(500),
    additional_links TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suggestion of using indexes: should you implement?
-- https://www.youtube.com/watch?v=gvRS9PxJivc
CREATE INDEX idx_day ON weekend_tasks(day);
CREATE INDEX idx_start_time ON weekend_tasks(start_time);
