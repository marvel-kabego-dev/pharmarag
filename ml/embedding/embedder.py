import httpx
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from typing import List, Dict
from qdrant_client.models import PointStruct, VectorParams, Distance
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

client_qdrant = QdrantClient(
    host=os.getenv("QDRANT_HOST"),
    port=int(os.getenv("QDRANT_PORT")) if os.getenv("QDRANT_PORT") else None,
)

_COLLECTION = os.getenv("QDRANT_COLLECTION_NAME")

def get_embedding(text: str) -> list:
    response = httpx.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text
        },
        timeout=300.0
    )
    return response.json()["embedding"]

def _ensure_collection():
    existing = [c.name for c in client_qdrant.get_collections().collections]
    if _COLLECTION not in existing:
        client_qdrant.create_collection(
            collection_name=_COLLECTION,
            vectors_config=VectorParams(
                size=768,
                distance=Distance.COSINE
            )
        )

def reset_collection():
    existing = [c.name for c in client_qdrant.get_collections().collections]
    if _COLLECTION in existing:
        client_qdrant.delete_collection(_COLLECTION)
    client_qdrant.create_collection(
        collection_name=_COLLECTION,
        vectors_config=VectorParams(
            size=768,
            distance=Distance.COSINE
        )
    )

def embed_and_store(chunks: List[Dict]) -> List[int]:
    _ensure_collection()

    if not chunks:
        return []

    # Déterminer un id de départ simple à partir du nombre d'éléments déjà présents
    start_id = 0
    try:
        # QdrantClient.count retourne un objet avec attribut `count` dans certaines versions
        count_res = client_qdrant.count(collection_name=_COLLECTION)
        if hasattr(count_res, "count"):
            start_id = int(count_res.count)
        elif isinstance(count_res, int):
            start_id = int(count_res)
    except Exception:
        # Si la collection n'existe pas ou erreur, on part de 0
        start_id = 0

    points: List[PointStruct] = []
    assigned_ids: List[int] = []

    for i, chunk in enumerate(chunks):
        text = chunk.get("text", "")

        # Obtenir l'embedding depuis le service local
        vector = get_embedding(text)

        # Préparer le payload attendu
        payload = {
            "text": text,
            "source": chunk.get("source"),
            "page": chunk.get("page"),
            "chunk_id": chunk.get("chunk_id"),
        }

        point_id = start_id + i

        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
        )
        assigned_ids.append(point_id)

    # Upsert batch
    client_qdrant.upsert(
        collection_name=_COLLECTION,
        points=points,
    )

    return assigned_ids
