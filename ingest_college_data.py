
import json
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

# --- Configuration ---
COLLECTION_NAME = "university_data" # Re-use same collection for unified search
MODEL_NAME = "all-MiniLM-L6-v2"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
INPUT_FILE = "college_data.json"

def main():
    print(f"🚀 Starting Ingestion for {INPUT_FILE}...")

    # 1. Load Model
    print(f"🔹 Loading Model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # 2. Connect to Qdrant
    print(f"🔹 Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # 3. Ensure Collection Exists (Do not recreate if it exists, to keep previous data? 
    #    Actually, user might want to mix. I'll check existence first.)
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if not exists:
        print(f"🔹 Creating Collection: {COLLECTION_NAME}")
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
    else:
        print(f"🔹 Collection {COLLECTION_NAME} exists. Appending data...")

    # 4. Load JSON
    print("🔹 Loading JSON File...")
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return

    # 5. Process Chunks
    # Structure is { "Category": ["line1", "line2"], ... }
    chunks = []
    
    # We'll infer university name from content or hardcode if it's single-uni file
    # Based on preview, it is Vignan University.
    default_uni_name = "Vignan University"

    for category, lines in data.items():
        if isinstance(lines, list):
            for line in lines:
                if not isinstance(line, str) or not line.strip():
                    continue
                
                # Create a chunk
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "text": line.strip(),
                    "payload": {
                        "university": default_uni_name,
                        "category": category,
                        "source": INPUT_FILE
                    }
                })

    print(f"🔹 Prepared {len(chunks)} text chunks for ingestion.")

    # 6. Embed & Upsert in Batches
    batch_size = 100
    points = []
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        texts = [c["text"] for c in batch]
        
        # Embed
        embeddings = model.encode(texts).tolist()
        
        # Prepare Points
        for idx, item in enumerate(batch):
            points.append(PointStruct(
                id=item["id"],
                vector=embeddings[idx],
                payload={"text": item["text"], **item["payload"]}
            ))
            
        # Upsert
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        points = []
        print(f"   Upserted batch {i} - {i+len(batch)}...")

    print(f"✅ Successfully pushed {INPUT_FILE} to Qdrant!")

if __name__ == "__main__":
    main()
