import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.srmist.edu.in/'
headers = {'User-Agent': 'Mozilla/5.0'}

r = requests.get(url, timeout=10, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')

# Remove unwanted tags
for tag in soup(['script', 'style', 'nav', 'footer']):
    tag.decompose()

text = soup.get_text()
text = re.sub(r'\s+', ' ', text).strip()

print(f"Total text length: {len(text)} characters")
print(f"\nFirst 2000 characters:")
print(text[:2000])
print("\n" + "="*80)

# Try splitting sentences
sentences = re.split(r'(?<=[.!?])\s+', text)
print(f"\nTotal split sentences: {len(sentences)}")

# Show first 10 sentences
print("\nFirst 10 sentences:")
for i, s in enumerate(sentences[:10], 1):
    print(f"{i}. [{len(s)} chars] {s[:200]}")

# Check sentence lengths
MIN_SENTENCE_LEN = 20
qualifying = [s for s in sentences if len(s) >= MIN_SENTENCE_LEN and len(s.split()) >= 5]
print(f"\nSentences meeting MIN criteria (>={MIN_SENTENCE_LEN} chars, >=5 words): {len(qualifying)}")

# Show some qualifying sentences
print("\nFirst 5 qualifying sentences:")
for i, s in enumerate(qualifying[:5], 1):
    print(f"{i}. [{len(s)} chars] {s[:300]}")
