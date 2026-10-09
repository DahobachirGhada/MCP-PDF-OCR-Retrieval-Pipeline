from pathlib import Path

from hybrid_rag.ingestion.document_classifier import classifier

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
file_path = FIXTURES / "Convocation_scolaire_arabe.pdf"


def test_classifier():
    classifier_result = classifier(file_path)
    if 0 in classifier_result:
        print("PDF is image-based!")
    else:
        print("PDF is text-based!")