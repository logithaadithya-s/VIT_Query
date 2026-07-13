import json

import pandas as pd
import plotly.express as px
import streamlit as st

from app.database import Base, SessionLocal, engine
from app.models import ResearchPaper
from app.services.field_analyzer import analyze_field_landscape
from app.services.paper_manager import (
    check_file_plagiarism,
    delete_paper,
    paper_to_dict,
    process_uploaded_file,
)

Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title="Research Paper Intelligence",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .hero {
        background: linear-gradient(135deg, #1e3a5f 0%, #0f766e 100%);
        padding: 1.5rem 1.75rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        margin: 0 0 0.35rem 0;
        font-size: 1.75rem;
        font-weight: 700;
    }

    .hero p {
        margin: 0;
        opacity: 0.9;
        font-size: 0.95rem;
    }

    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.1rem;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    div[data-testid="stSidebar"] {
        background: #0f172a;
    }

    div[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    div[data-testid="stSidebar"] .stRadio label {
        font-size: 1rem;
        padding: 0.35rem 0;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_db():
    return SessionLocal()


def load_analytics(db):
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
    avg_format = round(sum(p.format_score or 0 for p in papers) / len(papers), 2) if papers else 0.0

    return {
        **landscape,
        "summary": {
            "total_papers": len(papers),
            "unique_fields": len({p.primary_field for p in papers if p.primary_field}),
            "average_format_score": avg_format,
            "departments_represented": len({p.department for p in papers if p.department}),
        },
    }


def render_header():
    st.markdown(
        """
        <div class="hero">
            <h1>📚 Research Paper Intelligence Platform</h1>
            <p>Upload, store, detect plagiarism, and discover research gaps for your institution.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_dashboard(db):
    analytics = load_analytics(db)
    summary = analytics["summary"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Papers", summary["total_papers"])
    c2.metric("Research Fields", summary["unique_fields"])
    c3.metric("Avg Format Score", f"{summary['average_format_score']}%")
    c4.metric("Departments", summary["departments_represented"])

    left, right = st.columns(2)

    with left:
        st.subheader("Most Researched Fields")
        if analytics["top_researched_fields"]:
            df = pd.DataFrame(analytics["top_researched_fields"])
            fig = px.bar(
                df,
                x="count",
                y="field",
                orientation="h",
                color="count",
                color_continuous_scale="Teal",
            )
            fig.update_layout(showlegend=False, height=360, margin=dict(l=10, r=10, t=10, b=10))
            fig.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Upload papers to see field distribution.")

    with right:
        st.subheader("Research Opportunities")
        if analytics["opportunity_fields"]:
            for item in analytics["opportunity_fields"][:6]:
                with st.expander(f"🌱 {item['field']}", expanded=False):
                    st.write(item["reason"])
                    st.caption(item["suggested_action"])
        else:
            st.info("More papers needed to detect emerging opportunities.")


def page_upload(db):
    st.subheader("Upload Research Paper")
    st.caption("Supported: PDF, DOCX, TXT. Uploads with 70%+ similarity to existing papers are blocked.")

    with st.form("upload_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title (optional — auto-detected)")
            author = st.text_input("Author")
        with col2:
            department = st.text_input("Department")
            year = st.number_input("Publication Year", min_value=1990, max_value=2030, value=2025)

        uploaded = st.file_uploader("Choose document", type=["pdf", "docx", "txt"])
        submitted = st.form_submit_button("Upload & Analyze", type="primary", use_container_width=True)

    if submitted:
        if not uploaded:
            st.error("Please select a file to upload.")
            return

        with st.spinner("Extracting text, checking plagiarism, and analyzing fields..."):
            try:
                result = process_uploaded_file(
                    db=db,
                    file_bytes=uploaded.getvalue(),
                    filename=uploaded.name,
                    title=title,
                    author=author,
                    department=department,
                    publication_year=int(year) if year else None,
                )
            except ValueError as exc:
                st.error(str(exc))
                return
            except Exception as exc:
                st.error(f"Upload failed: {exc}")
                return

        if not result["success"]:
            st.error(result["message"])
            if result.get("plagiarism_report", {}).get("matches"):
                st.markdown("**Similar papers found:**")
                for match in result["plagiarism_report"]["matches"]:
                    st.warning(f"**{match['title']}** — {match['similarity_percent']}% similar")
            return

        paper = result["paper"]
        st.success("Paper uploaded and analyzed successfully!")
        st.balloons()

        m1, m2, m3 = st.columns(3)
        m1.metric("Primary Field", paper["primary_field"] or "Unclassified")
        m2.metric("Format Score", f"{result['structure']['format_score']}%")
        m3.metric(
            "Highest Similarity",
            f"{result['plagiarism_report']['highest_similarity']}%",
        )

        if paper["keywords"]:
            st.markdown("**Keywords:** " + ", ".join(paper["keywords"][:8]))

        missing = result["structure"]["missing_sections"]
        if missing:
            st.warning("Missing sections: " + ", ".join(missing))
        else:
            st.info("All standard paper sections detected.")


def page_plagiarism(db):
    st.subheader("Plagiarism Check")
    st.caption("Check a document against all stored papers without saving it.")

    uploaded = st.file_uploader(
        "Upload document to check",
        type=["pdf", "docx", "txt"],
        key="plagiarism_uploader",
    )

    if st.button("Run Plagiarism Check", type="primary", disabled=not uploaded):
        with st.spinner("Analyzing similarity..."):
            try:
                report = check_file_plagiarism(db, uploaded.getvalue(), uploaded.name)
            except ValueError as exc:
                st.error(str(exc))
                return

        if not report["matches"]:
            st.success("No significant similarity found with stored papers.")
            return

        status = report["status"].replace("_", " ").title()
        if report["status"] == "duplicate_detected":
            st.error(f"Status: {status} — {report['highest_similarity']}% max similarity")
        else:
            st.warning(f"Status: {status} — {report['highest_similarity']}% max similarity")

        for match in report["matches"]:
            with st.expander(
                f"{'🔴' if match['is_duplicate'] else '🟡'} {match['title']} — {match['similarity_percent']}%",
                expanded=match["is_duplicate"],
            ):
                if match.get("author"):
                    st.caption(f"Author: {match['author']}")
                for passage in match.get("matching_passages", [])[:3]:
                    st.markdown(f"**{passage['similarity_percent']}% match**")
                    st.text(passage["source_excerpt"][:250] + "...")


def page_papers(db):
    st.subheader("Stored Papers")
    papers = db.query(ResearchPaper).order_by(ResearchPaper.created_at.desc()).all()

    if not papers:
        st.info("No papers uploaded yet. Go to Upload Paper to add one.")
        return

    for paper in papers:
        data = paper_to_dict(paper)
        with st.container(border=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"### {data['title']}")
                meta = f"{data['author'] or 'Unknown'} · {data['department'] or 'No department'} · {data['publication_year'] or 'N/A'}"
                st.caption(meta)
                st.markdown(
                    f"**Field:** {data['primary_field']}  ·  **Format:** {data['format_score']}%  ·  **Words:** {data['word_count']}"
                )
                if data["keywords"]:
                    st.markdown("**Keywords:** " + ", ".join(data["keywords"][:6]))
            with col2:
                if st.button("Delete", key=f"delete_{paper.id}", type="secondary"):
                    delete_paper(db, paper.id)
                    st.rerun()


def page_analytics(db):
    analytics = load_analytics(db)

    tab1, tab2, tab3 = st.tabs(["Field Distribution", "Under-Explored Areas", "Trends"])

    with tab1:
        df = pd.DataFrame(analytics["field_distribution"])
        df = df[df["count"] > 0]
        if not df.empty:
            fig = px.pie(df, values="count", names="field", hole=0.45, color_discrete_sequence=px.colors.sequential.Teal)
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No field data yet.")

    with tab2:
        st.markdown("### Fields with scope for new research")
        for item in analytics["underexplored_fields"]:
            st.markdown(
                f"""
                <div class="metric-card" style="margin-bottom: 0.75rem;">
                    <strong>{item['field']}</strong> — {item['count']} paper(s)<br/>
                    <span style="color:#64748b;">{item['scope_note']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Trending Keywords**")
            if analytics["trending_keywords"]:
                kw_df = pd.DataFrame(analytics["trending_keywords"])
                fig = px.bar(kw_df.head(10), x="count", y="keyword", orientation="h", color="count", color_continuous_scale="Blues")
                fig.update_layout(showlegend=False, height=360, margin=dict(l=10, r=10, t=10, b=10))
                fig.update_yaxes(categoryorder="total ascending")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No keywords yet.")

        with col2:
            st.markdown("**Department Activity**")
            if analytics["department_activity"]:
                dept_df = pd.DataFrame(analytics["department_activity"])
                fig = px.bar(dept_df, x="department", y="count", color="count", color_continuous_scale="Viridis")
                fig.update_layout(showlegend=False, height=360, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No department data yet.")


def main():
    db = get_db()
    try:
        render_header()

        with st.sidebar:
            st.markdown("## Navigation")
            page = st.radio(
                "Go to",
                [
                    "Dashboard",
                    "Upload Paper",
                    "Plagiarism Check",
                    "All Papers",
                    "Field Analytics",
                ],
                label_visibility="collapsed",
            )
            st.divider()
            st.caption("College research repository with plagiarism detection and gap analysis.")

        pages = {
            "Dashboard": page_dashboard,
            "Upload Paper": page_upload,
            "Plagiarism Check": page_plagiarism,
            "All Papers": page_papers,
            "Field Analytics": page_analytics,
        }
        pages[page](db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
