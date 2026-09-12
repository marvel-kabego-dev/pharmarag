import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingestion.cleaner import clean_pages
from ingestion.pdf_loader import load_pdf


def main():
    pdf_path = ROOT / "data" / "lantus-epar-summary-public_en.pdf"

    pages = load_pdf(str(pdf_path))
    text = pages[0]["text"]
    lines = text.splitlines()

    print(f"Longueur du texte brut de la page 1 : {len(text)}")

    for line in lines[:20]:
        print(f"{len(line):3d} | {line}")

    pages = clean_pages(pages)

    print(f"Pages extraites : {len(pages)}")

    if pages:
        first_page_text = pages[0]["text"] or ""
        print("\n200 premiers caractères après nettoyage :\n")
        print(first_page_text[:200])


if __name__ == "__main__":
    main()
