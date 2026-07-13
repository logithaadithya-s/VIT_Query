from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import analytics, papers

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Research Paper Intelligence API",
    description="Backend API for paper upload, plagiarism detection, and research field analytics.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router)
app.include_router(analytics.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
