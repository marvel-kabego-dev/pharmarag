from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

load_dotenv()

def test_connection():
    client = QdrantClient(
        host=os.getenv("QDRANT_HOST"),
        port=int(os.getenv("QDRANT_PORT"))
    )

    # Crée une collection de test
    client.recreate_collection(
        collection_name="test_connection",
        vectors_config={"size": 4, "distance": "Cosine"}
    )

    # Vérifie qu'elle existe
    collections = client.get_collections()
    noms = [c.name for c in collections.collections]

    if "test_connection" in noms:
        print("✅ Connexion Qdrant OK")
    else:
        print("❌ Quelque chose a raté")

if __name__ == "__main__":
    test_connection()