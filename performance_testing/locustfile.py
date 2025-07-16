from locust import HttpUser, task, between
import json

from locust import HttpUser, task

class WebsiteTest(HttpUser):
    @task
    def load_home(self):
        self.client.get("/")