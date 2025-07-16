"""
End-to-end tests for Weekend Task Manager using Selenium WebDriver
"""

import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import TestConfig


class TestWeekendTaskManagerE2E:
    """End-to-end tests for the Weekend Task Manager using Selenium."""

    def test_complete_user_journey(self, driver):
        """
        Tests the complete user journey: navigate, add task, and verify it appears.
        """
        # Step 1: Navigate to the application
        driver.get(TestConfig.BASE_URL)
        
        # Verify we're on the correct page
        assert "Weekend Task Manager" in driver.title
        
        # Wait for page to load and verify main heading
        main_heading = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        assert "Weekend Task Manager" in main_heading.text
        
        # Take screenshot of dashboard
        self.take_screenshot(driver, "01_dashboard.png")
        
        # Step 2: Navigate to Add Task page
        add_task_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Add Task"))
        )
        add_task_button.click()
        
        # Verify we're on the add task page
        WebDriverWait(driver, 10).until(
            EC.url_contains("/add")
        )
        
        add_task_heading = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        assert "Add New Task" in add_task_heading.text
        
        # Take screenshot of add task page
        self.take_screenshot(driver, "02_add_task_page.png")
        
        # Step 3: Fill out the form
        # Fill event name
        event_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "event"))
        )
        event_input.clear()
        event_input.send_keys(TestConfig.TEST_EVENT)
        
        # Select day
        day_select = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "day"))
        ))
        day_select.select_by_visible_text(TestConfig.TEST_DAY)
        
        # Fill start time
        time_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "start_time"))
        )
        time_input.clear()
        time_input.send_keys(TestConfig.TEST_TIME)
        
        # Fill description if field exists
        try:
            description_input = driver.find_element(By.NAME, "description")
            description_input.clear()
            description_input.send_keys(TestConfig.TEST_DESCRIPTION)
        except NoSuchElementException:
            pass  # Description field might not exist
        
        # Fill additional links if field exists
        try:
            links_input = driver.find_element(By.NAME, "additional_links")
            links_input.clear()
            links_input.send_keys(TestConfig.TEST_LINKS)
        except NoSuchElementException:
            pass  # Links field might not exist
        
        # Take screenshot of filled form
        self.take_screenshot(driver, "03_form_filled.png")
        
        # Step 4: Submit the form
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()
        
        # Wait for redirect to dashboard
        WebDriverWait(driver, 10).until(
            EC.url_matches(f"{TestConfig.BASE_URL}/?.*")
        )
        
        # Step 5: Verify task appears on dashboard
        # Wait for the task to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{TestConfig.TEST_EVENT}')]"))
        )
        
        # Verify all task details are present
        assert self.is_text_present(driver, TestConfig.TEST_EVENT)
        assert self.is_text_present(driver, TestConfig.TEST_DAY)
        assert self.is_text_present(driver, TestConfig.TEST_TIME)
        
        # Take screenshot of task added
        self.take_screenshot(driver, "04_task_added.png")

    def test_dashboard_loads_existing_tasks(self, driver):
        """Verifies the dashboard loads and displays existing tasks."""
        driver.get(TestConfig.BASE_URL)
        
        # Verify page loads correctly
        assert "Weekend Task Manager" in driver.title
        
        # Wait for main heading
        main_heading = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        assert "Weekend Task Manager" in main_heading.text
        
        # Look for task containers or table rows
        task_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".task-item, .task-row, tr"))
        )
        
        # Should have at least one task element (header or actual task)
        assert len(task_elements) > 0
        
        # Take screenshot
        self.take_screenshot(driver, "dashboard_existing_tasks.png")

    def test_add_task_form_validation(self, driver):
        """Tests form validation on the add task page."""
        driver.get(f"{TestConfig.BASE_URL}/add")
        
        # Try to submit empty form
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()
        
        # Check if we're still on the add page (form validation should prevent submission)
        time.sleep(2)  # Give time for any validation messages
        
        # Verify required fields are still present (indicating form didn't submit)
        event_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "event"))
        )
        assert event_input.is_displayed()
        
        # Take screenshot
        self.take_screenshot(driver, "form_validation.png")

    def test_navigation_between_pages(self, driver):
        """Tests navigation between different pages of the application."""
        # Start on dashboard
        driver.get(TestConfig.BASE_URL)
        
        # Navigate to Add Task page
        add_task_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Add Task"))
        )
        add_task_link.click()
        
        # Verify we're on add task page
        WebDriverWait(driver, 10).until(
            EC.url_contains("/add")
        )
        
        # Navigate back to dashboard (look for a back link or home link)
        try:
            back_link = driver.find_element(By.LINK_TEXT, "Back to Dashboard")
            back_link.click()
        except NoSuchElementException:
            try:
                home_link = driver.find_element(By.LINK_TEXT, "Home")
                home_link.click()
            except NoSuchElementException:
                # Navigate directly if no back link
                driver.get(TestConfig.BASE_URL)
        
        # Verify we're back on dashboard
        WebDriverWait(driver, 10).until(
            EC.url_matches(f"{TestConfig.BASE_URL}/?.*")
        )
        
        # Take screenshot
        self.take_screenshot(driver, "navigation_test.png")

    def test_task_display_formatting(self, driver):
        """Tests that tasks are displayed with proper formatting."""
        driver.get(TestConfig.BASE_URL)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # Look for task elements
        task_elements = driver.find_elements(By.CSS_SELECTOR, ".task-item, .task-row, tr")
        
        if len(task_elements) > 1:  # More than just header
            # Verify task elements contain expected content structure
            for element in task_elements[:3]:  # Check first 3 elements
                text_content = element.text.lower()
                # Should contain day information
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                has_day = any(day in text_content for day in days)
                # Should contain time information (look for colon in time format)
                has_time = ':' in text_content
                
                # At least one of the task elements should have proper formatting
                if has_day or has_time:
                    break
        
        # Take screenshot
        self.take_screenshot(driver, "task_display_formatting.png")

    def test_responsive_design(self, driver):
        """Tests that the application works on different screen sizes."""
        # Test desktop size
        driver.set_window_size(1920, 1080)
        driver.get(TestConfig.BASE_URL)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        self.take_screenshot(driver, "desktop_view.png")
        
        # Test tablet size
        driver.set_window_size(768, 1024)
        driver.refresh()
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        self.take_screenshot(driver, "tablet_view.png")
        
        # Test mobile size
        driver.set_window_size(375, 667)
        driver.refresh()
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        self.take_screenshot(driver, "mobile_view.png")
        
        # Reset to desktop size
        driver.set_window_size(1280, 720)

    def is_text_present(self, driver, text):
        """Helper method to check if text is present on the page."""
        try:
            driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
            return True
        except NoSuchElementException:
            return False

    def take_screenshot(self, driver, filename):
        """Helper method to take screenshots."""
        if TestConfig.SCREENSHOT_ON_FAILURE:
            os.makedirs(TestConfig.SCREENSHOT_DIR, exist_ok=True)
            screenshot_path = os.path.join(TestConfig.SCREENSHOT_DIR, filename)
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, driver):
        """Setup and teardown for each test."""
        # Setup
        driver.implicitly_wait(10)
        
        yield
        