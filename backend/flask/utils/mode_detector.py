import requests
import time

def detect_mode(timeout=1.5, retries=2):
    test_urls = [
        'https://www.google.com',
        'https://clients3.google.com/generate_204'
    ]
    
    for _ in range(retries):
        for url in test_urls:
            try:
                requests.head(url, timeout=timeout)
                return "online"
            except:
                continue
        time.sleep(0.5)
        
    return "offline"