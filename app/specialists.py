import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.tools import suggest_icd_code

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)


def summarize_document(document_text: str) -> str:
    prompt = f"""
You are a Clinical Document Summarization Specialist.

Summarize the following clinical document clearly.

Include:
1. Main symptoms
2. Important clinical findings
3. Tests or observations
4. Physician-documented condition
5. Treatment mentioned

Do not invent information that is not present in the document.

Clinical document:
{document_text}
"""

    response = llm.invoke(prompt)
    return response.content


def coding_specialist(document_text: str) -> list[str]:
    """
    Generate coding suggestions using the coding tool.
    These are suggestions for review, not final medical coding decisions.
    """
    return suggest_icd_code(document_text)