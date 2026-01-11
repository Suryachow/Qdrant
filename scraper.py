# scraper.py
import json
import os
import re
import time
import requests
# import numpy as np
# import faiss
from groq import Groq

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from html import unescape
# from sentence_transformers import SentenceTransformer

# ================= CONFIG =================
BASE_URL = "https://vignan.ac.in/newvignan/"
MAX_PAGES = 50
MIN_SENTENCE_LEN = 30
MAX_CONTENT_PER_FIELD = 3000
SIMILARITY_THRESHOLD = 0.88

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0"
}

FIELDS = {
    "University Overview": ["about", "overview", "history", "vision", "mission", "founded", "established", "since", "accreditation", "naac", "nirf", "ranking", "institute", "university", "college"],
    "Courses Offered": ["b.tech", "m.tech", "mba", "bba", "program", "department", "branch", "specialization", "undergraduate", "postgraduate", "diploma", "course", "engineering", "degree"],
    "Admissions": ["admission", "apply", "entrance", "application", "selection", "counseling", "eligibility", "cutoff", "jee", "gate"],
    "Eligibility": ["eligibility", "qualification", "required", "minimum", "marks", "entrance exam", "cutoff score"],
    "Fees": ["fee structure", "tuition", "fees", "annual", "semester", "cost", "payment", "refund"],
    "Scholarships": ["scholarship", "financial aid", "assistance", "fee waiver", "merit", "grant"],
    "Placements": ["placement", "package", "salary", "company", "recruit", "career", "opportunity", "intern"],
    "Faculty": ["faculty", "professor", "instructor", "teacher", "phd", "expert", "experienced", "qualified"],
    "Facilities": ["hostel", "library", "laboratory", "lab", "sports", "cafeteria", "medical", "transport", "infrastructure", "amenities"],
    "Campus Life": ["club", "event", "activity", "fest", "cultural", "sports", "student life", "community"],
    "Contact": ["contact", "phone", "email", "address", "location", "reach us"],
    "Research": ["research", "paper", "publication", "project", "innovation", "development"],
}

# print("🔧 Loading AI Model...")
# embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
session = requests.Session()
session.headers.update(HEADERS)

# =============== UTILS ====================
def clean_text(text):
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_sentences(text):
    """Split text into quality sentences with balanced filtering"""
    # Split by sentence markers
    sentences = re.split(r'(?<=[.!?])\s+', text)
    clean_sentences = []
    
    for s in sentences:
        s = clean_text(s)
        
        # Skip if too short
        if len(s) < MIN_SENTENCE_LEN or len(s.split()) < 5:
            continue
        
        s_lower = s.lower()
        
        # Skip ONLY pure noise patterns (not content)
        if re.match(r'^[A-Z0-9]{6,}[_/]?\d{4}', s):  # Tax IDs
            continue
        if 'posted on:' in s_lower and len(s) < 50:  # Short date notifications
            continue
        if re.match(r'^(view|click|download|select|apply|know more)', s_lower):
            continue
        
        # Skip ONLY if MOSTLY numbers (>50% digits = code)
        digit_ratio = sum(c.isdigit() for c in s) / len(s)
        if digit_ratio > 0.5:
            continue
        
        # Must end with proper punctuation OR be meaningful
        if s[-1] in '.!?,' or len(s) > 80:
            clean_sentences.append(s)
    
    return clean_sentences

# =============== CRAWLER ==================
def crawl_site(url, max_pages):
    visited, queue = set(), [url]
    pages = []

    while queue and len(visited) < max_pages:
        current = queue.pop(0)
        if current in visited:
            continue

        try:
            print(f"📄 Crawling page {len(visited)+1}/{max_pages}: {current[:60]}...")
            # Add more realistic browser behavior
            res = session.get(
                current, 
                timeout=15,
                allow_redirects=True,
                verify=True
            )
            
            # Check if we got blocked
            if res.status_code == 403:
                print(f"⚠️ Access denied (403). Website may be blocking scrapers.")
                # Try alternate approach - some sites accept different patterns
                time.sleep(2)
                continue
                
            if res.status_code != 200:
                print(f"⚠️ Status {res.status_code}")
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")

            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()

            pages.append(soup)
            visited.add(current)

            for a in soup.find_all("a", href=True):
                link = urljoin(current, a["href"])
                if urlparse(link).netloc == urlparse(url).netloc:
                    if link not in visited:
                        queue.append(link)

            time.sleep(0.1)  # Reduced delay for faster crawling
        except Exception as e:
            print(f"⚠️ Error crawling {current[:60]}: {str(e)[:50]}")
            pass

    print(f"✅ Finished crawling {len(visited)} pages")
    return pages

