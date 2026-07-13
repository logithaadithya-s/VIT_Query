import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ResearchPaper
from app.services.field_analyzer import analyze_field_landscape

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def analytics_overview(db: Session = Depends(get_db)):
    papers = db.query(ResearchPaper).all()
    payload = []

    for paper in papers:
        keywords = []
        if paper.keywords:
            try:
                keywords = json.loads(paper.keywords)
            except json.JSONDecodeError:
                keywords = []

        payload.append(
            {
                "id": paper.id,
                "title": paper.title,
                "author": paper.author,
                "department": paper.department,
                "publication_year": paper.publication_year,
                "primary_field": paper.primary_field,
                "keywords": keywords,
                "extracted_text": paper.extracted_text,
            }
        )

    landscape = analyze_field_landscape(payload)

    avg_format = 0.0
    if papers:
        avg_format = round(sum(p.format_score or 0 for p in papers) / len(papers), 2)

    return {
        **landscape,
        "summary": {
            "total_papers": len(papers),
            "unique_fields": len({p.primary_field for p in papers if p.primary_field}),
            "average_format_score": avg_format,
            "departments_represented": len({p.department for p in papers if p.department}),
        },
    }


@router.get("/fields")
def field_breakdown(db: Session = Depends(get_db)):
    papers = db.query(ResearchPaper).all()
    counts = {}

    for paper in papers:
        field = paper.primary_field or "Unclassified"
        counts[field] = counts.get(field, 0) + 1

    ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    return {
        "fields": [{"field": field, "count": count} for field, count in ranked],
    }
