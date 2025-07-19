"""
src/phase1_preprocessing/pdf_extractor.py

Extracts structured text from PDF itinerary documents.
Prefers digital text, falls back to OCR if needed.
"""

import os
import logging

from pdfminer.high_level import extract_text as pdfminer_extract_text
from PyPDF2 import PdfReader

# Optional: Add OCR fallback for scanned PDFs
import fitz  # PyMuPDF
import tempfile
import pytesseract

logging.basicConfig(level=logging.INFO)

def extract_pdf_text(file_path: str) -> str:
    """
    Extracts structured text from a PDF document.
    Strategy:
        1. Try pdfminer.six (preserves layout, headings, etc.)
        2. Try PyPDF2 (faster for simple PDFs)
        3. Use OCR (PyMuPDF + pytesseract) for scanned/image PDFs

    Returns:
        str - The extracted plaintext from the PDF.
    """
    # 1. Try PDFMiner: handles headings, lists, etc.
    try:
        text = pdfminer_extract_text(file_path)
        if text and text.strip():
            logging.info("Text extracted using pdfminer.six.")
            return text
    except Exception as e:
        logging.warning(f"pdfminer.six extraction failed: {e}")

    # 2. Try PyPDF2: fallback for some PDFs
    try:
        reader = PdfReader(file_path)
        pages = [
            page.extract_text() or '' for page in reader.pages
        ]
        text = "\n".join(pages)
        if text and text.strip():
            logging.info("Text extracted using PyPDF2.")
            return text
    except Exception as e:
        logging.warning(f"PyPDF2 extraction failed: {e}")

    # 3. OCR fallback using pytesseract and PyMuPDF (fitz)
    try:
        text_blocks = []
        pdf_doc = fitz.open(file_path)
        for i, page in enumerate(pdf_doc):
            # Render page as image
            pix = page.get_pixmap(dpi=300)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
                pix.save(temp_img.name)
                ocr_text = pytesseract.image_to_string(temp_img.name)
                text_blocks.append(ocr_text)
                os.unlink(temp_img.name)
        ocr_text = "\n".join(text_blocks).strip()
        if ocr_text:
            logging.info("Text extracted using OCR fallback.")
            return ocr_text
        else:
            raise ValueError("OCR produced no text.")
    except Exception as e:
        logging.error(f"OCR extraction failed: {e}")
        raise RuntimeError(
            "Failed to extract text from PDF using all available methods."
        ) from e

# Debug/CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python pdf_extractor.py <pdf_file>")
        exit(1)
    pdf_fp = sys.argv[1]
    print(extract_pdf_text(pdf_fp))
