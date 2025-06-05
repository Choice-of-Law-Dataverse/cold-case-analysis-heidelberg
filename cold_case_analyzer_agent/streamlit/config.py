import os
from dotenv import load_dotenv
import uuid
from langchain_openai import ChatOpenAI
import json

load_dotenv()

def get_llm(model: str | None = None):
    """
    Return a ChatOpenAI instance. If `model` is provided, use it; otherwise fallback to env var or default.
    """
    selected = model or os.getenv("OPENAI_MODEL") or "gpt-4.1-nano"
    return ChatOpenAI(model=selected)

# default llm instance
llm = get_llm()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_CONCEPTS_TABLE = os.getenv("AIRTABLE_CONCEPTS_TABLE")

SQL_CONN_STRING = os.getenv("SQL_CONN_STRING")
# Load user credentials (as JSON string in .env): e.g. USER_CREDENTIALS='{"alice":"wonderland","bob":"builder"}'
USER_CREDENTIALS = json.loads(os.getenv("USER_CREDENTIALS", "{}"))

thread_id = str(uuid.uuid4())
#print(f"Thread ID: {thread_id}")
