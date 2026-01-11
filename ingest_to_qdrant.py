
import json
import logging
import sys
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "universities"
MODEL_NAME = "all-MiniLM-L6-v2" # Fast and effective model

def load_data(filepath):
    """Load JSON data from file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logging.error(f"Failed to load file {filepath}: {e}")
        return []

def prepare_chunks(universities):
    """
    Flatten university data into searchable chunks.
    We'll create separate vectors for:
    1. Overview
    2. Placements
    3. Individual courses
    4. Facilities
    """
    chunks = []
    
    for uni in universities:
        name = uni.get('university_name', 'Unknown University')
        base_payload = {"university": name}
        
        # 1. Overview Chunk
        overview = uni.get('overview', {})
        if isinstance(overview, dict):
            overview_text = f"{name} Overview. {overview.get('description', '')} Location: {overview.get('location', '')}. Type: {overview.get('type', '')}."
            chunks.append({
                "text": overview_text, 
                "payload": {**base_payload, "category": "Overview", "details": overview}
            })

        # 2. Placements Chunk
        placements = uni.get('placements', {})
        if isinstance(placements, dict):
            place_text = f"{name} Placements. {placements.get('description', '')} Highest Package: {placements.get('highest_package', '')}. Average: {placements.get('average_package', '')}."
            chunks.append({
                "text": place_text,
                "payload": {**base_payload, "category": "Placements", "details": placements}
            })

        # 3. Courses Chunks (One per course for better precision)
        courses = uni.get('courses_and_fees', [])
        if isinstance(courses, list):
            for course in courses:
                if isinstance(course, dict):
                    c_name = course.get('course_name', 'Unknown Course')
                    c_text = f"{name} Course: {c_name}. Fees: {course.get('total_tuition_fee', '')}. Eligibility: {course.get('eligibility', '')}."
                    chunks.append({
                        "text": c_text,
                        "payload": {**base_payload, "category": "Course", "course_name": c_name, "details": course}
                    })

        # 4. Facilities Chunk
        facilities = uni.get('facilities', [])
        if facilities:
            fac_text = f"{name} Facilities: {', '.join(facilities) if isinstance(facilities, list) else str(facilities)}"
            chunks.append({
                "text": fac_text,
                "payload": {**base_payload, "category": "Facilities", "details": facilities}
            })

    return chunks

def ingest_data():
    # 1. Check for File
    filepath = sys.argv[1] if len(sys.argv) > 1 else "data.json"
    logging.info(f"📚 Loading data from {filepath}...")
    data = load_data(filepath)
    if not data:
        logging.error(f"No data found! Please ensure '{filepath}' exists and contains valid JSON.")
        return

    logging.info(f"Loaded {len(data)} universities.")

    # 2. Initialize Model
    logging.info(f"🧠 Loading embedding model '{MODEL_NAME}'...")
    try:
        model = SentenceTransformer(MODEL_NAME)
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        return

    # 3. Connect to Qdrant
    logging.info(f"🔌 Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        # Check connection
        client.get_collections()
    except Exception as e:
        logging.error(f"❌ Could not connect to Qdrant: {e}")
        logging.info("💡 HINT: Is Docker running? Run 'docker run -p 6333:6333 qdrant/qdrant' first.")
        return

    # 4. Create Collection
    logging.info(f"🛠️  Creating/Recreating collection '{COLLECTION_NAME}'...")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    # 5. Process and Upsert
    logging.info("⚙️  Processing text chunks...")
    chunks = prepare_chunks(data)
    logging.info(f"Generated {len(chunks)} search chunks.")

    batch_size = 50
    total_upserted = 0

    logging.info("🚀 Starting ingestion...")
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        texts = [item['text'] for item in batch]
        payloads = [item['payload'] for item in batch]
        
        # Generate embeddings
        embeddings = model.encode(texts).tolist()
        
        # Create points
        points = [
            PointStruct(
                id=i + idx,
                vector=emb,
                payload={"text": txt, **pay}
            )
            for idx, (txt, pay, emb) in enumerate(zip(texts, payloads, embeddings))
        ]
        
        # Upload
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        total_upserted += len(points)
        print(f"   Processed {total_upserted}/{len(chunks)} chunks...")

    logging.info(f"✅ Successfully Ingested {total_upserted} points into Qdrant collection '{COLLECTION_NAME}'!")

if __name__ == "__main__":
    ingest_data()
