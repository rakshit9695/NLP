"""
src/phase1_preprocessing/text_cleaner.py

Cleans up extracted itinerary text:
- removes page numbers, headers/footers,
- flattens whitespace,
- standardizes breaks,
- ready for NLP pipeline.
"""

import re

def clean_text(text: str) -> str:
    # Remove common patterns: "Page X", "page X / Y", document headers/footers
    text = re.sub(r"(?mi)^page\s*\d+([^\w]|$)", "", text)
    text = re.sub(r"(?mi)^page\s*\d+\s*\/\s*\d+", "", text)
    text = re.sub(r"(?:\n(?:\s*[\w ]+\s*\n)?){0,1}(?:[—–-]{3,}|_{3,})\n", "", text)  # horizontal rules

    # Remove any footer-like patterns (dates, filepaths, etc. at line start or end)
    text = re.sub(r"(?m)^\s*(Exported\s+on|Created\s+by|Itinerary\s+Report).*$", "", text)

    # Normalize multiple newlines to single
    text = re.sub(r"\n{2,}", "\n\n", text)

    # Remove excess leading/trailing whitespace
    text = text.strip()

    # Collapse whitespace within lines
    cleaned = "\n".join(line.strip() for line in text.splitlines())
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)

    # Remove stray repeated punctuation (triple hyphens, etc.)
    cleaned = re.sub(r"[-_=]{4,}", "", cleaned)

    # Optionally, remove lines only containing numbers (leftover page numbers)
    cleaned = re.sub(r'(?m)^\d+\s*$', '', cleaned)

    # Optionally, remove control characters
    cleaned = re.sub(r'[\x00-\x1F\x7F]', '', cleaned)

    return cleaned

# For quick debug/CLI testing
if __name__ == "__main__":
    import sys
    with open(sys.argv[1], 'r', encoding='utf-8') as fin:
        print(clean_text(fin.read()))
