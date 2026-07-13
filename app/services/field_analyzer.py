import json
import re
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer


RESEARCH_FIELDS = {
    "Artificial Intelligence & Machine Learning": [
        "machine learning", "deep learning", "neural network", "artificial intelligence",
        "nlp", "natural language", "computer vision", "transformer", "llm", "classification",
    ],
    "Data Science & Analytics": [
        "data science", "big data", "analytics", "data mining", "predictive", "statistics",
        "visualization", "dataset", "regression", "clustering",
    ],
    "Cybersecurity & Networks": [
        "cybersecurity", "encryption", "network security", "blockchain", "intrusion",
        "firewall", "malware", "authentication", "iot security",
    ],
    "Software Engineering": [
        "software engineering", "agile", "microservices", "api", "software development",
        "testing", "devops", "cloud computing", "web application",
    ],
    "Electronics & Communication": [
        "electronics", "vlsi", "embedded", "signal processing", "wireless", "antenna",
        "communication", "semiconductor", "fpga", "microcontroller",
    ],
    "Mechanical Engineering": [
        "mechanical", "thermodynamics", "fluid mechanics", "manufacturing", "cad",
        "robotics", "automation", "materials", "tribology",
    ],
    "Civil Engineering": [
        "civil engineering", "structural", "concrete", "geotechnical", "construction",
        "infrastructure", "bridge", "transportation", "surveying",
    ],
    "Biotechnology & Life Sciences": [
        "biotechnology", "genomics", "protein", "microbiology", "bioinformatics",
        "pharmaceutical", "biomedical", "crispr", "cell culture",
    ],
    "Healthcare & Medicine": [
        "healthcare", "medical", "clinical", "diagnosis", "patient", "disease",
        "hospital", "treatment", "public health", "epidemiology",
    ],
    "Renewable Energy & Environment": [
        "renewable energy", "solar", "wind energy", "sustainability", "climate",
        "environmental", "carbon", "pollution", "green energy", "ecology",
    ],
    "Management & Business": [
        "management", "business", "marketing", "finance", "entrepreneurship",
        "supply chain", "human resource", "organizational", "strategy",
    ],
    "Education & Pedagogy": [
        "education", "teaching", "learning", "pedagogy", "curriculum", "student",
        "e-learning", "assessment", "higher education",
    ],
    "Mathematics & Physics": [
        "mathematics", "physics", "quantum", "algebra", "calculus", "theorem",
        "optics", "mechanics", "numerical", "differential",
    ],
    "Social Sciences & Humanities": [
        "sociology", "psychology", "anthropology", "policy", "governance",
        "social", "humanities", "culture", "ethics", "gender studies",
    ],
}

EMERGING_OPPORTUNITY_FIELDS = {
    "Quantum Computing Applications": [
        "quantum computing", "qubit", "quantum algorithm", "quantum machine learning",
    ],
    "Edge AI & TinyML": [
        "edge ai", "tinyml", "edge computing", "on-device", "federated learning",
    ],
    "Digital Twin Technology": [
        "digital twin", "simulation model", "cyber-physical", "smart manufacturing",
    ],
    "Green Hydrogen & Clean Tech": [
        "green hydrogen", "electrolysis", "clean technology", "carbon capture",
    ],
    "Generative AI in Education": [
        "generative ai", "chatgpt", "ai tutor", "personalized learning", "llm education",
    ],
    "Space Technology & Satellites": [
        "satellite", "aerospace", "space technology", "remote sensing", "orbital",
    ],
    "Mental Health Tech": [
        "mental health", "wellbeing", "teletherapy", "digital therapeutics",
    ],
    "AgriTech & Precision Farming": [
        "agritech", "precision farming", "smart agriculture", "crop monitoring", "drone farming",
    ],
}


def _tokenize_keywords(text: str, top_n: int = 12) -> list[str]:
    vectorizer = TfidfVectorizer(
        max_features=top_n,
        stop_words="english",
        ngram_range=(1, 2),
    )
    try:
        matrix = vectorizer.fit_transform([text])
        features = vectorizer.get_feature_names_out()
        scores = matrix.toarray()[0]
        ranked = sorted(zip(features, scores), key=lambda item: item[1], reverse=True)
        return [keyword for keyword, score in ranked if score > 0]
    except ValueError:
        return []


def classify_fields(text: str) -> dict:
    lowered = text.lower()
    scores = {}

    for field, keywords in RESEARCH_FIELDS.items():
        score = sum(1 for keyword in keywords if keyword in lowered)
        if score:
            scores[field] = score

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    primary_field = ranked[0][0] if ranked else "General / Interdisciplinary"
    secondary_fields = [field for field, _ in ranked[1:4]]

    keywords = _tokenize_keywords(text)

    return {
        "primary_field": primary_field,
        "secondary_fields": secondary_fields,
        "keywords": keywords,
        "field_scores": dict(ranked),
    }


