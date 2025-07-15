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
    -- DOUBLE CHECK, ensure this matches app.py and other data
    description VARCHAR(500),
    additional_links TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suggestion of using indexes: should you implement?
-- https://www.youtube.com/watch?v=gvRS9PxJivc
CREATE INDEX idx_day ON weekend_tasks(day);
CREATE INDEX idx_start_time ON weekend_tasks(start_time);

-- DOES THE FOLLOWING SEED A TEST DB?
-- q6 - DOES THIS FILE DO EVERYTHING?
-- NEED SCREENSHOT OF DB SEEDING
INSERT INTO weekend_tasks (event, day, start_time, description, additional_links) VALUES
('Morning Run', 'Friday', '06:30:00', '7 miles along the lakefront', 'https://example.com/route'),
('Work', 'Friday', '8:00:00', 'Finish weekly overview for leadership', NULL),
('Night in', 'Friday', '18:00:00', 'Find new movie on Amazon Prime', NULL),
('Read', 'Saturday', '07:00:00', 'Continue House of Morgan book', NULL),
('Homework', 'Saturday', '9:00:00', 'DevOps assignment', NULL),
('Night Out', 'Saturday', '18:00:00', 'Bars in Gold Coast', NULL),
('Yoga', 'Sunday', '08:00:00', 'Sunrise yoga', NULL);