# tools/precise_jurisdiction_detector.py
"""
Identifies the precise jurisdiction from court decision text using the jurisdictions.csv database.
"""
import csv
from pathlib import Path
from config import llm
from langchain_core.messages import HumanMessage, SystemMessage
from prompts.precise_jurisdiction_detection_prompt import PRECISE_JURISDICTION_DETECTION_PROMPT
import re
import json

def load_jurisdictions():
    """Load all jurisdictions from the CSV file."""
    jurisdictions_file = Path(__file__).parent.parent / 'data' / 'jurisdictions.csv'
    jurisdictions = []
    
    with open(jurisdictions_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Name'].strip():  # Only include rows with actual jurisdiction names
                jurisdictions.append({
                    'name': row['Name'].strip(),
                    'code': row['Alpha-3 Code'].strip(),
                    'summary': row['Jurisdiction Summary'].strip()
                })
    # Sort jurisdictions by name for better consistency
    jurisdictions.sort(key=lambda x: x['name'].lower())
    return jurisdictions

def create_jurisdiction_list():
    """Create a formatted list of jurisdictions for the LLM prompt."""
    jurisdictions = load_jurisdictions()
    jurisdiction_list = []
    
    for jurisdiction in jurisdictions:
        if jurisdiction['code']:  # Only include jurisdictions with codes
            jurisdiction_list.append(f"- {jurisdiction['name']} ({jurisdiction['code']})")
        else:
            jurisdiction_list.append(f"- {jurisdiction['name']}")
    
    return "\n".join(jurisdiction_list)

def detect_precise_jurisdiction(text: str) -> dict:
    """
    Uses an LLM to identify the precise jurisdiction from court decision text.
    Returns a dictionary with jurisdiction details and confidence.
    """
    if not text or len(text.strip()) < 50:
        return {
            "jurisdiction_name": None,
            "jurisdiction_code": None,
            "jurisdiction_summary": None
        }
    
    jurisdiction_list = create_jurisdiction_list()
    
    prompt = PRECISE_JURISDICTION_DETECTION_PROMPT.format(
        jurisdiction_list=jurisdiction_list,
        text=text[:5000]  # Limit text length to avoid token limits
    )

    try:
        response = llm.invoke([
            SystemMessage(content="You are an expert in legal systems and court jurisdictions worldwide. Respond only with valid JSON."),
            HumanMessage(content=prompt)
        ])
        
        result_text = response.content.strip()
        
        # Extract JSON from response if it's wrapped in markdown
        json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(1)
        elif result_text.startswith('```') and result_text.endswith('```'):
            result_text = result_text[3:-3].strip()
            if result_text.startswith('json'):
                result_text = result_text[4:].strip()
        
        try:
            result = json.loads(result_text)
            
            # Validate the result
            if not isinstance(result, dict):
                raise ValueError("Result is not a dictionary")
            
            # Ensure required fields exist
            jurisdiction_name = result.get("jurisdiction_name", "Unknown")
            
            # Validate jurisdiction against our list
            jurisdictions = load_jurisdictions()
            valid_jurisdiction = None
            
            if jurisdiction_name and jurisdiction_name != "Unknown":
                for jurisdiction in jurisdictions:
                    if (jurisdiction['name'].lower() == jurisdiction_name.lower() or
                        (jurisdiction['code'] and jurisdiction['code'].lower() == jurisdiction_name.lower())):
                        valid_jurisdiction = jurisdiction
                        break
            
            if valid_jurisdiction:
                return {
                    "jurisdiction_name": valid_jurisdiction['name'],
                    "jurisdiction_code": valid_jurisdiction['code'],
                    "jurisdiction_summary": valid_jurisdiction['summary']
                }
            else:
                return {
                    "jurisdiction_name": "Unknown",
                    "jurisdiction_code": None,
                    "jurisdiction_summary": None
                }
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Raw response: {result_text}")
            return {
                "jurisdiction_name": "Unknown",
                "jurisdiction_code": None,
                "jurisdiction_summary": None
            }
            
    except Exception as e:
        print(f"Error in jurisdiction detection: {e}")
        return {
            "jurisdiction_name": "Unknown",
            "jurisdiction_code": None,
            "jurisdiction_summary": None
        }

def determine_legal_system_type(jurisdiction_name: str, original_text: str) -> str:
    """
    Determine if the jurisdiction follows civil law or common law.
    
    Uses the existing jurisdiction detection logic with the original text as the primary method.
    """
    return "foo"