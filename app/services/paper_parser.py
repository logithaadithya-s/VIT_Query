import re

SECTION_ALIASES = {
    "Abstract": ["Abstract"],
    "Introduction": ["Introduction", "Intro"],
    "Literature Review": ["Literature Review", "Related Work", "Background"],
    "Methodology": ["Methodology", "Methods", "Research Methodology"],
    "Results": ["Results", "Findings", "Experimental Results"],
    "Discussion": ["Discussion"],
    "Conclusion": ["Conclusion", "Conclusions", "Summary"],
    "References": ["References", "Bibliography"],
}


def normalize_heading(heading: str) -> str:
    heading = heading.lower()
    heading = re.sub(
        r"^(?:[ivxlcdm]+\.\s*|\d+\.?\s*)",
        "",
        heading,
        flags=re.IGNORECASE,
    )
    return heading.strip()


def extract_sections(text: str, aliases: dict | None = None) -> dict[str, str]:
    aliases = aliases or SECTION_ALIASES
    heading_map = {}

    for canonical, variants in aliases.items():
        for variant in variants:
            heading_map[variant.lower()] = canonical

    pattern = re.compile(
        r"(?im)^(?:[IVXLCDM]+\.\s*|\d+\.?\s*)?[A-Za-z][A-Za-z\s\-&]{0,50}$"
    )
    matches = list(pattern.finditer(text))
    sections = {}

    for i, match in enumerate(matches):
        heading_text = match.group().strip()
        normalized = normalize_heading(heading_text)

        canonical = None
        for alias, canon in heading_map.items():
            if normalized == alias.lower():
                canonical = canon
                break

        if canonical is None:
            continue

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[canonical] = text[start:end].strip()

    return sections


def calculate_format_score(found_sections: dict, expected_sections: list) -> float:
    found_count = len(found_sections)
    total = len(expected_sections)
    return round((found_count / total) * 100, 2) if total else 0.0


def analyze_paper_structure(text: str) -> dict:
    extracted = extract_sections(text, SECTION_ALIASES)
    expected = list(SECTION_ALIASES.keys())
    missing = [section for section in expected if section not in extracted]
    score = calculate_format_score(extracted, expected)

    return {
        "sections": extracted,
        "missing_sections": missing,
        "format_score": score,
        "found_section_names": list(extracted.keys()),
    }
