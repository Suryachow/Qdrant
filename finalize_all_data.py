
import json
import os
import glob

def merge_all_data():
    all_data = []
    
    # 1. Get Top 10 NIRF Files
    nirf_files = glob.glob("*_nirf_data.json")
    print(f"found {len(nirf_files)} NIRF files")
    
    for f in nirf_files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Ensure it's a dict (profile) not list
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
                print(f"  + Added {data.get('university_name', 'Unknown')}")
        except Exception as e:
            print(f"  x Failed to read {f}: {e}")

    # 2. Get SRM, VIT, Vignan
    special_files = [
        "srm_profile_enhanced.json",
        "vellore_profile_enhanced.json",
        "vignan_profile_enhanced.json"
    ]
    
    for f in special_files:
        if os.path.exists(f):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    all_data.append(data)
                    print(f"  + Added {data.get('university_name', 'Unknown')}")
            except Exception as e:
                print(f"  x Failed to read {f}: {e}")

    # 3. Save Combined
    output_filename = "all_university_data_combined.json"
    
    # Remove duplicates if any (by name)
    unique_data = {item['university_name']: item for item in all_data}.values()
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(list(unique_data), f, indent=4)
        
    print(f"\n✅ SUCCESSFULLY MERGED {len(unique_data)} UNIVERSITIES into '{output_filename}'")

if __name__ == "__main__":
    merge_all_data()
