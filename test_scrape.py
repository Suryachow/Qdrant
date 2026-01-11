import requests
from bs4 import BeautifulSoup

url = 'https://www.srmist.edu.in/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

try:
    print(f"Testing URL: {url}")
    r = requests.get(url, timeout=10, headers=headers)
    print(f"Status Code: {r.status_code}")
    print(f"Page Size: {len(r.text)} characters")
    
    soup = BeautifulSoup(r.text, 'html.parser')
    print(f"Title: {soup.title.string if soup.title else 'No title'}")
    
    # Get clean text
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()
    
    text = soup.get_text()
    print(f"\nText content length: {len(text)} chars")
    print(f"\nFirst 1000 characters of content:")
    print(text[:1000])
    
except Exception as e:
    print(f"Error: {e}")
