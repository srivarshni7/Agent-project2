from unittest.mock import patch

from app.agent import (
    document_node,
    summary_node,
    coding_node,
    supervisor_node,
)


def test_document_node():
    result = document_node({
        "file_name": "sample_clinical_report.txt"
    })

    assert "document_text" in result
    assert "pneumonia" in result["document_text"].lower()


def test_document_node_contains_fever():
    result = document_node({
        "file_name": "sample_clinical_report.txt"
    })

    assert "fever" in result["document_text"].lower()


def test_document_node_contains_cough():
    result = document_node({
        "file_name": "sample_clinical_report.txt"
    })

    assert "cough" in result["document_text"].lower()


@patch("app.agent.summarize_document")
def test_summary_node(mock_summary):
    mock_summary.return_value = "Patient has pneumonia and fever."

    result = summary_node({
        "document_text": "Patient has pneumonia and fever."
    })

    assert result["summary"] == "Patient has pneumonia and fever."
    mock_summary.assert_called_once()


@patch("app.agent.summarize_document")
def test_summary_node_calls_specialist(mock_summary):
    mock_summary.return_value = "Clinical summary"

    summary_node({
        "document_text": "Clinical document"
    })

    mock_summary.assert_called_once_with("Clinical document")


def test_coding_node():
    result = coding_node({
        "document_text": "Patient has pneumonia, fever and cough."
    })

    assert "coding_suggestions" in result
    assert len(result["coding_suggestions"]) == 3


def test_coding_node_pneumonia():
    result = coding_node({
        "document_text": "Physician documents pneumonia."
    })

    assert "J18.9 - Pneumonia, unspecified organism" in result[
        "coding_suggestions"
    ]


@patch("app.agent.save_clinical_document")
def test_supervisor_node(mock_save):
    state = {
        "file_name": "test.txt",
        "document_text": "Patient has pneumonia.",
        "summary": "Patient has pneumonia.",
        "coding_suggestions": [
            "J18.9 - Pneumonia, unspecified organism"
        ],
    }

    result = supervisor_node(state)

    assert "final_response" in result
    assert "CLINICAL DOCUMENT ASSISTANT" in result["final_response"]
    assert "J18.9" in result["final_response"]


@patch("app.agent.save_clinical_document")
def test_supervisor_saves_document(mock_save):
    state = {
        "file_name": "test.txt",
        "document_text": "Patient has pneumonia.",
        "summary": "Patient has pneumonia.",
        "coding_suggestions": [
            "J18.9 - Pneumonia, unspecified organism"
        ],
    }

    supervisor_node(state)

    mock_save.assert_called_once_with(
        "test.txt",
        "Patient has pneumonia.",
        "Patient has pneumonia.",
        ["J18.9 - Pneumonia, unspecified organism"],
    )


@patch("app.agent.save_clinical_document")
def test_supervisor_contains_warning(mock_save):
    state = {
        "file_name": "test.txt",
        "document_text": "Patient has fever.",
        "summary": "Patient has fever.",
        "coding_suggestions": [
            "R50.9 - Fever, unspecified"
        ],
    }

    result = supervisor_node(state)

    assert "verified by a qualified professional" in result[
        "final_response"
    ]


@patch("app.agent.save_clinical_document")
def test_supervisor_contains_summary(mock_save):
    state = {
        "file_name": "test.txt",
        "document_text": "Patient has cough.",
        "summary": "Patient presents with cough.",
        "coding_suggestions": [
            "R05.9 - Cough, unspecified"
        ],
    }

    result = supervisor_node(state)

    assert "Patient presents with cough." in result["final_response"]
