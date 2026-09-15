from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from embedding.embedder import get_embedding, client_qdrant, _COLLECTION


def retrieve(question: str, user_id: str, top_k: int = 5) -> List[Dict[str, Any]]:

	vecteur_question = get_embedding(question)

	results = client_qdrant.query_points(
		collection_name=_COLLECTION,
		query=vecteur_question,
		query_filter=Filter(
			must=[FieldCondition(
				key="user_id",
				match=MatchValue(value=user_id)
			)]
		),
		limit=top_k,
	).points

	out: List[Dict[str, Any]] = []
	for r in results:
		out.append({
			"text": r.payload.get("text", ""),
			"source": r.payload.get("source"),
			"page": r.payload.get("page"),
			"score": round(r.score, 4) if getattr(r, 'score', None) is not None else None,
		})

	return out

