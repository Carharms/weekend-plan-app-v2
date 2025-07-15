from locust import HttpUser, task, between
import json

class WeekendTaskUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup for each user"""
        self.client.verify = False
        
    @task(3)
    def view_dashboard(self):
        """Test dashboard loading"""
        self.client.get("/")
        
    @task(1)
    def view_add_task_form(self):
        """Test add task form loading"""
        self.client.get("/add")
        
    @task(2)
    def api_get_tasks(self):
        """Test API endpoint for getting tasks"""
        self.client.get("/api/tasks")
        
    @task(1)
    def api_create_task(self):
        """Test API endpoint for creating task"""
        task_data = {
            "event": "Check test event",
            "day": "Sunday",
            "start_time": "8:00:00",
            "description": "This is a create task test",
            "additional_links": "test.com"
        }
        
        self.client.post("/api/tasks", 
                        json=task_data,
                        headers={"Content-Type": "application/json"})
        
    @task(1)
    def health_check(self):
        """Test health check endpoint"""
        self.client.get("/health")