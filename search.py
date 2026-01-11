
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Config
COLLECTION_NAME = "university_data"
MODEL_NAME = "all-MiniLM-L6-v2"

def search_university(query):
    # 1. Init
    client = QdrantClient(host="localhost", port=6333)
    model = SentenceTransformer(MODEL_NAME)
    
    # 2. Embed Query
    query_vector = model.encode(query).tolist()
    
    # 3. Search
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=3
    )
    
    # 4. Display
    print(f"\n🔍 Query: '{query}'\n")
    for r in results:
        payload = r.payload
        print(f"🏆 Score: {r.score:.4f}")
        print(f"🎓 University: {payload.get('university')}")
        print(f"📄 Detail: {payload.get('text')}")
        print("-" * 50)

if __name__ == "__main__":
    while True:
        user_q = input("\nEnter query (or 'q' to quit): ")
        if user_q.lower() == 'q':
            break
        search_university(user_q)
