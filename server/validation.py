import re
from typing import Dict, Any


def validate_test_plan(test_plan: str) -> Dict[str, Any]:
    """
    Validate the generated test plan for completeness and structure.
    
    Args:
        test_plan (str): The generated test plan content
        
    Returns:
        Dict[str, Any]: Validation result with is_valid flag and message
    """
    if not test_plan or not test_plan.strip():
        return {
            "is_valid": False,
            "message": "Test plan is empty or contains only whitespace"
        }
    
    # Check minimum length
    if len(test_plan.strip()) < 100:
        return {
            "is_valid": False,
            "message": "Test plan is too short (minimum 100 characters required)"
        }
    
    # Check for basic test plan structure
    required_sections = [
        r"(?i)(test|testing)",  # Should mention testing
        r"(?i)(objective|goal|purpose)",  # Should have objectives
        r"(?i)(scenario|case|step)",  # Should have test cases/scenarios
    ]
    
    missing_sections = []
    for section_pattern in required_sections:
        if not re.search(section_pattern, test_plan):
            missing_sections.append(section_pattern)
    
    if missing_sections:
        return {
            "is_valid": False,
            "message": f"Test plan is missing essential content. Consider adding more detail about testing objectives, scenarios, and steps."
        }
    
    # Check for reasonable structure (headings, lists, etc.)
    has_structure = any([
        re.search(r'^#{1,6}\s', test_plan, re.MULTILINE),  # Markdown headers
        re.search(r'^\d+\.', test_plan, re.MULTILINE),     # Numbered lists
        re.search(r'^[-*+]\s', test_plan, re.MULTILINE),   # Bullet lists
    ])
    
    if not has_structure:
        return {
            "is_valid": False,
            "message": "Test plan lacks clear structure. Consider using headers, lists, or numbered steps."
        }
    
    return {
        "is_valid": True,
        "message": "Test plan validation passed"
    } 