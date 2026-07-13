import re

# =====================================================
# SECTION DEFINITIONS
# =====================================================

SECTION_ALIASES = {
    "Abstract": [
        "Abstract"
    ],
    "Introduction": [
        "Introduction",
        "Intro"
    ],
    "Literature Review": [
        "Literature Review",
        "Related Work",
        "Background"
    ],
    "Methodology": [
        "Methodology",
        "Methods",
        "Research Methodology"
    ],
    "Results": [
        "Results",
        "Findings",
        "Experimental Results"
    ],
    "Discussion": [
        "Discussion"
    ],
    "Conclusion": [
        "Conclusion",
        "Conclusions",
        "Summary"
    ],
    "References": [
        "References",
        "Bibliography"
    ]
}


# =====================================================
# NORMALIZE HEADING
# =====================================================

def normalize_heading(heading):
    heading = heading.lower()

    # Remove numbering
    heading = re.sub(
        r'^(?:[ivxlcdm]+\.\s*|\d+\.?\s*)',
        '',
        heading,
        flags=re.IGNORECASE
    )

    return heading.strip()


# =====================================================
# EXTRACT SECTIONS
# =====================================================

def extract_sections(text, aliases):

    heading_map = {}

    # Create alias → canonical mapping
    for canonical, variants in aliases.items():
        for variant in variants:
            heading_map[variant.lower()] = canonical

    # Regex for headings
    pattern = re.compile(
        r'(?im)^(?:[IVXLCDM]+\.\s*|\d+\.?\s*)?[A-Za-z][A-Za-z\s\-&]{0,50}$'
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

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        content = text[start:end].strip()

        sections[canonical] = content

    return sections


# =====================================================
# SCORE CALCULATION
# =====================================================

def calculate_score(found_sections, expected_sections):

    found_count = len(found_sections)
    total = len(expected_sections)

    score = (found_count / total) * 100

    return round(score, 2)


# =====================================================
# MAIN ANALYSIS FUNCTION
# =====================================================

def analyze_paper(text):

    extracted = extract_sections(
        text,
        SECTION_ALIASES
    )

    expected = list(SECTION_ALIASES.keys())

    missing = [
        section
        for section in expected
        if section not in extracted
    ]

    score = calculate_score(
        extracted,
        expected
    )

    print("\n" + "=" * 60)
    print("RESEARCH PAPER ANALYSIS")
    print("=" * 60)

    print(f"\nFormat Score: {score}%")

    print("\nFound Sections:")
    for sec in extracted:
        print(f"✓ {sec}")

    print("\nMissing Sections:")
    if missing:
        for sec in missing:
            print(f"✗ {sec}")
    else:
        print("None")

    print("\n" + "=" * 60)
    print("EXTRACTED CONTENT")
    print("=" * 60)

    for section, content in extracted.items():

        print(f"\n[{section}]")
        print("-" * 40)

        preview = content[:500]

        if len(content) > 500:
            preview += "\n..."

        print(preview)


# =====================================================
# SAMPLE RESEARCH PAPER
# =====================================================

sample_paper = """
Abstract
This paper explores machine learning techniques.

1. Introduction
Machine learning is becoming increasingly important.

2. Literature Review
Several studies have explored this topic.

3. Methodology
A neural network was trained using historical data.

4. Results
The model achieved 95% accuracy.

5. Conclusion
The proposed approach performed well.

References
[1] Author et al.
"""

# =====================================================
# RUN
# =====================================================

analyze_paper(sample_paper)