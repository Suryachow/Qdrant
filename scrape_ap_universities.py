"""
Script to scrape multiple AP (Andhra Pradesh) Universities
and generate JSON files similar to Vignan.json format
"""

import os
import sys
from scraper import run_scraper_with_groq, save_to_json
from datetime import datetime

# List of Universities with their official websites
# Including AP Universities + SRM, VIT as requested
AP_UNIVERSITIES = {
    # Top Deemed Universities (Requested)
    "SRM University": "https://www.srmist.edu.in/",
    "VIT University": "https://vit.ac.in/",
    "Vignan University": "https://vignan.ac.in/",
    
    # Other Deemed Universities in AP
    "GITAM University": "https://www.gitam.edu/",
    "KL University": "https://www.kluniversity.in/",
    
    # State Universities
    "Andhra University": "https://www.andhrauniversity.edu.in/",
    "Acharya Nagarjuna University": "https://www.nagarjunauniversity.ac.in/",
    "JNTU Anantapur": "https://www.jntua.ac.in/",
    "JNTU Kakinada": "https://www.jntuk.edu.in/",
    "Sri Venkateswara University": "https://www.svuniversity.edu.in/",
    "Adikavi Nannaya University": "https://www.aknu.edu.in/",
    "Krishna University": "https://www.krishnauniversity.ac.in/",
    "Rayalaseema University": "https://www.ruk.ac.in/",
    "Vikrama Simhapuri University": "https://www.simhapuriuniv.ac.in/",
    
    # Central Universities
    "Central University of Andhra Pradesh": "https://www.cuap.ac.in/",
}

def scrape_university(name, url, max_pages=50, groq_api_key=None):
    """
    Scrape a single university and save to JSON
    
    Args:
        name: University name
        url: University website URL
        max_pages: Maximum pages to crawl
        groq_api_key: Optional Groq API key for enhancement
    """
    print(f"\n{'='*80}")
    print(f"🎓 Scraping: {name}")
    print(f"🌐 URL: {url}")
    print(f"{'='*80}\n")
    
    try:
        # Run the scraper
        if groq_api_key:
            data = run_scraper_with_groq(url=url, pages=max_pages, groq_api_key=groq_api_key)
        else:
            from scraper import run_scraper
            data = run_scraper(url=url, pages=max_pages)
        
        if data:
            # Save to JSON
            filename = save_to_json(data, url)
            print(f"✅ Successfully scraped {name}")
            print(f"📄 Saved to: {filename}")
            return filename
        else:
            print(f"❌ No data extracted for {name}")
            return None
            
    except Exception as e:
        print(f"❌ Error scraping {name}: {str(e)}")
        return None

def scrape_all_universities(max_pages=50, groq_api_key=None, universities=None):
    """
    Scrape all AP universities
    
    Args:
        max_pages: Maximum pages to crawl per university
        groq_api_key: Optional Groq API key
        universities: Optional dict of specific universities to scrape
    """
    if universities is None:
        universities = AP_UNIVERSITIES
    
    print(f"\n🚀 Starting AP Universities Scraping")
    print(f"📊 Total universities to scrape: {len(universities)}")
    print(f"📄 Max pages per university: {max_pages}")
    print(f"🤖 Groq Enhancement: {'Enabled' if groq_api_key else 'Disabled'}")
    print(f"\n{'='*80}\n")
    
    results = {}
    successful = 0
    failed = 0
    
    for name, url in universities.items():
        filename = scrape_university(name, url, max_pages, groq_api_key)
        
        if filename:
            results[name] = {
                "status": "success",
                "filename": filename,
                "url": url
            }
            successful += 1
        else:
            results[name] = {
                "status": "failed",
                "url": url
            }
            failed += 1
        
        # Small delay between scrapes to be respectful
        import time
        time.sleep(2)
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"📊 SCRAPING SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successful: {successful}/{len(universities)}")
    print(f"❌ Failed: {failed}/{len(universities)}")
    print(f"\n📁 Generated Files:")
    
    for name, result in results.items():
        if result["status"] == "success":
            print(f"  ✓ {name}: {result['filename']}")
        else:
            print(f"  ✗ {name}: Failed")
    
    # Save summary report
    summary_file = f"scraping_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"AP Universities Scraping Summary\n")
        f.write(f"{'='*80}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Universities: {len(universities)}\n")
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {failed}\n\n")
        
        for name, result in results.items():
            f.write(f"\n{name}:\n")
            f.write(f"  URL: {result['url']}\n")
            f.write(f"  Status: {result['status']}\n")
            if result['status'] == 'success':
                f.write(f"  File: {result['filename']}\n")
    
    print(f"\n📄 Summary saved to: {summary_file}")
    print(f"\n{'='*80}\n")
    
    return results

if __name__ == "__main__":
    # You can customize these settings
    MAX_PAGES = 50  # Adjust based on how deep you want to crawl
    
    # Optional: Set your Groq API key for AI enhancement
    # GROQ_API_KEY = "your_groq_api_key_here"
    GROQ_API_KEY = None  # Set to None to scrape without AI enhancement
    
    # Option 1: Scrape all universities
    scrape_all_universities(max_pages=MAX_PAGES, groq_api_key=GROQ_API_KEY)
    
    # Option 2: Scrape specific universities only
    # specific_universities = {
    #     "GITAM University": "https://www.gitam.edu/",
    #     "KL University": "https://www.kluniversity.in/",
    # }
    # scrape_all_universities(max_pages=MAX_PAGES, groq_api_key=GROQ_API_KEY, universities=specific_universities)
