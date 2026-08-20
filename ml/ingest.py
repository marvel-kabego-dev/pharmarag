import sys
import os
from pathlib import Path

from ingestion.pdf_loader import load_pdf
from ingestion.cleaner import clean_pages
from ingestion.chunker import split_pages
from embedding.embedder import embed_and_store, reset_collection

DATA_DIR = Path(__file__).parent / "data"

def ingest_all():
    pdfs = list(DATA_DIR.glob("*.pdf"))
    
    if not pdfs:
        print("Aucun PDF trouvé dans ml/data/")
        return

    all_chunks = []

    for pdf_path in pdfs:
        print(f"Traitement : {pdf_path.name}")
        pages = load_pdf(str(pdf_path))
        pages = clean_pages(pages)
        chunks = split_pages(pages)
        all_chunks.extend(chunks)
        print(f"  → {len(chunks)} chunks extraits")

    print("Réinitialisation de la collection Qdrant...")
    reset_collection()

    print(f"\nTotal : {len(all_chunks)} chunks — début de l'embedding...")
    ids = embed_and_store(all_chunks)
    print(f"✅ {len(ids)} chunks stockés dans Qdrant")

if __name__ == "__main__":
    ingest_all()