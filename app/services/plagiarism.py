import re
from difflib import SequenceMatcher

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _split_into_chunks(text: str, chunk_size: int = 400, overlap: int = 100) -> list[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


def compute_document_similarity(source_text: str, target_text: str) -> float:
    normalized_source = _normalize_text(source_text)
    normalized_target = _normalize_text(target_text)

    if not normalized_source or not normalized_target:
        return 0.0

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=5000,
        stop_words="english",
    )
    matrix = vectorizer.fit_transform([normalized_source, normalized_target])
    similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return round(float(similarity) * 100, 2)


def find_matching_passages(source_text: str, target_text: str, threshold: float = 0.55) -> list[dict]:
    source_chunks = _split_into_chunks(source_text)
    target_chunks = _split_into_chunks(target_text)
    matches = []

    for source_chunk in source_chunks:
        best_ratio = 0.0
        best_target = ""

        for target_chunk in target_chunks:
            ratio = SequenceMatcher(
                None,
                _normalize_text(source_chunk),
                _normalize_text(target_chunk),
            ).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_target = target_chunk

        if best_ratio >= threshold:
            matches.append(
                {
                    "similarity_percent": round(best_ratio * 100, 2),
                    "source_excerpt": source_chunk[:300],
                    "matched_excerpt": best_target[:300],
                }
            )

    matches.sort(key=lambda item: item["similarity_percent"], reverse=True)
    return matches[:5]


def check_plagiarism(
    new_text: str,
    existing_papers: list[dict],
    similarity_threshold: float = 25.0,
) -> dict:
    results = []

    for paper in existing_papers:
        similarity = compute_document_similarity(new_text, paper["extracted_text"])
        if similarity >= similarity_threshold:
            matches = find_matching_passages(new_text, paper["extracted_text"])
            results.append(
                {
                    "paper_id": paper["id"],
                    "title": paper["title"],
                    "author": paper.get("author"),
                    "similarity_percent": similarity,
                    "matching_passages": matches,
                    "is_duplicate": similarity >= 70.0,
                }
            )

    results.sort(key=lambda item: item["similarity_percent"], reverse=True)

    highest = results[0]["similarity_percent"] if results else 0.0
    status = "clear"
    if highest >= 70:
        status = "duplicate_detected"
    elif highest >= 40:
        status = "high_similarity"
    elif highest >= 25:
        status = "moderate_similarity"

    return {
        "status": status,
        "highest_similarity": highest,
        "matches": results,
        "total_matches": len(results),
    }
