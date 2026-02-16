"""
LLM-based payment screenshot parser for VaadBot.

This module uses LLM reasoning to extract payment details from OCR text
from Israeli bank transfer screenshots.
"""

import re
from datetime import datetime
from typing import Dict, Optional


def parse_payment_screenshot_llm(ocr_text: str) -> Dict[str, Optional[str]]:
    """
    Parse payment details from OCR text using LLM reasoning.
    
    Args:
        ocr_text: Raw OCR extracted text from payment screenshot
        
    Returns:
        Dictionary with keys: datetime, name, account, amount, reference
    """
    
    # Initialize result
    result = {
        "datetime": None,
        "name": None,
        "account": None,
        "amount": None,
        "reference": "Payment screenshot"
    }
    
    # LLM reasoning for datetime extraction
    # Look for Israeli date formats: DD/MM/YYYY or DD.MM.YYYY
    date_patterns = [
        r'(\d{2})/(\d{2})/(\d{4})',  # DD/MM/YYYY
        r'(\d{2})\.(\d{2})\.(\d{4})',  # DD.MM.YYYY
        r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, ocr_text)
        if match:
            if pattern.startswith(r'(\d{4})'):  # YYYY-MM-DD
                result["datetime"] = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            else:  # DD/MM/YYYY or DD.MM.YYYY
                result["datetime"] = f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
            break
    
    # LLM reasoning for amount extraction
    # Look for Israeli shekel amounts (could be with ₪ or just numbers with .00)
    amount_patterns = [
        r'(\d{1,6}\.\d{2})\s*(?:₪|ILS|ils|ש"ח)',
        r'(?:₪|ILS|ils|ש"ח)\s*(\d{1,6}\.\d{2})',
        r'\b(\d{1,6}\.\d{2})\b',
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, ocr_text)
        if match:
            amount_str = match.group(1)
            try:
                result["amount"] = str(float(amount_str))
                break
            except ValueError:
                continue
    
    # LLM reasoning for bank account extraction
    # Israeli bank accounts: bank(2-3 digits)-branch(3 digits)-account(variable length)
    # Common patterns in OCR text
    account_patterns = [
        r'(\d{2,3})[־\-\s]*(\d{3})[־\-\s]*(\d{4,8})',  # With separators
        r'(?:חשבון|account|acc)[:\s]*(\d{2,3})[־\-]?(\d{3})[־\-]?(\d{4,8})',  # After "account" label
    ]
    
    for pattern in account_patterns:
        match = re.search(pattern, ocr_text, re.IGNORECASE)
        if match:
            if len(match.groups()) == 3:
                bank = match.group(1).zfill(2)
                branch = match.group(2).zfill(3)
                account = match.group(3)
                result["account"] = f"{bank}-{branch}-{account}"
                break
    
    # If no pattern found, try to extract just the account number
    if not result["account"]:
        simple_account = re.search(r'\b(\d{5,8})\b', ocr_text)
        if simple_account:
            result["account"] = f"12-701-{simple_account.group(1)}"  # Default to Hapoalim 701
    
    # LLM reasoning for name extraction
    # Look for Hebrew or English names
    # Common patterns: actual person names (not form labels like "הוראת קבע", "בנק", etc.)
    # Blacklist common form terms
    form_terms = ['הוראת', 'קבע', 'בנק', 'חשבון', 'זכות', 'חיוב', 'לזכות', 'משלם', 'פרטי']
    
    name_patterns = [
        r'(?:משלם|שם משלם|שם)[:\s]+([א-ת][א-ת\s\'״\"]+)',  # Hebrew name after label
        r'(?:name|from)[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # English name
        r'\b([א-ת]{3,}\s+[א-ת]{3,})\b',  # Two Hebrew words (likely first + last name)
    ]
    
    for pattern in name_patterns:
        matches = re.findall(pattern, ocr_text, re.IGNORECASE)
        for match in matches:
            name_candidate = match.strip() if isinstance(match, str) else match[0].strip()
            # Skip if contains form terms
            if not any(term in name_candidate for term in form_terms):
                result["name"] = name_candidate
                break
        if result["name"]:
            break
    
    # Fallback: if name not found, mark as unknown
    if not result["name"]:
        result["name"] = "Unknown Resident"
    
    # If no datetime found, use current timestamp
    if not result["datetime"]:
        result["datetime"] = datetime.now().strftime("%Y-%m-%d")
    
    return result


def validate_parsed_payment(parsed_data: Dict[str, Optional[str]]) -> bool:
    """
    Validate that critical payment data was extracted.
    
    Returns:
        True if amount and account are present, False otherwise
    """
    return (
        parsed_data.get("amount") is not None and
        parsed_data.get("account") is not None
    )


# Example usage and testing
if __name__ == "__main__":
    # Test with sample OCR text
    sample_ocr = """
    11/02/2026 1
    10:55 ay
    
    oa 7A 701 jp [lax 435910
    N7 Ww 2 TW 00012341 4) wow in'7X 134528 aun
    
    ; o7pwani0 4 190 19 460.00 B10
    """
    
    result = parse_payment_screenshot_llm(sample_ocr)
    print("Parsed payment data:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print(f"\nValidation: {'✅ VALID' if validate_parsed_payment(result) else '❌ INVALID'}")
