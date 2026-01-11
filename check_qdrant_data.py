import json
from qdrant_client import QdrantClient

# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# Get collection info
collection_info = client.get_collection("universities")
print(f"\n📊 Collection: universities")
print(f"   Total points: {collection_info.points_count}")
print(f"   Vector size: {collection_info.config.params.vectors.size}")
print(f"   Status: {collection_info.status}\n")

# Retrieve first 10 points
print("📝 Sample Data (first 10 points):\n")
points = client.scroll(
    collection_name="universities",
    limit=10,
    with_payload=True,
    with_vectors=False
)[0]

for i, point in enumerate(points, 1):
    print(f"\n{i}. ID: {point.id}")
    print(f"   University: {point.payload.get('university', 'N/A')}")
    print(f"   Category: {point.payload.get('category', 'N/A')}")
    print(f"   Text preview: {point.payload.get('text', '')[:100]}...")

# Check for duplicates by university name
print("\n\n📋 Points per University:")
all_points = client.scroll(
    collection_name="universities",
    limit=1000,
    with_payload=True,
    with_vectors=False
)[0]

uni_counts = {}
for point in all_points:
    uni_name = point.payload.get('university', 'Unknown')
    uni_counts[uni_name] = uni_counts.get(uni_name, 0) + 1

for uni, count in sorted(uni_counts.items()):
    print(f"   {uni}: {count} chunks")
