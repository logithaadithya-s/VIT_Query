# Research Paper Intelligence Platform

A **Streamlit** web app for college staff to upload, store, and analyze research papers. It detects plagiarism, classifies research fields, and highlights under-explored areas with scope for new work.

## Features

- **Paper upload & storage** — PDF, DOCX, and TXT with metadata
- **Plagiarism detection** — Compare against all stored papers; blocks 70%+ duplicates
- **Field classification** — Auto-detects primary research domain
- **Analytics dashboard** — Charts for field distribution, gaps, keywords, departments
- **Paper structure check** — Validates standard sections (Abstract, Methodology, etc.)

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed sample papers (optional)
python seed_data.py

# 4. Run the app
python main.py
```

Open the URL printed in your terminal (default: **http://localhost:8501**).

If port 8501 is busy, `main.py` automatically picks the next free port (8502, 8503, etc.).

Or run Streamlit directly:

```bash
streamlit run streamlit_app.py
```

## App Pages

| Page | Description |
|------|-------------|
| **Dashboard** | Overview metrics, top fields, research opportunities |
| **Upload Paper** | Upload with author/department metadata; auto-analysis |
| **Plagiarism Check** | Test a file without saving it |
| **All Papers** | Browse and delete stored papers |
| **Field Analytics** | Pie charts, under-explored fields, trending keywords |

## Project Structure

```
├── streamlit_app.py       # Main UI (Streamlit)
├── app/
│   ├── services/
│   │   ├── paper_manager.py   # Upload & delete logic
│   │   ├── plagiarism.py      # Similarity detection
│   │   ├── field_analyzer.py  # Field & gap analysis
│   │   ├── paper_parser.py    # Section extraction
│   │   └── text_extractor.py  # PDF/DOCX/TXT parsing
│   ├── database.py
│   └── models.py
├── data/                  # SQLite DB + uploads
├── seed_data.py
└── main.py
```

## Tech Stack

- **UI:** Streamlit, Plotly, Pandas
- **Backend:** Python, SQLAlchemy, SQLite
- **ML/NLP:** scikit-learn (TF-IDF, cosine similarity)
- **Documents:** pdfplumber, python-docx

## Legacy API (optional)

The FastAPI backend is still available if needed:

```bash
uvicorn app.main:app --reload --port 8000
```

The Streamlit app is the recommended interface.
