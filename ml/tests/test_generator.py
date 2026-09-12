import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from retrieval.retriever import retrieve
from generation.generator import generate


if __name__ == '__main__':
    question = "What are the side effects of Humira?"
    try:
        chunks = retrieve(question)
    except Exception as e:
        print("Erreur lors de la récupération des chunks:", e)
        chunks = []

    try:
        result = generate(question, chunks)
    except Exception as e:
        print("Erreur lors de la génération:", e)
        result = {"reponse": "", "sources": [], "statut": "non_disponible"}

    print(result.get("reponse"))
    print(result.get("sources"))
    print(result.get("statut"))
