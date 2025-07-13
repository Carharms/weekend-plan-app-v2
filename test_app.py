#!/usr/bin/env python3
"""
Test suite for Weekend Task Manager Flask Application
"""

import unittest
import json
import sys
import os

# alter this and determine what testing logic to use - selenium?
# test for Jenkins
from unittest.mock import patch, MagicMock

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, get_db_connection, init_db

class WeekendTaskManagerTests(unittest.TestCase):
    """Test cases for Weekend Task Manager"""
    
    def setUp(self):
        """Set up test client and configuration"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_dashboard_route(self):
        """Test dashboard route accessibility"""
        with patch('app.get_db_connection') as mock_db:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_connection.cursor.return_value = mock_cursor
            mock_db.return_value = mock_connection
            
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            
    def test_add_task_get_route(self):
        """Test add task GET route"""
        response = self.client.get('/add')
        self.assertEqual(response.status_code, 200)
        
    def test_health_check_healthy(self):
        """Test health check endpoint when database is healthy"""
        with patch('app.get_db_connection') as mock_db:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_db.return_value = mock_connection
            
            response = self.client.get('/health')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'healthy')
            
    def test_health_check_unhealthy(self):
        """Test health check endpoint when database is unhealthy"""
        with patch('app.get_db_connection') as mock_db:
            mock_db.return_value = None
            
            response = self.client.get('/health')
            self.assertEqual(response.status_code, 503)
            
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'unhealthy')
            
    def test_api_get_tasks(self):
        """Test API endpoint for getting tasks"""
        with patch('app.get_db_connection') as mock_db:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                {
                    'id': 1,
                    'event': 'Test Event',
                    'day': 'Saturday',
                    'start_time': '10:00:00',
                    'description': 'Test Description',
                    'additional_links': '',
                    'created_at': '2025-01-01T10:00:00'
                }
            ]
            mock_connection.cursor.return_value = mock_cursor
            mock_db.return_value = mock_connection
            
            response = self.client.get('/api/tasks')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIn('tasks', data)
            self.assertEqual(len(data['tasks']), 1)
            
    def test_api_create_task_success(self):
        """Test API endpoint for creating a task successfully"""
        with patch('app.get_db_connection') as mock_db:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = {
                'id': 1,
                'event': 'New Event',
                'day': 'Sunday',
                'start_time': '14:00:00',
                'description': 'New Description',
                'additional_links': '',
                'created_at': '2025-01-01T14:00:00'
            }
            mock_connection.cursor.return_value = mock_cursor
            mock_db.return_value = mock_connection
            
            task_data = {
                'event': 'New Event',
                'day': 'Sunday',
                'start_time': '14:00:00',
                'description': 'New Description',
                'additional_links': ''
            }
            
            response = self.client.post('/api/tasks', 
                                     data=json.dumps(task_data),
                                     content_type='application/json')
            self.assertEqual(response.status_code, 201)
            
            data = json.loads(response.data)
            self.assertIn('task', data)
            self.assertEqual(data['task']['event'], 'New Event')
            
    def test_api_create_task_missing_fields(self):
        """Test API endpoint for creating a task with missing fields"""
        task_data = {
            'event': 'Incomplete Event'
            # Missing day and start_time
        }
        
        response = self.client.post('/api/tasks', 
                                 data=json.dumps(task_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Missing required fields')

    def test_add_task_post_success(self):
        """Test adding a task via POST form"""
        with patch('app.get_db_connection') as mock_db:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_db.return_value = mock_connection
            
            task_data = {
                'event': 'Form Event',
                'day': 'Friday',
                'start_time': '18:00',
                'description': 'Form Description',
                'additional_links': 'http://example.com'
            }
            
            response = self.client.post('/add', data=task_data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()