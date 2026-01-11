from scraper import run_scraper_with_groq
import scraper
import os

# Override the BASE_URL
scraper.BASE_URL = "https://www.srmist.edu.in/"

# Patch the MIN_SENTENCE_LEN to be less strict
scraper.MIN_SENTENCE_LEN = 20

print("Starting scraper for SRM IST...")
result = run_scraper_with_groq(
    url="https://www.srmist.edu.in/",
    pages=30,
    groq_api_key=os.getenv("GROQ_API_KEY", "")
)

print("\n" + "="*60)
print("SCRAPING COMPLETE!")
print("="*60)
print(f"Total fields extracted: {len(result)}")
for field, content in result.items():
    if isinstance(content, dict):
        print(f"\n{field}:")
        print(f"  Quality Score: {content.get('quality_score', 'N/A')}")
        print(f"  Status: {content.get('data_status', 'N/A')}")
    else:
        print(f"\n{field}: {len(content)} items")
