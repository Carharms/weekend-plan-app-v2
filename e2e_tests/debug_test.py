"""
Debug version of E2E test with visual mode and detailed logging
Run this for debugging issues
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
from config import TestConfig

def debug_user_journey():
    """Debug version with visual browser and step-by-step execution"""
    with sync_playwright() as p:

        # Launch browser in non-headless mode for debugging
        browser = p.chromium.launch(
            headless=False,
            slow_mo=1000,
            devtools=True
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        
        page = context.new_page()
        
        try:
            print("Debug step 1: going to dashboard")
            page.goto(TestConfig.BASE_URL)
            
            print("Debug step 2: selecting Add Task")
            page.locator("text=Add Task").first.click()
            
            print("Debug step 3: filling in form")
            page.locator("input[name='event']").fill("DEBUG TEST")
            page.locator("select[name='day']").select_option("Saturday")
            page.locator("input[name='start_time']").fill("15:30")
            
            print("Debug step 4: submitting form")
            page.locator("button[type='submit']").click()
            
            print("Debug step 5: verifying task")
            page.wait_for_selector("text=DEBUG TEST")
            
            print("All Debug Steps Completed!")
            
        except Exception as e:
            print(f"Debug test failed: {e}")
            
        finally:
            input("Press Enter to exit browser")
            browser.close()

if __name__ == "__main__":
    debug_user_journey()