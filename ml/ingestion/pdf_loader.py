import os
import fitz


def load_pdf(file_path):
    doc = fitz.open(file_path)
    source_name = os.path.basename(file_path)
    pages = []

    for i, page in enumerate(doc):
        pages.append(
            {
                "source": source_name,
                "page": i + 1,
                "text": page.get_text(),
            }
        )

    doc.close()
    return pages