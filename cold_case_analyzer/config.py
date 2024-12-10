import os
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_CD_TABLE = os.getenv('AIRTABLE_CD_TABLE')
AIRTABLE_CONCEPTS_TABLE = os.getenv('AIRTABLE_CONCEPTS_TABLE')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLAMA_API_KEY = os.getenv('LLAMA_API_KEY')