
import requests
import json
import re
import os

API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

def get_vignan():
    url = "https://api.perplexity.ai/chat/completions"
    
    prompt = """
    Generate a JSON profile for Vignan's Foundation for Science, Technology & Research (Vignan University).
    Structure:
    {
      "university_name": "Vignan University",
      "overview": { "established_year": "...", "location": "...", "type": "...", "campus_size": "..." },
      "rankings": ["NIRF...", "NAAC..."],
      "courses_and_fees": [
         { "course_name": "B.Tech CSE", "fee": "...", "eligibility": "..." },
         { "course_name": "MBA", "fee": "..." }
      ],
      "placements": { "highest_package": "...", "average_package": "..." },
      "facilities": ["..."],
      "contact": { "website": "...", "address": "..." }
    }
    RETURN ONLY JSON.
    """

    payload = {
        "model": "sonar", 
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print("🤖 Retrying extraction for Vignan University (Attempt 2 - Sonar Model)...")
        response = requests.post(url, json=payload, headers=headers)
        content = response.json()['choices'][0]['message']['content']
        
        # Regex extract
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            json_str = match.group(0)
            # Try to clean common trailing comma errors
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            try:
                data = json.loads(json_str)
                with open('vignan_profile_enhanced.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                print("✅ Success! Dictionary saved to vignan_profile_enhanced.json")
            except Exception as parse_err:
                print(f"❌ JSON Parse Error on cleaned string: {parse_err}")
                print(f"Raw String: {json_str}")
        else:
            print("❌ Failed to find JSON in response")
            print(f"Full Content: {content}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_vignan()