# =============== EXTRACTION =================
def extract_data(pages):
    print(f"🔍 Extracting data from {len(pages)} pages...")
    content = defaultdict(list)

    for soup in pages:
        text = clean_text(soup.get_text())
        sentences = split_sentences(text)
        
        print(f"  📄 Processing page with {len(sentences)} sentences...")

        for sent in sentences:
            sent_lower = sent.lower()
            
            for field, keys in FIELDS.items():
                # Check if ANY keyword matches (more lenient)
                if any(k in sent_lower for k in keys):
                    content[field].append(sent)
                    break  # Don't add same sentence to multiple fields

    # Deduplicate and limit per field
    final_content = {}
    for field, sents in content.items():
        # Remove exact duplicates
        unique_sents = list(set(sents))
        # Sort by length and take top 20
        sorted_sents = sorted(unique_sents, key=len, reverse=True)[:20]
        if sorted_sents:
            final_content[field] = sorted_sents
    
    total = sum(len(v) for v in final_content.values())
    print(f"✅ Extracted {total} unique sentences across {len(final_content)} fields")
    
    if total == 0:
        print("⚠️ WARNING: No data extracted! Returning all sentences anyway...")
        # Fallback: if nothing matched keywords, return some general content
        for soup in pages:
            text = clean_text(soup.get_text())
            sentences = split_sentences(text)
            if sentences:
                final_content["General Content"] = sentences[:30]
                break
    
    return final_content

# =============== MAIN FUNCTION =============
def run_scraper(url=BASE_URL, pages=MAX_PAGES):
    pages_data = crawl_site(url, pages)
    data = extract_data(pages_data)

    save_to_json(data, url)   # 👈 SAVE HERE with URL

    return data

