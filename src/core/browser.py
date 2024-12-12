from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import random
import logging
from .fingerprint import generate_fingerprint, inject_fingerprint
from .human_behavior import add_human_behaviors

class BrowserManager:
    def __init__(self):
        self.driver = None
        
    def setup_chrome_options(self):
        """Configure Chrome options with enhanced privacy and anti-detection"""
        chrome_options = Options()
        
        # Privacy and security settings
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-automation')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Random viewport size
        viewport_sizes = [(1920, 1080), (1366, 768), (1536, 864), (1440, 900),
                         (1280, 720), (1600, 900), (1920, 1200), (2560, 1440)]
        viewport = random.choice(viewport_sizes)
        chrome_options.add_argument(f'--window-size={viewport[0]},{viewport[1]}')
        
        # Random user agent
        ua = UserAgent()
        chrome_options.add_argument(f'--user-agent={ua.random}')
        
        # Additional privacy settings
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        return chrome_options
        
    def create_driver(self):
        """Create and configure WebDriver with anti-detection measures"""
        try:
            options = self.setup_chrome_options()
            self.driver = webdriver.Chrome(options=options)
            
            # Generate and inject fingerprint
            fingerprint = generate_fingerprint()
            inject_fingerprint(self.driver, fingerprint)
            
            # Add human-like behaviors
            add_human_behaviors(self.driver)
            
            # Hide automation
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Override permissions query
                    const originalQuery = navigator.permissions.query;
                    navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                        Promise.resolve({state: Notification.permission}) :
                        originalQuery(parameters)
                    );
                """
            })
            
            return self.driver
            
        except Exception as e:
            logging.error(f"Failed to create browser: {str(e)}")
            if self.driver:
                self.driver.quit()
            raise
            
    def cleanup(self):
        """Clean up browser resources"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logging.error(f"Error cleaning up browser: {str(e)}")
            finally:
                self.driver = None