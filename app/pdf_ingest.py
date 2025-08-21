import fitz  # PyMuPDF
from typing import List, Dict

def load_pdf(path: str) -> List[Dict]:
    doc = fitz.open(path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        pages.append({"page": i+1, "text": text})
    return pages
