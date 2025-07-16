from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test_homepage_loads():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get("http://localhost:5000")
    assert "Weekend" in driver.title
    driver.quit()
