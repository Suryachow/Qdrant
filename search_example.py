from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)

# Search by filtering
results = client.scroll(
    collection_name="universities",
    scroll_filter={
        "must": [
            {
                "key": "category",
                "match": {"value": "Placements"}
            }
        ]
    },
    limit=5,
    with_payload=True
)[0]

print("\n🔍 Sample Search: All Placements Data\n")
for point in results:
    print(f"University: {point.payload['university']}")
    print(f"Text: {point.payload['text'][:200]}...\n")
