"""
PROG8850 Assignment 3 - Selenium Test Script
Simple automated testing for Flask user registration application
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import mysql.connector
import time
import os

class FlaskSeleniumTest:
    def __init__(self):
        self.driver = None
        self.app_url = os.getenv('APP_URL', 'http://localhost:5000')
        self.db_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'user': os.getenv('MYSQL_USER', 'loginappuser'),
            'password': os.getenv('MYSQL_PASSWORD', 'LoginAppDbPwd@2025'),
            'database': os.getenv('MYSQL_DB', 'loginapp'),
            'port': int(os.getenv('MYSQL_PORT', '3306'))
        }

    def setup_driver(self):
        """Setup Chrome WebDriver"""
        print("Setting up Chrome WebDriver...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        print("WebDriver setup complete")

    def test_registration_form(self):
        """Test the registration form submission"""
        print(f"Testing registration form at {self.app_url}")
        
        # Navigate to the application
        self.driver.get(self.app_url)
        
        # Generate test data
        timestamp = int(time.time())
        test_username = f"test_user_{timestamp}"
        test_password = "test_password_123"
        
        print(f"Testing with username: {test_username}")
        
        # Fill the form
        username_field = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="username-input"]')
        password_field = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="password-input"]')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="submit-button"]')
        
        username_field.send_keys(test_username)
        password_field.send_keys(test_password)
        
        # Submit form
        submit_button.click()
        
        # Wait for response
        time.sleep(3)
        
        # Check if successful
        current_url = self.driver.current_url
        print(f"Current URL after submission: {current_url}")
        
        # Verify in database
        self.verify_database(test_username)
        
        print("Registration form test completed")

    def verify_database(self, username):
        """Verify user was inserted into database"""
        print("Verifying database insertion...")
        
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user:
                print(f"✅ User found in database: {user}")
            else:
                print("❌ User not found in database")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Database verification error: {e}")

    def run_test(self):
        """Run the complete test"""
        try:
            self.setup_driver()
            self.test_registration_form()
            print("✅ Test completed successfully")
        except Exception as e:
            print(f"❌ Test failed: {e}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    test = FlaskSeleniumTest()
    test.run_test()
