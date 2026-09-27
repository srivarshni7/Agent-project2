from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.tools import read_clinical_document, suggest_icd_code


def test_read_txt_document():
    text = read_clinical_document("sample_clinical_report.txt")
    assert "pneumonia" in text.lower()


def test_read_txt_contains_fever():
    text = read_clinical_document("sample_clinical_report.txt")
    assert "fever" in text.lower()


def test_read_txt_contains_cough():
    text = read_clinical_document("sample_clinical_report.txt")
    assert "cough" in text.lower()


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        read_clinical_document("missing_file.txt")


def test_unsupported_file_type(tmp_path):
    file = tmp_path / "report.docx"
    file.write_text("clinical data")

    with pytest.raises(ValueError):
        read_clinical_document(str(file))


def test_empty_txt_file(tmp_path):
    file = tmp_path / "empty.txt"
    file.write_text("")

    assert read_clinical_document(str(file)) == ""


@patch("app.tools.PdfReader")
def test_read_pdf_document(mock_reader, tmp_path):
    file = tmp_path / "report.pdf"
    file.write_text("fake pdf")

    page = MagicMock()
    page.extract_text.return_value = "Patient has pneumonia."

    mock_reader.return_value.pages = [page]

    result = read_clinical_document(str(file))

    assert "pneumonia" in result.lower()


@patch("app.tools.PdfReader")
def test_read_pdf_multiple_pages(mock_reader, tmp_path):
    file = tmp_path / "report.pdf"
    file.write_text("fake pdf")

    page1 = MagicMock()
    page1.extract_text.return_value = "Fever present."

    page2 = MagicMock()
    page2.extract_text.return_value = "Pneumonia documented."

    mock_reader.return_value.pages = [page1, page2]

    result = read_clinical_document(str(file))

    assert "fever" in result.lower()
    assert "pneumonia" in result.lower()


def test_pneumonia_code():
    codes = suggest_icd_code("Patient has pneumonia.")

    assert "J18.9 - Pneumonia, unspecified organism" in codes


def test_fever_code():
    codes = suggest_icd_code("Patient has fever.")

    assert "R50.9 - Fever, unspecified" in codes


def test_cough_code():
    codes = suggest_icd_code("Patient has cough.")

    assert "R05.9 - Cough, unspecified" in codes


def test_multiple_codes():
    text = "Patient has pneumonia with fever and cough."

    codes = suggest_icd_code(text)

    assert len(codes) == 3
    assert "J18.9 - Pneumonia, unspecified organism" in codes
    assert "R50.9 - Fever, unspecified" in codes
    assert "R05.9 - Cough, unspecified" in codes


def test_no_matching_code():
    codes = suggest_icd_code("Patient has headache.")

    assert codes == ["No matching coding suggestion found."]
