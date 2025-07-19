"""
src/phase1_preprocessing/document_parser.py

Entrypoint for parsing itinerary documents (.pdf, .docx).
Dispatches extraction and cleaning based on file type.
"""

import os
from .pdf_extractor import extract_pdf_text
from .docx_extractor import extract_docx_text
from .text_cleaner import clean_text

from config.settings import SUPPORTED_FILETYPES

class UnsupportedFileTypeError(Exception):
    pass

def parse_document(file_path: str) -> str:
    """
    Given a file path to an itinerary document (.pdf or .docx),
    returns the cleaned plaintext content preserving logical order.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext not in SUPPORTED_FILETYPES:
        raise UnsupportedFileTypeError(
            f"File type '{ext}' not supported. Supported types: {SUPPORTED_FILETYPES}"
        )

    # Route to appropriate extractor
    if ext == ".pdf":
        raw_text = extract_pdf_text(file_path)
    elif ext == ".docx":
        raw_text = extract_docx_text(file_path)
    else:
        # Defensive, shouldn't reach here due to above check.
        raise UnsupportedFileTypeError(
            f"File type '{ext}' not recognized by parser."
        )

    # Clean up and return text
    cleaned = clean_text(raw_text)
    return cleaned

# Example usage / CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python document_parser.py <file>")
        exit(1)
    doc_path = sys.argv[1]
    print(parse_document(doc_path))
