from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base


class ResearchPaper(Base):
    __tablename__ = "research_papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    author = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    publication_year = Column(Integer, nullable=True)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(20), nullable=False)
    extracted_text = Column(Text, nullable=False)
    primary_field = Column(String(255), nullable=True)
    secondary_fields = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    format_score = Column(Float, nullable=True)
    word_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
