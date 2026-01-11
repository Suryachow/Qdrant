
import requests
import json
import time
import os

# Perplexity API Key from env
API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

# List of universities to profile
UNIVERSITIES = [
    "SRM Institute of Science and Technology (SRM University)",
    "Vellore Institute of Technology (VIT)",
    "Vignan's Foundation for Science, Technology & Research"
]

def get_college_data(university_name):
    """
    Queries Perplexity to get a structured JSON profile for a university.
    """
    url = "https://api.perplexity.ai/chat/completions"
    
    # We ask specifically for JSON format matching standard education portals
    prompt = f"""
    Generate a detailed JSON profile for {university_name}.
    The JSON structure MUST be exactly like this (fill in the data):
    
    {{
      "university_name": "{university_name}",
      "overview": {{
         "established_year": "YYYY",
         "location": "City, State",
         "type": "Private/Deemed/Public",
         "approval": "UGC, AICTE, etc.",
         "campus_size": "XM Acres",
         "description": "2-3 sentences about the legacy and key highlights."
      }},
      "rankings": [
         "NIRF Ranking 2024: #X",
         "NAAC Grade: A++",
         "Other notable rankings"
      ],
      "courses_and_fees": [
         {{
            "course_name": "B.Tech Computer Science",
            "duration": "4 Years",
            "total_tuition_fee": "Approx ₹X Lakhs",
            "eligibility": "Class 12 with X% + Entrance Exam info"
         }},
         {{
             "course_name": "MBA",
             "duration": "2 Years",
             "total_tuition_fee": "Approx ₹X Lakhs",
             "eligibility": "Graduation with X%"
         }}
         // Add 3-4 other popular courses (B.Sc, M.Tech, BBA, etc.)
      ],
      "placements": {{
         "highest_package": "₹X LPA",
         "average_package": "₹X LPA",
         "major_recruiters": ["Company A", "Company B", "Company C"],
         "placement_stats": "Brief summary of recent placement season success."
      }},
      "facilities": [
         "Library", "Hostel", "Sports Complex", "Labs", "Gym", "Wi-Fi Campus", "Cafeteria"
      ],
      "scholarships": [
         "Merit Scholarship: Details",
         "Sports Scholarship: Details"
      ],
      "contact_info": {{
         "website": "URL",
         "address": "Full Address"
      }}
    }}
    
    RETURN ONLY THE RAW JSON. NO MARKDOWN FORMATTING. NO EXPLANATORY TEXT.
    """

    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful data extraction assistant that outputs only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print(f"🤖 Querying Perplexity for: {university_name}...")
        response = requests.post(url, json=payload, headers=headers)
        
        # improved error handling
        if response.status_code != 200:
            print(f"Server returned error: {response.text}")
        
        response.raise_for_status()
        
        content = response.json()['choices'][0]['message']['content']
        
        # Robust JSON extraction
        import re
        try:
            # Find the JSON block
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON Parse Error. Raw content received:\n{content}")
            raise e
        
    except Exception as e:
        print(f"❌ Error fetching details for {university_name}: {e}")
        return None

def main():
    print("🚀 Starting Perplexity-Powered College Data Extraction...\n")
    
    all_data = []
    
    for uni in UNIVERSITIES:
        data = get_college_data(uni)
        if data:
            all_data.append(data)
            
            # Save individual files as well
            filename = f"{uni.split(' ')[0].lower()}_profile_enhanced.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"✅ Saved clean data to: {filename}\n")
        else:
            print(f"⚠️ Skipping {uni} due to error.\n")
            
        time.sleep(2) # rate verify
    
    # Save combined file
    with open('all_colleges_enhanced_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4)
    
    print("✨ Extraction Complete! Combined data saved to 'all_colleges_enhanced_data.json'")

if __name__ == "__main__":
    main()
