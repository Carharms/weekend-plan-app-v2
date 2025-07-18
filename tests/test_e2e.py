import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time

@pytest.fixture
# requirements of selenium
def driver():
    """Setup Chrome driver"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def test_complete_user_journey(driver):
    """Test complete user journey"""
    base_url = "http://localhost:5000"
    
    # start at dashboard
    driver.get(base_url)
    assert "Weekend Task Manager" in driver.title
    
    # selection of add task button
    add_task_link = driver.find_element(By.LINK_TEXT, "Add Task")
    add_task_link.click()
    
    # complete task
    driver.find_element(By.ID, "event").send_keys("Test Event")
    
    day_select = Select(driver.find_element(By.ID, "day"))
    day_select.select_by_value("Saturday")
    
    driver.find_element(By.ID, "start_time").send_keys("10:00")
    driver.find_element(By.ID, "description").send_keys("Test Description")
    
    # Submit form
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    # return to dashboard
    assert base_url in driver.current_url
    
    # determine if tasks appears
    page_source = driver.page_source
    assert "Test Event" in page_source

def test_dashboard_navigation(driver):
    """Test dashboard navigation"""
    driver.get("http://localhost:5000")
    
    # test for nav links
    nav_links = driver.find_elements(By.CSS_SELECTOR, ".nav a")
    assert len(nav_links) >= 2
    
    # test for weekend grid in html
    weekend_grid = driver.find_element(By.CLASS_NAME, "weekend-grid")
    assert weekend_grid.is_displayed()
    
    # test for day columns in html
    day_columns = driver.find_elements(By.CLASS_NAME, "day-column")
    assert len(day_columns) == 3