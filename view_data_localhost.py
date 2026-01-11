from qdrant_client import QdrantClient
import json

# Connect to localhost
client = QdrantClient(host="localhost", port=6333)

print("\n" + "="*60)
print("🌐 QDRANT DATA ON LOCALHOST:6333")
print("="*60 + "\n")

# Get collection info
info = client.get_collection("universities")
print(f"✅ Collection: universities")
print(f"📊 Total Points: {info.points_count}")
print(f"🔗 Accessible at: http://localhost:6333/dashboard\n")

# Fetch first 5 data points
print("📝 SAMPLE DATA FROM LOCALHOST:\n")
points = client.scroll(
    collection_name="universities",
    limit=5,
    with_payload=True,
    with_vectors=False
)[0]

for i, point in enumerate(points, 1):
    print(f"{i}. University: {point.payload['university']}")
    print(f"   Category: {point.payload['category']}")
    print(f"   Text: {point.payload['text'][:150]}...")
    print()

print("\n" + "="*60)
print("🌐 ACCESS YOUR DATA:")
print("="*60)
print(f"Dashboard: http://localhost:6333/dashboard")
print(f"API: http://localhost:6333/collections/universities")
print(f"\nRun this script anytime to view data on localhost!")
print("="*60 + "\n")
