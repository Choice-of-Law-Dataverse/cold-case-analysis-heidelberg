# utils/jurisdiction_test_helper.py
"""
Utility functions for testing and validating jurisdiction detection functionality.
"""
import csv
from pathlib import Path

def get_jurisdiction_statistics():
    """
    Get statistics about the jurisdictions in the CSV file.
    
    Returns:
        dict: Statistics about jurisdictions
    """
    jurisdictions_file = Path(__file__).parent.parent / 'data' / 'jurisdictions.csv'
    
    total_jurisdictions = 0
    jurisdictions_with_summaries = 0
    jurisdictions_with_codes = 0
    unique_regions = set()
    
    with open(jurisdictions_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Name'].strip():
                total_jurisdictions += 1
                
                if row['Jurisdiction Summary'].strip():
                    jurisdictions_with_summaries += 1
                    
                if row['Alpha-3 Code'].strip():
                    jurisdictions_with_codes += 1
                    
                # Try to identify regions from names
                name_lower = row['Name'].lower()
                if any(term in name_lower for term in ['africa', 'african']):
                    unique_regions.add('Africa')
                elif any(term in name_lower for term in ['asia', 'asian']):
                    unique_regions.add('Asia')
                elif any(term in name_lower for term in ['europe', 'european']):
                    unique_regions.add('Europe')
                elif any(term in name_lower for term in ['america', 'american', 'states', 'canada']):
                    unique_regions.add('Americas')
                elif any(term in name_lower for term in ['oceania', 'australia', 'pacific']):
                    unique_regions.add('Oceania')
    
    return {
        'total_jurisdictions': total_jurisdictions,
        'jurisdictions_with_summaries': jurisdictions_with_summaries,
        'jurisdictions_with_codes': jurisdictions_with_codes,
        'coverage_percentage': round((jurisdictions_with_summaries / total_jurisdictions * 100) if total_jurisdictions > 0 else 0, 1),
        'regions_identified': sorted(list(unique_regions))
    }

def search_jurisdictions_by_name(search_term: str, limit: int = 10):
    """
    Search for jurisdictions by name (fuzzy matching).
    
    Args:
        search_term: Term to search for
        limit: Maximum number of results to return
        
    Returns:
        list: Matching jurisdictions
    """
    jurisdictions_file = Path(__file__).parent.parent / 'data' / 'jurisdictions.csv'
    results = []
    
    search_term_lower = search_term.lower()
    
    with open(jurisdictions_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Name'].strip():
                name_lower = row['Name'].lower()
                
                # Exact match gets highest priority
                if search_term_lower == name_lower:
                    results.insert(0, {
                        'name': row['Name'].strip(),
                        'code': row['Alpha-3 Code'].strip(),
                        'has_summary': bool(row['Jurisdiction Summary'].strip()),
                        'match_type': 'exact'
                    })
                # Starts with search term gets second priority
                elif name_lower.startswith(search_term_lower):
                    results.append({
                        'name': row['Name'].strip(),
                        'code': row['Alpha-3 Code'].strip(),
                        'has_summary': bool(row['Jurisdiction Summary'].strip()),
                        'match_type': 'prefix'
                    })
                # Contains search term gets third priority
                elif search_term_lower in name_lower:
                    results.append({
                        'name': row['Name'].strip(),
                        'code': row['Alpha-3 Code'].strip(),
                        'has_summary': bool(row['Jurisdiction Summary'].strip()),
                        'match_type': 'contains'
                    })
                
                if len(results) >= limit:
                    break
    
    return results[:limit]

def validate_jurisdiction_name(jurisdiction_name: str):
    """
    Validate if a jurisdiction name exists in our database.
    
    Args:
        jurisdiction_name: Name to validate
        
    Returns:
        dict: Validation result
    """
    jurisdictions_file = Path(__file__).parent.parent / 'data' / 'jurisdictions.csv'
    
    with open(jurisdictions_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Name'].strip().lower() == jurisdiction_name.lower():
                return {
                    'valid': True,
                    'exact_name': row['Name'].strip(),
                    'code': row['Alpha-3 Code'].strip(),
                    'has_summary': bool(row['Jurisdiction Summary'].strip())
                }
    
    return {
        'valid': False,
        'exact_name': None,
        'code': None,
        'has_summary': False
    }
