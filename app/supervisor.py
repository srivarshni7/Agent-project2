from app.specialists import summarize_document, coding_specialist


def supervisor(document_text: str) -> dict:
    """
    Supervisor coordinates the clinical document specialists.
    """

    summary = summarize_document(document_text)

    coding_suggestions = coding_specialist(document_text)

    final_response = f"""
=== CLINICAL DOCUMENT ASSISTANT ===

DOCUMENT SUMMARY
----------------
{summary}

CODING SUGGESTIONS
------------------
"""

    for code in coding_suggestions:
        final_response += f"- {code}\n"

    final_response += """
    
Note: Coding suggestions are for review and should be verified by a qualified professional.
"""

    return {
        "summary": summary,
        "coding_suggestions": coding_suggestions,
        "final_response": final_response,
    }