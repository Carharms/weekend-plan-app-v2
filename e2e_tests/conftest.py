"""
Pytest configuration for Selenium E2E tests
"""

import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from config import TestConfig


@pytest.fixture(scope="session")
def driver_init():
    """Initialize the WebDriver for the session."""
    browser = os.getenv('BROWSER', 'chrome').lower()
    
    if browser == 'chrome':
        chrome_options = Options()
        
        if TestConfig.BROWSER_HEADLESS:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1280,720')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-javascript')
        chrome_options.add_argument('--disable-default-apps')
        
        # Enable JavaScript for our tests
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
    elif browser == 'firefox':
        firefox_options = FirefoxOptions()
        
        if TestConfig.BROWSER_HEADLESS:
            firefox_options.add_argument('--headless')
        
        firefox_options.add_argument('--width=1280')
        firefox_options.add_argument('--height=720')
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=firefox_options)
        
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    
    # Set timeouts
    driver.implicitly_wait(TestConfig.DEFAULT_TIMEOUT / 1000)  # Convert to seconds
    driver.set_page_load_timeout(TestConfig.NAVIGATION_TIMEOUT / 1000)
    
    yield driver
    
    driver.quit()


@pytest.fixture
def driver(driver_init):
    """Create a new driver instance for each test."""
    # Reset driver state for each test
    driver_init.delete_all_cookies()
    
    yield driver_init
    
    # Cleanup after each test
    try:
        driver_init.execute_script("window.localStorage.clear();")
        driver_init.execute_script("window.sessionStorage.clear();")
    except:
        pass  # Ignore errors during cleanup


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, driver):
    """Take screenshot on test failure."""
    yield
    
    # Check if test failed
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        if TestConfig.SCREENSHOT_ON_FAILURE:
            # Create screenshots directory if it doesn't exist
            os.makedirs(TestConfig.SCREENSHOT_DIR, exist_ok=True)
            
            # Generate screenshot filename
            test_name = request.node.name
            screenshot_path = os.path.join(TestConfig.SCREENSHOT_DIR, f"{test_name}_failure.png")
            
            # Take screenshot
            try:
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"Failed to take screenshot: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for screenshot fixture."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests."""
    # Create necessary directories
    os.makedirs(TestConfig.SCREENSHOT_DIR, exist_ok=True)
    
    # You can add more setup logic here
    print(f"Setting up test environment...")
    print(f"Base URL: {TestConfig.BASE_URL}")
    print(f"Screenshots will be saved to: {TestConfig.SCREENSHOT_DIR}")
    print(f"Headless mode: {TestConfig.BROWSER_HEADLESS}")
    
    yield
    
    # Cleanup after all tests
    print("Cleaning up test environment...")


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "smoke: marks tests as smoke tests"
    )
    config.addinivalue_line(
        "markers", "regression: marks tests as regression tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add smoke marker to basic tests
        if "dashboard" in item.name or "navigation" in item.name:
            item.add_marker(pytest.mark.smoke)
        
        # Add regression marker to comprehensive tests
        if "complete_user_journey" in item.name or "form_validation" in item.name:
            item.add_marker(pytest.mark.regression)
        
        # Add slow marker to tests that might take longer
        if "responsive" in item.name or "formatting" in item.name:
            item.add_marker(pytest.mark.slow)