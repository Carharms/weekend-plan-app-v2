""" Configuration for E2E tests """

import os

class TestConfig:
    # Application URL
    BASE_URL = os.getenv('TEST_BASE_URL', 'http://localhost:5000')
    
    # Test information
    TEST_EVENT = "Playwright testing event"
    TEST_DAY = "Monday"
    TEST_TIME = "20:00"
    TEST_DESCRIPTION = "End-to-end test using Playwright - Q7 "
    TEST_LINKS = "https://playwright.dev"
    
    # Browser settings
    BROWSER_HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
    BROWSER_SLOWMO = int(os.getenv('SLOWMO', '100'))  
    
    # Recorded in milliseconds = 30 / 10 seconds
    DEFAULT_TIMEOUT = 30000
    NAVIGATION_TIMEOUT = 10000 
    
    SCREENSHOT_ON_FAILURE = True
    SCREENSHOT_DIR = "e2e_tests/screenshots"