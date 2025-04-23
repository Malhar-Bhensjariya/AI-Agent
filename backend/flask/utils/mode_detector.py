import requests
import time

def detect_mode(timeout=1.5, retries=3):
    """Improved connectivity detection with multiple checks"""
    test_urls = [
        'https://www.google.com',
        'https://api.ipify.org',
        'https://clients3.google.com/generate_204'
    ]
    
    success_threshold = 2  # Require multiple successful checks
    
    for _ in range(retries):
        successes = 0
        for url in test_urls:
            try:
                response = requests.head(url, timeout=timeout)
                if response.status_code < 500:
                    successes += 1
                if successes >= success_threshold:
                    return "online"
            except:
                continue
        time.sleep(0.5)
        
    return "offline"