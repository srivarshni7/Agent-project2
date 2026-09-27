from pathlib import Path
from pypdf import PdfReader


def read_clinical_document(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text.strip()

    raise ValueError("Only .txt and .pdf files are supported.")


def suggest_icd_code(document_text: str) -> list[str]:
    text = document_text.lower()

    suggestions = []

    if "pneumonia" in text:
        suggestions.append("J18.9 - Pneumonia, unspecified organism")

    if "fever" in text:
        suggestions.append("R50.9 - Fever, unspecified")

    if "cough" in text:
        suggestions.append("R05.9 - Cough, unspecified")

    if not suggestions:
        suggestions.append("No matching coding suggestion found.")

    return suggestions