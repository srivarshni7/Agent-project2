import sys
from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.tools import read_clinical_document, suggest_icd_code
from app.specialists import summarize_document
from app.database import save_clinical_document


class ClinicalState(TypedDict, total=False):
    file_name: str
    document_text: str
    summary: str
    coding_suggestions: list[str]
    final_response: str


def document_node(state: ClinicalState):
    file_path = state["file_name"]

    return {
        "document_text": read_clinical_document(file_path)
    }


def summary_node(state: ClinicalState):
    return {
        "summary": summarize_document(
            state["document_text"]
        )
    }


def coding_node(state: ClinicalState):
    return {
        "coding_suggestions": suggest_icd_code(
            state["document_text"]
        )
    }


def supervisor_node(state: ClinicalState):
    final_response = f"""
=== CLINICAL DOCUMENT ASSISTANT ===

DOCUMENT SUMMARY
----------------
{state["summary"]}

CODING SUGGESTIONS
------------------
"""

    for code in state["coding_suggestions"]:
        final_response += f"- {code}\n"

    final_response += """
    
Note: Coding suggestions are for review and should be verified by a qualified professional.
"""

    save_clinical_document(
        state["file_name"],
        state["document_text"],
        state["summary"],
        state["coding_suggestions"],
    )

    return {
        "final_response": final_response
    }


workflow = StateGraph(ClinicalState)

workflow.add_node("document_reader", document_node)
workflow.add_node("summary_specialist", summary_node)
workflow.add_node("coding_specialist", coding_node)
workflow.add_node("supervisor", supervisor_node)

workflow.set_entry_point("document_reader")

workflow.add_edge("document_reader", "summary_specialist")
workflow.add_edge("summary_specialist", "coding_specialist")
workflow.add_edge("coding_specialist", "supervisor")
workflow.add_edge("supervisor", END)

app = workflow.compile()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.agent <clinical_file>")
        print("Example: python -m app.agent sample_clinical_report.txt")
        sys.exit(1)

    file_path = sys.argv[1]

    result = app.invoke({
        "file_name": file_path
    })

    print(result["final_response"])
    print("\nDocument saved to Supabase successfully.")
