
import json
import os

files = [
    "srm_profile_enhanced.json",
    "vellore_profile_enhanced.json",
    "vignan_profile_enhanced.json"
]

combined_data = []

for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            combined_data.append(data)
            print(f"✅ Loaded {f}")
    except Exception as e:
        print(f"❌ Failed to load {f}: {e}")

output_file = "all_colleges_enhanced_data.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(combined_data, f, indent=4)

print(f"\n✨ Combined {len(combined_data)} profiles into {output_file}")
