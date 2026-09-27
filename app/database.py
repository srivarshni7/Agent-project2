import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY is missing in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_clinical_document(file_name, document_text, summary, coding_suggestions):
    data = {
        "file_name": file_name,
        "document_text": document_text,
        "summary": summary,
        "coding_suggestions": coding_suggestions,
    }

    response = (
        supabase
        .table("clinical_documents")
        .insert(data)
        .execute()
    )

    return response.data


def get_clinical_documents():
    response = (
        supabase
        .table("clinical_documents")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data
