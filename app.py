from fastapi import FastAPI, Query
from scraper import run_scraper, run_scraper_with_groq
import os

app = FastAPI(
    title="College Semantic Intelligence API",
    description="AI powered college information extractor with Groq enhancement",
    version="2.0"
)

# Groq API Key (set environment variable GROQ_API_KEY)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

@app.get("/")
def home():
    return {
        "status": "API running successfully 🚀",
        "version": "2.0",
        "endpoints": [
            "/scrape - Basic scraping",
            "/scrape-enhanced - Scraping with Groq AI enhancement",
            "/docs - API documentation"
        ]
    }

@app.get("/scrape")
def scrape(
    url: str = Query(..., description="College website URL"),
    pages: int = Query(30, description="Number of pages to crawl")
):
    data = run_scraper(url, pages)
    return {
        "college_url": url,
        "status": "success",
        "fields": data
    }

@app.get("/scrape-enhanced")
def scrape_enhanced(
    url: str = Query(..., description="College website URL"),
    pages: int = Query(30, description="Number of pages to crawl")
):
    """Scrape website and optimize data quality with Groq AI
    
    Returns:
    - cleaned_content: High-quality optimized text
    - key_points: Extracted main facts (3-5 points)
    - quality_score: 1-10 rating of data quality
    - original_sentence_count: How many raw sentences were processed
    """
    data = run_scraper_with_groq(url, pages, GROQ_API_KEY)
    return {
        "college_url": url,
        "status": "success",
        "ai_optimized": True,
        "optimization": "Data quality enhanced with Groq",
        "fields": data
    }