def analyze_field_landscape(papers: list[dict]) -> dict:
    field_counts = Counter()
    keyword_counter = Counter()
    year_by_field: dict[str, Counter] = {}
    department_by_field: dict[str, Counter] = {}

    for paper in papers:
        field = paper.get("primary_field") or "Unclassified"
        field_counts[field] += 1

        keywords = paper.get("keywords") or []
        if isinstance(keywords, str):
            try:
                keywords = json.loads(keywords)
            except json.JSONDecodeError:
                keywords = [keywords]

        keyword_counter.update(keywords)

        year = paper.get("publication_year")
        if year:
            year_by_field.setdefault(field, Counter())[year] += 1

        department = paper.get("department")
        if department:
            department_by_field.setdefault(field, Counter())[department] += 1

    all_fields = list(RESEARCH_FIELDS.keys())
    field_distribution = [
        {"field": field, "count": field_counts.get(field, 0)}
        for field in all_fields
    ]
    field_distribution.sort(key=lambda item: item["count"], reverse=True)

    avg_count = sum(field_counts.values()) / max(len(all_fields), 1)
    underexplored = [
        {
            "field": field,
            "count": field_counts.get(field, 0),
            "scope_note": _scope_note(field, field_counts.get(field, 0), avg_count),
        }
        for field in all_fields
        if field_counts.get(field, 0) <= max(1, avg_count * 0.35)
    ]
    underexplored.sort(key=lambda item: item["count"])

    opportunity_fields = _detect_opportunity_fields(papers, field_counts)
    trending_keywords = keyword_counter.most_common(15)
    top_fields = field_distribution[:8]

    return {
        "total_papers": len(papers),
        "field_distribution": field_distribution,
        "top_researched_fields": top_fields,
        "underexplored_fields": underexplored,
        "opportunity_fields": opportunity_fields,
        "trending_keywords": [
            {"keyword": keyword, "count": count}
            for keyword, count in trending_keywords
        ],
        "papers_by_year": _aggregate_years(papers),
        "department_activity": _aggregate_departments(papers),
    }


def _scope_note(field: str, count: int, avg_count: float) -> str:
    if count == 0:
        return f"No papers yet in {field}. High potential for pioneering research."
    if count <= 1:
        return f"Only {count} paper(s) in {field}. Room for deeper exploration and new directions."
    return f"Below average activity ({count} papers vs ~{avg_count:.1f} average). Good scope for expansion."


def _detect_opportunity_fields(papers: list[dict], field_counts: Counter) -> list[dict]:
    opportunities = []
    corpus = " ".join(paper.get("extracted_text", "") for paper in papers).lower()

    for field, keywords in EMERGING_OPPORTUNITY_FIELDS.items():
        keyword_hits = sum(1 for keyword in keywords if keyword in corpus)
        existing_in_primary = sum(1 for paper in papers if paper.get("primary_field") == field)

        if keyword_hits >= 2 and existing_in_primary == 0:
            opportunities.append(
                {
                    "field": field,
                    "signal_strength": "high",
                    "reason": "Emerging keywords appear in the corpus but no dedicated papers yet.",
                    "suggested_action": f"Consider focused research in {field}.",
                }
            )
        elif keyword_hits >= 1 and existing_in_primary <= 1:
            opportunities.append(
                {
                    "field": field,
                    "signal_strength": "medium",
                    "reason": "Early signals detected with limited dedicated coverage.",
                    "suggested_action": f"Explore interdisciplinary work connecting existing papers to {field}.",
                }
            )

    low_activity_main_fields = [
        field
        for field in RESEARCH_FIELDS
        if field_counts.get(field, 0) <= 1
    ]

    for field in low_activity_main_fields[:5]:
        opportunities.append(
            {
                "field": field,
                "signal_strength": "institutional_gap",
                "reason": f"Core domain '{field}' has minimal representation in the repository.",
                "suggested_action": f"Encourage faculty/students to submit work in {field}.",
            }
        )

    return opportunities[:12]


def _aggregate_years(papers: list[dict]) -> list[dict]:
    counter = Counter(paper.get("publication_year") for paper in papers if paper.get("publication_year"))
    return [{"year": year, "count": count} for year, count in sorted(counter.items())]


def _aggregate_departments(papers: list[dict]) -> list[dict]:
    counter = Counter(paper.get("department") for paper in papers if paper.get("department"))
    return [
        {"department": department, "count": count}
        for department, count in counter.most_common(10)
    ]
