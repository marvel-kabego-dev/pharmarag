import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.chunker import split_pages

def test_split_pages():
    mock_pages = [
        {
            "text": "La posologie recommandée chez l'adulte est de une injection par jour. " * 10,
            "source": "lantus-epar-summary-public_en.pdf",
            "page": 1,
        },
        {
            "text": "Keytruda est indiqué dans le traitement du mélanome avancé chez l'adulte. " * 10,
            "source": "keytruda-epar-medicine-overview_en.pdf",
            "page": 2,
        },
    ]

    chunks = split_pages(mock_pages)

    print(f"\n--- Nombre de chunks total : {len(chunks)} ---\n")

    for i, chunk in enumerate(chunks[:3]):
        print(f"Chunk #{i + 1}")
        print(f"  Source : {chunk['source']}")
        print(f"  Page   : {chunk['page']}")
        print(f"  ID     : {chunk['chunk_id']}")
        print(f"  Extrait: {chunk['text'][:100]}...")
        print("-" * 40)

if __name__ == "__main__":
    test_split_pages()