from locust import HttpUser, task, between

class WeekendAppUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_dashboard(self):
        """Load dashboard page"""
        self.client.get("/")
    
    @task(2)
    def view_add_task(self):
        """Load add task page"""
        self.client.get("/add")
    
    @task(1)
    def api_get_tasks(self):
        """Test API get tasks"""
        self.client.get("/api/tasks")
    
    @task(1)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/health")
    
    def on_start(self):
        """Run on user start"""
        self.client.get("/health")