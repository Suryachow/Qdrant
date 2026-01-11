
import requests
import json
import re
import time
import os

API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

NIRF_COLLEGES = [
    "Indian Institute of Technology Madras (IIT Madras)",
    "Indian Institute of Technology Delhi (IIT Delhi)",
    "Indian Institute of Technology Bombay (IIT Bombay)",
    "Indian Institute of Technology Kanpur (IIT Kanpur)",
    "Indian Institute of Technology Kharagpur (IIT Kharagpur)",
    "Indian Institute of Technology Roorkee (IIT Roorkee)",
    "Indian Institute of Technology Guwahati (IIT Guwahati)",
    "Indian Institute of Technology Hyderabad (IIT Hyderabad)",
    "National Institute of Technology Tiruchirappalli (NIT Trichy)",
    "Indian Institute of Technology Varanasi (IIT BHU)"
]

def get_detailed_profile(college_name):
    url = "https://api.perplexity.ai/chat/completions"
    
    prompt = f"""
    Generate a VERY DETAILED JSON profile for {college_name}.
    The user specifically requested "around 10 lines for each category".
    Ensure the "description" fields are long and detailed.
    
    Structure:
    {{
      "university_name": "{college_name}",
      "overview": {{
         "established_year": "...",
         "location": "...",
         "type": "Public/Government",
         "campus_size": "...",
         "description": "PROVIDE A LONG DETAILED DESCRIPTION (approx 10 sentences) covering history, reputation, recent achievements, campus culture, and significance."
      }},
      "rankings": [
         "NIRF 2024 Engineering: #Rank",
         "QS World Ranking: #Rank",
         // Provide at least 5-10 detailed ranking achievements
      ],
      "courses_and_fees": [
         // Provide details for at least 8-10 major programs (B.Tech, M.Tech, PhD, MSc, MBA, etc.)
         {{
            "course_name": "B.Tech Computer Science",
            "duration": "4 Years",
            "total_tuition_fee": "Detailed fee structure",
            "eligibility": "Detailed eligibility criteria including exams and cutoffs"
         }}
      ],
      "placements": {{
         "description": "PROVIDE A LONG DETAILED SUMMARY (approx 10 sentences) of the placement scenario, trends, average packages over years, intern opportunities, and highest offers.",
         "highest_package": "...",
         "average_package": "...",
         "major_recruiters": ["List at least 15-20 top companies"]
      }},
      "facilities": [
         // List at least 10-15 detailed facilities with brief descriptions for each
         "Central Library with X volumes",
         "Hostels with capacity Y",
         "Advanced Research Labs for Z"
      ],
      "contact_info": {{
         "website": "...",
         "address": "..."
      }}
    }}
    
    RETURN ONLY RAW JSON. NO MARKDOWN. NO PREAMBLE.
    """

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a detailed data assistant that outputs strict JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"🤖 Fetching detailed data for: {college_name}...")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        # Robust Regex Extraction
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            json_str = match.group(0)
            # Cleanup common issues
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            return json.loads(json_str)
        else:
            print(f"❌ JSON not found in response for {college_name}")
            return None
            
    except Exception as e:
        print(f"❌ Error processing {college_name}: {e}")
        return None

def main():
    print("🚀 Starting Top 10 NIRF Data Extraction...\n")
    
    results = []
    
    for college in NIRF_COLLEGES:
        data = get_detailed_profile(college)
        if data:
            results.append(data)
            # Save individual for safety
            safe_name = college.split('(')[0].strip().replace(' ', '_').lower()
            with open(f"{safe_name}_nirf_data.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"✅ Saved {safe_name}_nirf_data.json\n")
        
        time.sleep(2) # rate limit
        
    # Combined file
    with open("top_10_nirf_colleges_detailed.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    print("✨ All done! Saved to 'top_10_nirf_colleges_detailed.json'")

if __name__ == "__main__":
    main()
