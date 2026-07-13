import json
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import UPLOADS_DIR, get_db
from app.models import ResearchPaper
from app.services.field_analyzer import classify_fields
from app.services.paper_parser import analyze_paper_structure
from app.services.plagiarism import check_plagiarism
from app.services.text_extractor import extract_text, guess_title

router = APIRouter(prefix="/api/papers", tags=["papers"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def _paper_to_dict(paper: ResearchPaper) -> dict:
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
        "created_at": paper.created_at.isoformat() if paper.created_at else None,
    }


@router.get("")
def list_papers(db: Session = Depends(get_db)):
    papers = db.query(ResearchPaper).order_by(ResearchPaper.created_at.desc()).all()
    return [_paper_to_dict(paper) for paper in papers]


@router.get("/{paper_id}")
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    data = _paper_to_dict(paper)
    structure = analyze_paper_structure(paper.extracted_text)
    data["structure"] = {
        "format_score": structure["format_score"],
        "found_sections": structure["found_section_names"],
        "missing_sections": structure["missing_sections"],
    }
    return data


@router.post("/upload")
async def upload_paper(
    file: UploadFile = File(...),
    title: str = Form(""),
    author: str = Form(""),
    department: str = Form(""),
    publication_year: int | None = Form(None),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    stored_name = f"{uuid.uuid4().hex}{extension}"
    stored_path = UPLOADS_DIR / stored_name

    with stored_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_type = extension.lstrip(".")
    try:
        extracted_text = extract_text(stored_path, file_type)
    except ValueError as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    resolved_title = title.strip() or guess_title(extracted_text, file.filename)
    structure = analyze_paper_structure(extracted_text)
    field_info = classify_fields(extracted_text)

    existing = db.query(ResearchPaper).all()
    existing_payload = [
        {
            "id": paper.id,
            "title": paper.title,
            "author": paper.author,
            "extracted_text": paper.extracted_text,
        }
        for paper in existing
    ]
    plagiarism_report = check_plagiarism(extracted_text, existing_payload)

    if plagiarism_report["status"] == "duplicate_detected":
        stored_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Duplicate or highly similar content detected.",
                "plagiarism_report": plagiarism_report,
            },
        )

    paper = ResearchPaper(
        title=resolved_title,
        author=author.strip() or None,
        department=department.strip() or None,
        publication_year=publication_year,
        filename=file.filename,
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

    response = _paper_to_dict(paper)
    response["structure"] = {
        "format_score": structure["format_score"],
        "found_sections": structure["found_section_names"],
        "missing_sections": structure["missing_sections"],
    }
    response["plagiarism_report"] = plagiarism_report
    return response


@router.post("/check-plagiarism")
async def check_plagiarism_only(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    temp_name = f"temp_{uuid.uuid4().hex}{extension}"
    temp_path = UPLOADS_DIR / temp_name

    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_text(temp_path, extension.lstrip("."))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        temp_path.unlink(missing_ok=True)

    existing = db.query(ResearchPaper).all()
    existing_payload = [
        {
            "id": paper.id,
            "title": paper.title,
            "author": paper.author,
            "extracted_text": paper.extracted_text,
        }
        for paper in existing
    ]

    return check_plagiarism(extracted_text, existing_payload)


@router.delete("/{paper_id}")
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    file_path = Path(paper.file_path)
    if file_path.exists():
        file_path.unlink()

    db.delete(paper)
    db.commit()
    return {"message": "Paper deleted successfully."}
