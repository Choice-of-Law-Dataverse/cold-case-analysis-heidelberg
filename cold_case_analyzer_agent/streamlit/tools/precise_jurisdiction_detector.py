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
            "confidence": "low",
            "reasoning": "Insufficient text provided"
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
            jurisdiction_code = result.get("jurisdiction_code")
            confidence = result.get("confidence", "low")
            reasoning = result.get("reasoning", "No reasoning provided")
            
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
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "jurisdiction_summary": valid_jurisdiction['summary']
                }
            else:
                return {
                    "jurisdiction_name": "Unknown",
                    "jurisdiction_code": None,
                    "confidence": "low",
                    "reasoning": f"Could not match '{jurisdiction_name}' to available jurisdictions",
                    "jurisdiction_summary": None
                }
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Raw response: {result_text}")
            return {
                "jurisdiction_name": "Unknown",
                "jurisdiction_code": None,
                "confidence": "low",
                "reasoning": f"Failed to parse LLM response as JSON: {str(e)}",
                "jurisdiction_summary": None
            }
            
    except Exception as e:
        print(f"Error in jurisdiction detection: {e}")
        return {
            "jurisdiction_name": "Unknown",
            "jurisdiction_code": None,
            "confidence": "low",
            "reasoning": f"Error during detection: {str(e)}",
            "jurisdiction_summary": None
        }

def determine_legal_system_type(jurisdiction_name: str, jurisdiction_code: str, jurisdiction_summary: str) -> str:
    """
    Determine if the jurisdiction follows civil law or common law based on the jurisdiction summary.
    """
    if not jurisdiction_summary:
        return "Unknown legal system"
    
    # Analyze the summary for legal system indicators
    summary_lower = jurisdiction_summary.lower()
    
    # Civil law indicators
    civil_law_indicators = [
        'civil code', 'civil law', 'napoleonic code', 'continental law',
        'romano-germanic', 'codified law', 'inquisitorial',
        'french civil code', 'german civil code', 'portuguese civil code',
        'rome i regulation', 'european union'
    ]
    
    # Common law indicators  
    common_law_indicators = [
        'common law', 'case law', 'precedent', 'stare decisis',
        'english law', 'anglo-american', 'adversarial',
        'judge-made law', 'judicial precedent', 'closest connection',
        'proper law of the contract'
    ]
    
    civil_law_score = sum(1 for indicator in civil_law_indicators if indicator in summary_lower)
    common_law_score = sum(1 for indicator in common_law_indicators if indicator in summary_lower)
    
    if civil_law_score > common_law_score:
        return "Civil-law jurisdiction"
    elif common_law_score > civil_law_score:
        return "Common-law jurisdiction"
    else:
        # If unclear from summary, use known jurisdiction patterns
        known_civil_law = [
            'Germany', 'France', 'Spain', 'Italy', 'Switzerland', 'Austria', 
            'Netherlands', 'Belgium', 'Portugal', 'Brazil', 'Argentina', 
            'Chile', 'Colombia', 'Mexico', 'Japan', 'South Korea', 'China',
            'European Union', 'Denmark', 'Sweden', 'Norway', 'Finland'
        ]
        
        known_common_law = [
            'United States', 'United Kingdom', 'Canada', 'Australia', 
            'New Zealand', 'India', 'South Africa', 'Nigeria', 'Kenya',
            'Ghana', 'Ireland', 'Singapore', 'Hong Kong', 'Malaysia',
            'Tanzania', 'Uganda', 'Zambia', 'Common-law Africa'
        ]
        
        for civil_jurisdiction in known_civil_law:
            if civil_jurisdiction.lower() in jurisdiction_name.lower():
                return "Civil-law jurisdiction"
                
        for common_jurisdiction in known_common_law:
            if common_jurisdiction.lower() in jurisdiction_name.lower():
                return "Common-law jurisdiction"
        
        return "Mixed or unclear legal system"
