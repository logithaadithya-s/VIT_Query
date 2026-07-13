import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ResearchPaper
from app.services.field_analyzer import analyze_field_landscape
from app.services.research_agent import generate_research_insights, get_agent_integration_suggestions

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _papers_payload(db: Session) -> list[dict]:
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

    return payload


@router.get("/overview")
def analytics_overview(db: Session = Depends(get_db)):
    payload = _papers_payload(db)
    landscape = analyze_field_landscape(payload)

    return {
        **landscape,
        "summary": {
            "total_papers": len(payload),
            "unique_fields": len({p["primary_field"] for p in payload if p.get("primary_field")}),
            "departments_represented": len({p["department"] for p in payload if p.get("department")}),
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


@router.get("/agent-insights")
async def agent_insights(db: Session = Depends(get_db)):
    payload = _papers_payload(db)
    insights = await generate_research_insights(payload)
    return insights


@router.get("/agent-suggestions")
def agent_suggestions():
    return {"suggestions": get_agent_integration_suggestions()}
