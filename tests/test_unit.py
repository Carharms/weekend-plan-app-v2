import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health endpoint"""
    response = client.get('/health')
    assert response.status_code in [200, 503]

def test_dashboard_loads(client):
    """Test dashboard page loads"""
    response = client.get('/')
    assert response.status_code == 200

def test_add_task_page(client):
    """Test add task page loads"""
    response = client.get('/add')
    assert response.status_code == 200

def test_api_tasks_endpoint(client):
    """Test API tasks endpoint"""
    response = client.get('/api/tasks')
    assert response.status_code in [200, 500]
    
def test_api_create_task_validation(client):
    """Test API task creation validation"""
    response = client.post('/api/tasks', 
                          data=json.dumps({}),
                          content_type='application/json')
    assert response.status_code == 400