# =============== SAVE TO JSON ===============
def save_to_json(data, url=None):
    from datetime import datetime
    
    # Generate unique filename from URL
    if url:
        domain = urlparse(url).netloc.replace('www.', '').replace('.', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{domain}_{timestamp}.json"
    else:
        filename = "college_data.json"
    
    # Structure the output nicely
    output = {
        "college_url": url,
        "scraped_at": datetime.now().isoformat(),
        "total_fields": len(data),
        "total_sentences": sum(len(v) for v in data.values()),
        "data": data
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Data saved to {os.path.abspath(filename)}")

# =============== GROQ AI ENHANCEMENT =========
def enhance_with_groq(data, api_key):
    """Use Groq LLM to optimize and clean scraped data for high quality"""
    try:
        client = Groq(api_key=api_key)
        optimized_data = {}
        
        print("\n🤖 Optimizing data quality with Groq AI...\n")
        
        # Field-specific prompts for better results
        field_prompts = {
            "University Overview": "Provide a professional overview of the university including its type, founding year, mission, and key achievements.",
            "Courses Offered": "List and describe the academic programs and courses offered with specializations.",
            "Admissions": "Explain the admission process, application requirements, and selection criteria.",
            "Eligibility": "Describe the eligibility criteria and requirements for different programs.",
            "Fees": "Provide information about fee structure, payment options, and any refund policies.",
            "Scholarships": "Detail the available scholarships, financial aid, and fee waiver programs.",
            "Placements": "Summarize placement statistics, top recruiting companies, and average/highest packages.",
            "Faculty": "Describe the faculty qualifications, expertise, and student-faculty ratio.",
            "Facilities": "List and describe campus facilities including libraries, hostels, labs, and amenities.",
            "Campus Life": "Explain student life, clubs, events, cultural activities, and sports.",
            "Contact": "Provide contact information and ways to reach the university."
        }
        
        for field, sentences in data.items():
            if not sentences or len(sentences) == 0:
                optimized_data[field] = {
                    "cleaned_content": "No information available",
                    "key_points": [],
                    "quality_score": 0,
                    "data_status": "no_data"
                }
                continue
            
            # Create better context from sentences
            content = "\n".join(sentences)
            field_prompt = field_prompts.get(field, f"Optimize and summarize information about {field}")
            
            # Call Groq with optimized prompt
            try:
                completion = client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    max_tokens=800,
                    temperature=0.2,  # Even lower for more focused output
                    messages=[
                        {
                            "role": "user",
                            "content": f"""You are a professional data curator for educational institutions.

Task: Extract ONLY relevant, high-quality information about '{field}' from the following text. Remove ALL noise, duplicates, and irrelevant content.

Raw Information:
{content}

STRICT RULES:
1. EXCLUDE: tax IDs, document codes, file names, URLs, links, "View More", "Posted On", dates, notification text
2. EXTRACT: Only factual, useful information about {field}
3. REMOVE: All repetition and duplicate content
4. FORMAT: Create a clear, professional summary

Provide ONLY valid JSON (no other text):
{{
    "cleaned_summary": "A professional, high-quality summary (100-250 words). If no useful info found, write 'Information not available'",
    "key_points": ["point1", "point2", "point3"],
    "quality_score": 7,
    "data_completeness": "good"
}}

If the text contains only noise/codes/irrelevant data, set quality_score to 1 and summary to 'Information not available'."""
                        }
                    ]
                )
                
                response_text = completion.choices[0].message.content.strip()
                
                # Parse JSON response
                try:
                    import json as json_module
                    # Find JSON in response
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = response_text[start:end]
                        result = json_module.loads(json_str)
                    else:
                        raise ValueError("No JSON found")
                        
                    # Validate result
                    summary = result.get("cleaned_summary", "").strip()
                    if not summary or "not available" in summary.lower():
                        quality = 0
                    else:
                        quality = min(10, max(0, result.get("quality_score", 5)))
                    
                    optimized_data[field] = {
                        "cleaned_content": summary,
                        "key_points": result.get("key_points", [])[:4],
                        "quality_score": quality,
                        "data_status": "optimized" if quality >= 5 else "insufficient"
                    }
                    print(f"  ✅ {field:20} → Quality: {quality}/10 | Status: {'Good' if quality >= 5 else 'Insufficient'}")
                    
                except Exception as e:
                    # Fallback if JSON parsing fails
                    optimized_data[field] = {
                        "cleaned_content": "Unable to process data",
                        "key_points": [],
                        "quality_score": 0,
                        "data_status": "error"
                    }
                    print(f"  ⚠️ {field:20} → Parse error")
                
            except Exception as e:
                print(f"  ❌ {field:20} → API Error: {str(e)[:40]}")
                optimized_data[field] = {
                    "cleaned_content": "Processing failed",
                    "key_points": [],
                    "quality_score": 0,
                    "data_status": "failed"
                }
        
        print("\n✅ Groq optimization complete!\n")
        return optimized_data
        
    except Exception as e:
        print(f"❌ Critical Groq error: {str(e)}")
        return data

# =============== GROQ CATEGORY BUILDER ========
def groq_categorize_from_general(general_sentences, api_key):
    """Use Groq to split general content into our predefined fields.
    Returns a dict mapping fields to arrays of cleaned sentences.
    """
    try:
        client = Groq(api_key=api_key)

        # Build a compact context to keep token usage reasonable
        context = "\n".join(general_sentences[:100])  # cap to first 100 sentences

        fields_list = list(FIELDS.keys())
        fields_json = json.dumps(fields_list)

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            temperature=0.2,
            max_tokens=1200,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "You are organizing college website content into structured fields. "
                        "Given the raw text below, group the information into the provided fields. "
                        "Only include relevant, meaningful sentences per field. Remove duplicates, codes, IDs, and navigation text. "
                        "Keep sentences concise but complete. If a field has no data, use an empty list.\n\n"
                        f"Fields: {fields_json}\n\n"
                        f"Raw text (sentences):\n{context}\n\n"
                        "Return ONLY valid JSON mapping each field to an array of sentences."
                    )
                }
            ]
        )

        response_text = completion.choices[0].message.content.strip()

        # Extract JSON payload
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = response_text[start:end]
            result = json.loads(json_str)
            # Ensure all expected fields exist
            categorized = {key: (result.get(key) or []) for key in fields_list}
            print("✅ Groq categorized general content into fields")
            return categorized
        else:
            print("⚠️ Groq categorization: no JSON found")
            return {}

    except Exception as e:
        print(f"❌ Groq categorization error: {str(e)[:80]}")
        return {}

def run_scraper_with_groq(url=BASE_URL, pages=MAX_PAGES, groq_api_key=None):
    """Run scraper and optimize with Groq for best quality"""
    pages_data = crawl_site(url, pages)
    data = extract_data(pages_data)
    
    # Optimize with Groq if API key provided
    if groq_api_key:
        # If extraction returned empty or very sparse data, build categories from general content first
        total_items = sum(len(v) for v in data.values())
        if total_items == 0:
            # Compose general sentences from first few pages
            combined_sentences = []
            for soup in pages_data[:5]:
                text = clean_text(soup.get_text())
                combined_sentences.extend(split_sentences(text))
            if combined_sentences:
                categorized = groq_categorize_from_general(combined_sentences, groq_api_key)
                if categorized:
                    data = categorized
        # Then optimize field content for quality summarization
        data = enhance_with_groq(data, groq_api_key)
    
    save_to_json(data, url)
    return data
