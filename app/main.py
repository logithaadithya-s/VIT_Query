from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import Base, engine
from app.routers import analytics, papers

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Research Paper Intelligence Platform",
    description="Upload, store, detect plagiarism, and analyze research field trends for college staff.",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(papers.router)
app.include_router(analytics.router)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    return {"status": "ok"}
