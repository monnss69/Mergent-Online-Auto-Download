from selenium.webdriver.common.action_chains import ActionChains
import random
import time
import math
import logging

class HumanBehavior:
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger("MergentScraper.HumanBehavior")

    @staticmethod
    def add_human_behaviors(driver):
        """Add all human-like behaviors to the browser"""
        behavior = HumanBehavior(driver)
        behavior._add_event_listeners()
        behavior._add_mouse_trails()
        behavior._add_timing_variations()
        behavior._add_scroll_variations()
        return behavior

    def _add_event_listeners(self):
        """Add random event listeners to simulate human presence"""
        js_code = """
        // Add random mouse movement tracking
        document.addEventListener('mousemove', function(e) {
            window.__lastMouseMove = {
                x: e.clientX,
                y: e.clientY,
                timestamp: Date.now()
            };
        });

        // Add random focus/blur handling
        document.addEventListener('focus', function() {
            window.__lastFocus = Date.now();
        });
        """
        self.driver.execute_script(js_code)

    def _add_mouse_trails(self):
        """Add subtle mouse movement trails"""
        js_code = """
        // Create subtle mouse trail effect
        let trail = [];
        document.addEventListener('mousemove', function(e) {
            trail.push({x: e.clientX, y: e.clientY, timestamp: Date.now()});
            if (trail.length > 5) trail.shift();
        });
        """
        self.driver.execute_script(js_code)

    def _add_timing_variations(self):
        """Add random timing variations to actions"""
        js_code = """
        // Add random delays to element interactions
        const originalClick = HTMLElement.prototype.click;
        HTMLElement.prototype.click = function() {
            const delay = Math.random() * 100;
            setTimeout(() => originalClick.call(this), delay);
        };
        """
        self.driver.execute_script(js_code)

    def _add_scroll_variations(self):
        """Add natural scroll behavior variations"""
        js_code = """
        // Add smooth scroll behavior
        document.addEventListener('scroll', function() {
            window.__lastScroll = Date.now();
        });
        """
        self.driver.execute_script(js_code)

    @staticmethod
    def natural_scroll(driver, scroll_amount):
        """Perform natural scrolling with variable speed"""
        current = 0
        while current < scroll_amount:
            # Variable scroll step
            step = random.randint(100, 300)
            # Randomize scroll speed
            duration = random.uniform(0.1, 0.3)
            
            driver.execute_script(f"""
                window.scrollBy({{
                    top: {step},
                    behavior: 'smooth'
                }});
            """)
            current += step
            time.sleep(duration)
            
    @staticmethod
    def natural_mouse_movement(driver, element=None):
        """Generate human-like mouse movement"""
        action = ActionChains(driver)
        
        if element:
            # Get element location
            location = element.location
            size = element.size
            target_x = location['x'] + size['width'] / 2
            target_y = location['y'] + size['height'] / 2
        else:
            # Random point on screen
            viewport_width = driver.execute_script("return window.innerWidth;")
            viewport_height = driver.execute_script("return window.innerHeight;")
            target_x = random.randint(0, viewport_width)
            target_y = random.randint(0, viewport_height)
            
        # Generate bezier curve control points
        control_points = [
            (random.randint(0, target_x), random.randint(0, target_y)),
            (random.randint(0, target_x), random.randint(0, target_y))
        ]
        
        # Move mouse along bezier curve
        steps = 25
        for i in range(steps + 1):
            t = i / steps
            # Calculate position using cubic bezier curve
            x = HumanBehavior._bezier(t, 0, control_points[0][0], 
                                    control_points[1][0], target_x)
            y = HumanBehavior._bezier(t, 0, control_points[0][1], 
                                    control_points[1][1], target_y)
            
            action.move_by_offset(x, y)
            # Add random pause
            action.pause(random.uniform(0.001, 0.003))
            
        action.perform()
        
    @staticmethod
    def _bezier(t, p0, p1, p2, p3):
        """Calculate point on cubic bezier curve"""
        return math.pow(1-t, 3) * p0 + \
               3 * math.pow(1-t, 2) * t * p1 + \
               3 * (1-t) * math.pow(t, 2) * p2 + \
               math.pow(t, 3) * p3
               
    @staticmethod
    def natural_typing(element, text):
        """Simulate natural typing rhythm"""
        for char in text:
            element.send_keys(char)
            # Variable typing speed
            delay = random.gauss(0.1, 0.02)
            time.sleep(max(0.02, delay))
            
            # Occasional longer pause
            if random.random() < 0.1:
                time.sleep(random.uniform(0.1, 0.3))
                
    @staticmethod
    def natural_click(driver, element):
        """Perform a natural click with slight offset"""
        try:
            # Get element dimensions
            size = element.size
            
            # Calculate random offset within element
            offset_x = random.randint(5, max(6, size['width'] - 5))
            offset_y = random.randint(5, max(6, size['height'] - 5))
            
            # Move to element with natural motion
            HumanBehavior.natural_mouse_movement(driver, element)
            
            # Click with offset
            action = ActionChains(driver)
            action.move_to_element_with_offset(element, offset_x, offset_y)
            action.pause(random.uniform(0.1, 0.3))
            action.click()
            action.perform()
            
            # Random pause after click
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logging.warning(f"Failed to perform natural click: {str(e)}")
            # Fallback to regular click
            element.click()
            time.sleep(random.uniform(0.5, 1.5))