"""Seed the database with sample research papers for demo and testing."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Base, SessionLocal, UPLOADS_DIR, engine
from app.models import ResearchPaper
from app.services.field_analyzer import classify_fields

SAMPLE_PAPERS = [
    {
        "title": "Deep Learning for Medical Image Classification",
        "author": "Dr. Priya Sharma",
        "department": "Computer Science",
        "publication_year": 2024,
        "text": """
Abstract
This paper presents a convolutional neural network approach for classifying medical images with high accuracy.

1. Introduction
Medical image classification using machine learning has gained significant attention in healthcare research.

2. Literature Review
Several studies have applied deep learning to radiology and pathology image analysis.

3. Methodology
We trained a ResNet model on a dataset of 10,000 labeled medical scans using transfer learning.

4. Results
The model achieved 94% accuracy on the test set, outperforming traditional methods.

5. Conclusion
Deep learning shows strong potential for automated medical diagnosis support systems.

References
[1] Smith et al., Journal of Medical AI, 2023.
""",
    },
    {
        "title": "IoT-Based Smart Agriculture Monitoring System",
        "author": "Prof. Rajesh Kumar",
        "department": "Electronics & Communication",
        "publication_year": 2023,
        "text": """
Abstract
An IoT-enabled precision farming system for real-time crop and soil monitoring is proposed.

1. Introduction
Smart agriculture leverages sensors and wireless communication to optimize crop yields.

2. Literature Review
Existing agritech solutions focus on irrigation automation and drone-based monitoring.

3. Methodology
Soil moisture, temperature, and humidity sensors transmit data to a cloud dashboard via LoRaWAN.

4. Results
Field trials showed 18% water savings and improved crop health indicators.

5. Conclusion
IoT-based monitoring is cost-effective for small and medium farms.

References
[1] AgriTech Review, 2022.
""",
    },
    {
        "title": "Blockchain for Secure Academic Credential Verification",
        "author": "Dr. Ananya Reddy",
        "department": "Information Technology",
        "publication_year": 2025,
        "text": """
Abstract
A blockchain-based system for tamper-proof verification of academic degrees and certificates.

1. Introduction
Credential fraud is a growing concern in higher education and recruitment.

2. Literature Review
Distributed ledger technology offers immutable record-keeping for academic institutions.

3. Methodology
We implemented a permissioned blockchain with smart contracts for issuing and verifying credentials.

4. Results
Verification time reduced from days to seconds with zero false positives in testing.

5. Conclusion
Blockchain provides a scalable solution for academic credential management.

References
[1] IEEE Blockchain Standards, 2024.
""",
    },
    {
        "title": "Renewable Energy Integration in Rural Microgrids",
        "author": "Dr. Meena Iyer",
        "department": "Electrical Engineering",
        "publication_year": 2022,
        "text": """
Abstract
This study analyzes solar and wind energy integration for rural microgrid systems.

1. Introduction
Rural communities face unreliable grid access; renewable microgrids offer a sustainable alternative.

2. Literature Review
Prior work examines solar PV sizing and battery storage for off-grid applications.

3. Methodology
We simulated a hybrid solar-wind microgrid using HOMER Pro for three village profiles.

4. Results
Hybrid systems achieved 99.2% reliability with 30% lower cost than diesel-only backup.

5. Conclusion
Renewable microgrids are viable for rural electrification in developing regions.

References
[1] Renewable Energy Journal, 2021.
""",
    },
    {
        "title": "NLP Techniques for Automated Essay Grading in Higher Education",
        "author": "Prof. Vikram Patel",
        "department": "Computer Science",
        "publication_year": 2024,
        "text": """
Abstract
Natural language processing methods for automated assessment of student essays in e-learning platforms.

1. Introduction
E-learning growth demands scalable, consistent essay evaluation tools.

2. Literature Review
Transformer-based models have shown promise in educational assessment and personalized learning.

3. Methodology
We fine-tuned a BERT model on 5,000 instructor-graded essays across multiple subjects.

4. Results
The system achieved 0.87 correlation with human graders on coherence and content scores.

5. Conclusion
NLP-based grading can support faculty while maintaining fair assessment standards.

References
[1] AI in Education, 2023.
""",
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    existing = db.query(ResearchPaper).count()

    if existing > 0:
        print(f"Database already has {existing} papers. Skipping seed.")
        db.close()
        return

    for index, sample in enumerate(SAMPLE_PAPERS, start=1):
        filename = f"sample_{index}.txt"
        file_path = UPLOADS_DIR / filename
        file_path.write_text(sample["text"].strip(), encoding="utf-8")

        fields = classify_fields(sample["text"])

        paper = ResearchPaper(
            title=sample["title"],
            author=sample["author"],
            department=sample["department"],
            publication_year=sample["publication_year"],
            filename=filename,
            file_path=str(file_path),
            file_type="txt",
            extracted_text=sample["text"].strip(),
            primary_field=fields["primary_field"],
            secondary_fields=json.dumps(fields["secondary_fields"]),
            keywords=json.dumps(fields["keywords"]),
            format_score=None,
            word_count=len(sample["text"].split()),
        )
        db.add(paper)

    db.commit()
    db.close()
    print(f"Seeded {len(SAMPLE_PAPERS)} sample papers.")


if __name__ == "__main__":
    seed()
