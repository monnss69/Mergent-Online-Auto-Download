import time
import random
from collections import deque
from threading import Lock
import logging

class RateLimiter:
    def __init__(self, max_requests=400, time_window=3600):
        """
        Initialize rate limiter with intelligent request distribution
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = Lock()
        
    def _clean_old_requests(self):
        """Remove requests outside the time window"""
        current_time = time.time()
        while self.requests and current_time - self.requests[0] >= self.time_window:
            self.requests.popleft()
            
    def add_natural_delay(self):
        """Add naturally distributed delays between requests"""
        # Use Gaussian distribution for more natural timing
        mean_delay = 2.0
        sigma = 0.5
        delay = max(0.5, random.gauss(mean_delay, sigma))
        
        # Add occasional longer pauses
        if random.random() < 0.1:  # 10% chance of longer pause
            delay += random.uniform(2, 5)
            
        time.sleep(delay)
        
    def can_make_request(self):
        """Check if a request can be made within rate limits"""
        with self.lock:
            self._clean_old_requests()
            if len(self.requests) < self.max_requests:
                current_time = time.time()
                self.requests.append(current_time)
                return True
            return False
            
    def wait_if_needed(self):
        """Wait until a request can be made"""
        while not self.can_make_request():
            wait_time = random.uniform(5, 15)  # Random wait between 5-15 seconds
            logging.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
        self.add_natural_delay()

class RequestManager:
    def __init__(self, rate_limiter):
        self.rate_limiter = rate_limiter
        self.session_start_time = time.time()
        
    def pre_request(self):
        """Prepare for making a request"""
        self.rate_limiter.wait_if_needed()
        
    def post_request(self):
        """Handle post-request tasks"""
        # Add variation to avoid perfect timing patterns
        time.sleep(random.uniform(0.1, 0.3))