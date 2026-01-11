import json
import re
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse

# Headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

class SmartScraper:
    def __init__(self, base_url, max_pages=30):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited = set()
        self.data = {
            "university_info": {},
            "placements": [],
            "courses_and_fees": [],
            "admission_eligibility": [],
            "infrastructure": [],
            "contact_info": []
        }

    def clean_text(self, text):
        return re.sub(r'\s+', ' ', text).strip()

    def get_soup(self, url):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
        except Exception:
            pass
        return None

    def extract_money(self, text):
        # Extract patterns like ₹ 5 LPA, 40 Lakhs, 50,000
        patterns = [
            r'₹\s?[\d,]+(\.\d+)?\s?(Lakhs?|LPA|Crore|Cr)?',
            r'Rs\.?\s?[\d,]+(\.\d+)?\s?(Lakhs?|LPA)?',
            r'[\d,]+(\.\d+)?\s?LPA'
        ]
        matches = []
        for p in patterns:
            found = re.findall(p, text, re.IGNORECASE)
            matches.extend([f for f in found if f])
        return len(matches) > 0

    def parse_page(self, soup, url):
        text = soup.get_text(" ", strip=True)
        
        # 1. Basic Info (Establishment, Location)
        if "est" in text.lower() or "founded" in text.lower():
            est_match = re.search(r'(Est\.|Established|Founded)\s?in\s?(\d{4})', text)
            if est_match and "established_year" not in self.data["university_info"]:
                self.data["university_info"]["established_year"] = est_match.group(2)
        
        # 2. Placements (Look for LPA, Packages)
        # Scan specifically for placement related keywords
        if "placement" in url.lower() or "career" in url.lower() or "recruit" in text.lower():
            # Look for table rows first as they often contain stats
            rows = soup.find_all('tr')
            for row in rows:
                cols = [self.clean_text(c.get_text()) for c in row.find_all(['td', 'th'])]
                row_text = " ".join(cols)
                if "LPA" in row_text or "Package" in row_text:
                    self.data["placements"].append(row_text)
            
            # Look for high value text patterns
            sentences = text.split('.')
            for s in sentences:
                if "LPA" in s or "Highest Package" in s or "Average Package" in s:
                    cleaned = self.clean_text(s)
                    if len(cleaned) < 200: # specific info, not paragraph
                        self.data["placements"].append(cleaned)

    def crawl(self):
        print(f"🚀 Starting Smart Scrape for {self.base_url}")
        queue = [self.base_url]
        self.visited.add(self.base_url)
        count = 0

        while queue and count < self.max_pages:
            url = queue.pop(0)
            count += 1
            
            print(f"  📄 [{count}/{self.max_pages}] Analyzing: {url}")
            soup = self.get_soup(url)
            if not soup:
                continue

            self.parse_page(soup, url)

            # Find new links
            for a in soup.find_all('a', href=True):
                link = urljoin(self.base_url, a['href'])
                if link not in self.visited and self.base_url in link:
                    # Prioritize relevant pages
                    priority_words = ['admission', 'fee', 'course', 'placement', 'about', 'contact']
                    if any(w in link.lower() for w in priority_words):
                        queue.insert(0, link) # Visit meaningful pages first
                    else:
                        queue.append(link)
                    self.visited.add(link)

        
        # Post-Processing to deduplicate
        self.data["placements"] = list(set(self.data["placements"]))
        
        return self.data

def run_smart_scraper():
    universities = {
        "SRM_University": "https://www.srmist.edu.in/",
        "VIT_University": "https://vit.ac.in/",
        "Vignan_University": "https://vignan.ac.in/"
    }

    for name, url in universities.items():
        scraper = SmartScraper(url, max_pages=25)
        data = scraper.crawl()
        
        filename = f"{name}_smart_data.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"✅ Saved structured data to {filename}\n")

if __name__ == "__main__":
    run_smart_scraper()
