import json
import logging
import sys
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "universities"
VECTOR_SIZE = 384  # Standard embedding size

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
    """Flatten university data into searchable chunks."""
    chunks = []
    
    for uni in universities:
        name = uni.get('university_name', 'Unknown University')
        base_payload = {"university": name}
        
        # Overview Chunk
        overview = uni.get('overview', {})
        if isinstance(overview, dict):
            overview_text = f"{name} Overview. {overview.get('description', '')} Location: {overview.get('location', '')}. Type: {overview.get('type', '')}."
            chunks.append({
                "text": overview_text, 
                "payload": {**base_payload, "category": "Overview", "details": overview}
            })

        # Placements Chunk
        placements = uni.get('placements', {})
        if isinstance(placements, dict):
            place_text = f"{name} Placements. {placements.get('description', '')} Highest Package: {placements.get('highest_package', '')}. Average: {placements.get('average_package', '')}."
            chunks.append({
                "text": place_text,
                "payload": {**base_payload, "category": "Placements", "details": placements}
            })

        # Courses Chunks
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

        # Facilities Chunk
        facilities = uni.get('facilities', [])
        if facilities:
            fac_text = f"{name} Facilities: {', '.join(facilities) if isinstance(facilities, list) else str(facilities)}"
            chunks.append({
                "text": fac_text,
                "payload": {**base_payload, "category": "Facilities", "details": facilities}
            })

    return chunks

def create_dummy_vector():
    """Create a random vector for testing (replace with real embeddings later)."""
    return [random.random() for _ in range(VECTOR_SIZE)]

def ingest_data():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "data.json"
    logging.info(f"📚 Loading data from {filepath}...")
    data = load_data(filepath)
    if not data:
        logging.error(f"No data found! Please ensure '{filepath}' exists and contains valid JSON.")
        return

    logging.info(f"Loaded {len(data)} universities.")

    # Connect to Qdrant
    logging.info(f"🔌 Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        client.get_collections()
    except Exception as e:
        logging.error(f"❌ Could not connect to Qdrant: {e}")
        logging.info("💡 HINT: Is Docker running? Run 'start_qdrant.bat' first.")
        return

    # Create Collection
    logging.info(f"🛠️  Creating/Recreating collection '{COLLECTION_NAME}'...")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    # Process and Upsert
    logging.info("⚙️  Processing text chunks...")
    chunks = prepare_chunks(data)
    logging.info(f"Generated {len(chunks)} search chunks.")

    batch_size = 50
    total_upserted = 0

    logging.info("🚀 Starting ingestion with dummy vectors (replace with embeddings later)...")
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        
        # Create points with dummy vectors
        points = [
            PointStruct(
                id=i + idx,
                vector=create_dummy_vector(),
                payload={"text": item['text'], **item['payload']}
            )
            for idx, item in enumerate(batch)
        ]
        
        # Upload
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        total_upserted += len(points)
        print(f"   Processed {total_upserted}/{len(chunks)} chunks...")

    logging.info(f"✅ Successfully Ingested {total_upserted} points into Qdrant collection '{COLLECTION_NAME}'!")
    logging.info(f"⚠️  Note: Using random vectors. Install sentence-transformers for proper embeddings.")

if __name__ == "__main__":
    ingest_data()
