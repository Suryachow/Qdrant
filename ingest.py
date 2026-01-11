
import json
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

# --- Configuration ---
COLLECTION_NAME = "university_data"
MODEL_NAME = "all-MiniLM-L6-v2"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

def get_chunks(data):
    """
    Transforms the complex nested university JSON into a flat list of text chunks
    suitable for embedding.
    """
    chunks = []
    
    for uni in data:
        base_info = {
            "university": uni.get("university_name"),
            "location": uni.get("overview", {}).get("location")
        }
        
        # 1. Overview Chunk
        overview = uni.get("overview", {})
        text = f"{uni['university_name']} Overview: {overview.get('description', '')}"
        chunks.append({
            "id": str(uuid.uuid4()),
            "text": text,
            "payload": {**base_info, "category": "Overview", **overview}
        })
        
        # 2. Placements Chunk
        placements = uni.get("placements", {})
        text = f"{uni['university_name']} Placements: {placements.get('description', '')} Highest: {placements.get('highest_package')} Average: {placements.get('average_package')}"
        chunks.append({
            "id": str(uuid.uuid4()),
            "text": text,
            "payload": {**base_info, "category": "Placements", **placements}
        })
        
        # 3. Courses Chunks
        courses = uni.get("courses_and_fees", [])
        for course in courses:
            text = f"{uni['university_name']} Course: {course.get('course_name')} Duration: {course.get('duration')} Fees: {course.get('total_tuition_fee')} Eligibility: {course.get('eligibility')}"
            chunks.append({
                "id": str(uuid.uuid4()),
                "text": text,
                "payload": {**base_info, "category": "Courses", **course}
            })
            
        # 4. Facilities Chunk
        facilities = uni.get("facilities", [])
        if facilities:
            text = f"{uni['university_name']} Facilities: {', '.join(facilities) if isinstance(facilities, list) else str(facilities)}"
            chunks.append({
                "id": str(uuid.uuid4()),
                "text": text,
                "payload": {**base_info, "category": "Facilities"}
            })
            
    return chunks

def main():
    print("🚀 Starting Ingestion Pipeline...")

    # 1. Load Model
    print(f"🔹 Loading Model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # 2. Connect to Qdrant
    print(f"🔹 Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # 3. Create Collection
    print(f"🔹 Creating Collection: {COLLECTION_NAME}")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

    # 4. Load & Process Data
    print("🔹 Loading Local JSON...")
    with open("data.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    chunks = get_chunks(raw_data)
    print(f"🔹 Processed {len(chunks)} searchable chunks from {len(raw_data)} universities.")

    # 5. Embed & Upsert
    print("🔹 Generating Embeddings and Upserting...")
    
    points = []
    batch_size = 64
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        texts = [c["text"] for c in batch]
        
        embeddings = model.encode(texts).tolist()
        
        for idx, item in enumerate(batch):
            points.append(PointStruct(
                id=item["id"],
                vector=embeddings[idx],
                payload={"text": item["text"], **item["payload"]}
            ))
            
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        points = [] # Clear batch
        print(f"   Saved batch {i} - {i+len(batch)}...")

    print("✅ Data successfully inserted into Qdrant!")

if __name__ == "__main__":
    main()
