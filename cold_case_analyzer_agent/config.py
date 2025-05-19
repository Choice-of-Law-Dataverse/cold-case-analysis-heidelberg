import os
from dotenv import load_dotenv
import uuid
from langchain.chat_models import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(model="gpt-4.1-nano")

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_CONCEPTS_TABLE = os.getenv("AIRTABLE_CONCEPTS_TABLE")

thread_id = str(uuid.uuid4())
print(f"Thread ID: {thread_id}")