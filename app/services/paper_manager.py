import json
import shutil
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import UPLOADS_DIR
from app.models import ResearchPaper
from app.services.field_analyzer import classify_fields
from app.services.paper_parser import analyze_paper_structure
from app.services.plagiarism import check_plagiarism
from app.services.text_extractor import extract_text, guess_title

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def paper_to_dict(paper: ResearchPaper) -> dict:
    keywords = []
    secondary_fields = []

    if paper.keywords:
        try:
            keywords = json.loads(paper.keywords)
        except json.JSONDecodeError:
            keywords = [paper.keywords]

    if paper.secondary_fields:
        try:
            secondary_fields = json.loads(paper.secondary_fields)
        except json.JSONDecodeError:
            secondary_fields = [paper.secondary_fields]

    return {
        "id": paper.id,
        "title": paper.title,
        "author": paper.author,
        "department": paper.department,
        "publication_year": paper.publication_year,
        "filename": paper.filename,
        "file_type": paper.file_type,
        "primary_field": paper.primary_field,
        "secondary_fields": secondary_fields,
        "keywords": keywords,
        "format_score": paper.format_score,
        "word_count": paper.word_count,
        "created_at": paper.created_at,
    }


def get_existing_papers_payload(db: Session) -> list[dict]:
    papers = db.query(ResearchPaper).all()
    return [
        {
            "id": paper.id,
            "title": paper.title,
            "author": paper.author,
            "extracted_text": paper.extracted_text,
        }
        for paper in papers
    ]


def process_uploaded_file(
    db: Session,
    file_bytes: bytes,
    filename: str,
    title: str = "",
    author: str = "",
    department: str = "",
    publication_year: int | None = None,
    block_duplicates: bool = True,
) -> dict:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    stored_name = f"{uuid.uuid4().hex}{extension}"
    stored_path = UPLOADS_DIR / stored_name
    stored_path.write_bytes(file_bytes)

    file_type = extension.lstrip(".")
    try:
        extracted_text = extract_text(stored_path, file_type)
    except ValueError:
        stored_path.unlink(missing_ok=True)
        raise

    resolved_title = title.strip() or guess_title(extracted_text, filename)
    structure = analyze_paper_structure(extracted_text)
    field_info = classify_fields(extracted_text)
    plagiarism_report = check_plagiarism(extracted_text, get_existing_papers_payload(db))

    if block_duplicates and plagiarism_report["status"] == "duplicate_detected":
        stored_path.unlink(missing_ok=True)
        return {
            "success": False,
            "message": "Duplicate or highly similar content detected.",
            "plagiarism_report": plagiarism_report,
        }

    paper = ResearchPaper(
        title=resolved_title,
        author=author.strip() or None,
        department=department.strip() or None,
        publication_year=publication_year,
        filename=filename,
        file_path=str(stored_path),
        file_type=file_type,
        extracted_text=extracted_text,
        primary_field=field_info["primary_field"],
        secondary_fields=json.dumps(field_info["secondary_fields"]),
        keywords=json.dumps(field_info["keywords"]),
        format_score=structure["format_score"],
        word_count=len(extracted_text.split()),
    )

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return {
        "success": True,
        "paper": paper_to_dict(paper),
        "structure": {
            "format_score": structure["format_score"],
            "found_sections": structure["found_section_names"],
            "missing_sections": structure["missing_sections"],
        },
        "plagiarism_report": plagiarism_report,
    }


def check_file_plagiarism(db: Session, file_bytes: bytes, filename: str) -> dict:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type.")

    temp_name = f"temp_{uuid.uuid4().hex}{extension}"
    temp_path = UPLOADS_DIR / temp_name

    try:
        temp_path.write_bytes(file_bytes)
        extracted_text = extract_text(temp_path, extension.lstrip("."))
        return check_plagiarism(extracted_text, get_existing_papers_payload(db))
    finally:
        temp_path.unlink(missing_ok=True)


def delete_paper(db: Session, paper_id: int) -> bool:
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper:
        return False

    file_path = Path(paper.file_path)
    if file_path.exists():
        file_path.unlink()

    db.delete(paper)
    db.commit()
    return True
