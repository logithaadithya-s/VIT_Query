from pathlib import Path

import pdfplumber
from docx import Document


def extract_text_from_pdf(file_path: Path) -> str:
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_text_from_docx(file_path: Path) -> str:
    document = Document(file_path)
    return "\n\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())


def extract_text_from_txt(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore")


def extract_text(file_path: Path, file_type: str) -> str:
    extractors = {
        "pdf": extract_text_from_pdf,
        "docx": extract_text_from_docx,
        "txt": extract_text_from_txt,
    }

    extractor = extractors.get(file_type)
    if not extractor:
        raise ValueError(f"Unsupported file type: {file_type}")

    text = extractor(file_path)
    if not text or len(text.strip()) < 50:
        raise ValueError("Could not extract enough text from the document.")

    return text.strip()


def guess_title(text: str, filename: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:15]:
        if 10 <= len(line) <= 200 and not line.lower().startswith("abstract"):
            return line
    return Path(filename).stem.replace("_", " ").replace("-", " ").title()
