from pathlib import Path

from hybrid_rag.ingestion.document_classifier import classifier

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
file_path = FIXTURES / "Convocation_scolaire_arabe.pdf"


def test_classifier():
    labels = classifier(file_path)
    print(labels)

    assert len(labels) > 0
    if "scanned" in labels:
        print("PDF contains scanned pages!")
    else:
        print("PDF is text-based!")