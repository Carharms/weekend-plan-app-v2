import pytest
from playwright.sync_api import Page, expect
from config import TestConfig

class TestWeekendTaskManagerE2E:
    """End-to-end tests for the Weekend Task Manager."""

    def test_complete_user_journey(self, page: Page):
        """
        Tests the complete user journey: navigate, add task, and verify it appears.
        """
        page.goto(TestConfig.BASE_URL)
        expect(page).to_have_title("Weekend Task Manager")
        expect(page.locator("h1")).to_contain_text("Weekend Task Manager")
        page.screenshot(path="e2e_tests/screenshots/01_dashboard.png")

        page.locator("text=Add Task").first.click()
        expect(page).to_have_url(f"{TestConfig.BASE_URL}/add")
        expect(page.locator("h1")).to_contain_text("Add New Task")
        page.screenshot(path="e2e_tests/screenshots/02_add_task_page.png")

        page.locator("input[name='event']").fill(TestConfig.TEST_EVENT)
        page.locator("select[name='day']").select_option(TestConfig.TEST_DAY)
        page.locator("input[name='start_time']").fill(TestConfig.TEST_TIME)
        
        description_input = page.locator("textarea[name='description']")
        if description_input.is_visible():
            description_input.fill(TestConfig.TEST_DESCRIPTION)
        
        links_input = page.locator("input[name='additional_links']")
        if links_input.is_visible():
            links_input.fill(TestConfig.TEST_LINKS)
        
        page.screenshot(path="e2e_tests/screenshots/03_form_filled.png")

        with page.expect_navigation():
            page.locator("button[type='submit']").click()
        
        expect(page).to_have_url(TestConfig.BASE_URL + "/")
        page.wait_for_load_state("networkidle")

        expect(page.locator(f"text={TestConfig.TEST_EVENT}")).to_be_visible()
        expect(page.locator(f"text={TestConfig.TEST_DAY}")).to_be_visible()
        expect(page.locator(f"text={TestConfig.TEST_TIME}")).to_be_visible()
        page.screenshot(path="e2e_tests/screenshots/04_task_added.png")

    def test_dashboard_loads_existing_tasks(self, page: Page):
        """Verifies the dashboard loads and displays existing tasks."""
        page.goto(TestConfig.BASE_URL)
        expect(page).to_have_title("Weekend Task Manager")
        expect(page.locator("h1")).to_contain_text("Weekend Task Manager")
        expect(page.locator(".task-item, .task-row, tr").first).to_be_visible()
        page.screenshot(path="e2e_tests/screenshots/dashboard_existing_tasks.png")

    def test_add_task_form_validation(self, page: Page):
        """Tests form validation on the add task page."""
        page.goto(f"{TestConfig.BASE_URL}/add")
        page.locator("button[type='submit']").click()
        expect(page.locator("input[name='event']")).to_be_visible()
        page.screenshot(path="e2e_tests/screenshots/form_validation.png")

    def test_api_endpoint_accessibility(self, page: Page):
        """Confirms API endpoints are accessible."""
        response = page.request.get(f"{TestConfig.BASE_URL}/api/tasks")
        assert response.status == 200
        data = response.json()
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_health_check_endpoint(self, page: Page):
        """Tests the health check endpoint."""
        response = page.request.get(f"{TestConfig.BASE_URL}/health")
        assert response.status == 200
        data = response.json()
        assert data["status"] == "healthy"


"""
pip install -r requirements.txt
chmod +x e2e_tests/install_playwright.sh
chmod +x e2e_tests/run_e2e_tests.sh
cd e2e_tests
./run_e2e_tests.sh
"""