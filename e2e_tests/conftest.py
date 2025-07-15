"""
Pytest configuration for E2E tests
"""

import pytest
import os
from playwright.sync_api import sync_playwright
from config import TestConfig

@pytest.fixture(scope="session")
def browser_context():
    """Create browser context for all tests"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=TestConfig.BROWSER_HEADLESS,
            slow_mo=TestConfig.BROWSER_SLOWMO
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            ignore_https_errors=True
        )
        
        # Set default timeout
        context.set_default_timeout(TestConfig.DEFAULT_TIMEOUT)
        
        yield context
        
        context.close()
        browser.close()

@pytest.fixture
def page(browser_context):
    """Create a new page for each test"""
    page = browser_context.new_page()
    yield page
    page.close()

@pytest.fixture(autouse=True)
def screenshot_on_failure(request, page):
    """Take screenshot on test failure"""
    yield
    
    if request.node.rep_call.failed and TestConfig.SCREENSHOT_ON_FAILURE:
        # Create screenshots directory if it doesn't exist
        os.makedirs(TestConfig.SCREENSHOT_DIR, exist_ok=True)
        
        # Generate screenshot filename
        test_name = request.node.name
        screenshot_path = f"{TestConfig.SCREENSHOT_DIR}/{test_name}_failure.png"
        
        # Take screenshot
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for screenshot fixture"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)