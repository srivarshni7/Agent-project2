from typing import TypedDict


class ClinicalState(TypedDict, total=False):
    document_text: str
    summary: str
    coding_suggestions: list[str]
    final_response: str