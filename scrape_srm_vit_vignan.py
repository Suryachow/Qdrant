"""
Quick script to scrape SRM, VIT, and Vignan universities
Generates JSON files in the Vignan.json format
"""

import os
import sys
from scraper import run_scraper_with_groq, save_to_json, run_scraper
from datetime import datetime

# Priority universities to scrape
PRIORITY_UNIVERSITIES = {
    "SRM University": "https://www.srmist.edu.in/",
    "VIT University": "https://vit.ac.in/",
    "Vignan University": "https://vignan.ac.in/",
}

def scrape_priority_universities(max_pages=50, groq_api_key=None):
    """
    Scrape SRM, VIT, and Vignan universities
    
    Args:
        max_pages: Maximum pages to crawl per university (default: 50)
        groq_api_key: Optional Groq API key for AI enhancement
    """
    print(f"\n{'='*80}")
    print(f"🎓 SCRAPING PRIORITY UNIVERSITIES: SRM, VIT, VIGNAN")
    print(f"{'='*80}\n")
    print(f"📊 Total universities: {len(PRIORITY_UNIVERSITIES)}")
    print(f"📄 Max pages per university: {max_pages}")
    print(f"🤖 Groq Enhancement: {'Enabled ✓' if groq_api_key else 'Disabled ✗'}")
    print(f"\n{'='*80}\n")
    
    results = []
    
    for idx, (name, url) in enumerate(PRIORITY_UNIVERSITIES.items(), 1):
        print(f"\n[{idx}/{len(PRIORITY_UNIVERSITIES)}] 🎓 Scraping: {name}")
        print(f"🌐 URL: {url}")
        print(f"{'-'*80}")
        
        try:
            # Run the scraper
            if groq_api_key:
                print("🤖 Using Groq AI enhancement...")
                data = run_scraper_with_groq(url=url, pages=max_pages, groq_api_key=groq_api_key)
            else:
                print("📝 Using basic scraper...")
                data = run_scraper(url=url, pages=max_pages)
            
            if data:
                # Save to JSON
                filename = save_to_json(data, url)
                print(f"✅ SUCCESS! Saved to: {filename}")
                
                # Print quick stats
                total_sentences = data.get('total_sentences', 0)
                total_fields = data.get('total_fields', 0)
                print(f"📊 Extracted {total_sentences} sentences across {total_fields} fields")
                
                results.append({
                    "name": name,
                    "url": url,
                    "status": "success",
                    "filename": filename,
                    "sentences": total_sentences,
                    "fields": total_fields
                })
            else:
                print(f"❌ FAILED: No data extracted for {name}")
                results.append({
                    "name": name,
                    "url": url,
                    "status": "failed",
                    "error": "No data extracted"
                })
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                "name": name,
                "url": url,
                "status": "error",
                "error": str(e)
            })
        
        # Delay between scrapes
        if idx < len(PRIORITY_UNIVERSITIES):
            print(f"\n⏳ Waiting 3 seconds before next scrape...\n")
            import time
            time.sleep(3)
    
    # Print final summary
    print(f"\n{'='*80}")
    print(f"📊 FINAL SUMMARY")
    print(f"{'='*80}\n")
    
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - successful
    
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}\n")
    
    print("📁 Generated Files:")
    for r in results:
        if r['status'] == 'success':
            print(f"  ✓ {r['name']}")
            print(f"    File: {r['filename']}")
            print(f"    Data: {r['sentences']} sentences, {r['fields']} fields\n")
        else:
            print(f"  ✗ {r['name']} - {r.get('error', 'Unknown error')}\n")
    
    # Save summary
    summary_file = f"priority_scraping_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("SRM, VIT, VIGNAN - Scraping Summary\n")
        f.write("="*80 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Successful: {successful}/{len(results)}\n")
        f.write(f"Failed: {failed}/{len(results)}\n\n")
        
        for r in results:
            f.write(f"\n{r['name']}:\n")
            f.write(f"  URL: {r['url']}\n")
            f.write(f"  Status: {r['status']}\n")
            if r['status'] == 'success':
                f.write(f"  File: {r['filename']}\n")
                f.write(f"  Sentences: {r['sentences']}\n")
                f.write(f"  Fields: {r['fields']}\n")
            else:
                f.write(f"  Error: {r.get('error', 'Unknown')}\n")
    
    print(f"📄 Summary saved to: {summary_file}")
    print(f"\n{'='*80}\n")
    
    return results

if __name__ == "__main__":
    print("\n🚀 Starting Priority Universities Scraper")
    print("🎯 Target: SRM, VIT, Vignan\n")
    
    # Configuration
    MAX_PAGES = 50  # Adjust if needed
    GROQ_API_KEY = None  # Set your Groq API key here if you have one
    
    # Run the scraper
    results = scrape_priority_universities(max_pages=MAX_PAGES, groq_api_key=GROQ_API_KEY)
    
    print("✨ Scraping complete! Check the generated JSON files.")
