import requests
from bs4 import BeautifulSoup
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# Try different URLs
urls_to_try = [
    "https://www.srmist.edu.in/",
    "https://www.srmist.edu.in/about/",
    "https://www.srmist.edu.in/admissions/",
    "https://www.srmist.edu.in/program/",
]

session = requests.Session()
session.headers.update(headers)

for url in urls_to_try:
    try:
        print(f"\nTrying: {url}")
        time.sleep(1)
        r = session.get(url, timeout=10, allow_redirects=True)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.title.string if soup.title else "No title"
            print(f"Title: {title}")
            
            # Get text length
            for tag in soup(['script', 'style']):
                tag.decompose()
            text = soup.get_text()
            print(f"Content length: {len(text)} chars")
            print(f"Preview: {text[:200]}")
        else:
            print(f"Failed with status {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")
