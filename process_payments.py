"""
Process payment screenshots from Input folder using LLM-based parsing.

This script:
1. Finds payment screenshots in Input folder
2. Uses doc2md MCP for OCR extraction
3. Uses LLM reasoning to parse payment details
4. Inserts into BankTransactions table
5. Moves screenshots to Documents folder
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from payment_parser import parse_payment_screenshot_llm, validate_parsed_payment


DB_PATH = Path(__file__).parent / "vaadbot.db"
INPUT_DIR = Path(__file__).parent / "Input"
DOCUMENTS_DIR = Path(__file__).parent / "Documents"


def process_payment_screenshot(image_path: Path, ocr_text: str) -> Optional[int]:
    """
    Process a payment screenshot: parse and insert into database.
    
    Args:
        image_path: Path to the screenshot file
        ocr_text: OCR extracted text from the screenshot
        
    Returns:
        Transaction ID if successful, None otherwise
    """
    
    # Parse using LLM reasoning
    parsed = parse_payment_screenshot_llm(ocr_text)
    
    # Validate
    if not validate_parsed_payment(parsed):
        print(f"❌ Failed to parse critical data from {image_path.name}")
        return None
    
    # Insert into database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO BankTransactions (datetime, name, account, amount, reference, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            parsed["datetime"],
            parsed["name"],
            parsed["account"],
            float(parsed["amount"]),
            parsed["reference"],
            datetime.utcnow().isoformat()
        ))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        
        # Move file to Documents folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = DOCUMENTS_DIR / f"payment_{timestamp}_{transaction_id}{image_path.suffix}"
        shutil.move(str(image_path), str(dest))
        
        print(f"✅ Payment recorded (ID: {transaction_id})")
        print(f"   Amount: ₪{parsed['amount']}")
        print(f"   From: {parsed['name']}")
        print(f"   Account: {parsed['account']}")
        print(f"   Date: {parsed['datetime']}")
        print(f"   Screenshot archived to: {dest.name}")
        
        return transaction_id
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return None
        
    finally:
        conn.close()


def get_all_transactions(limit: int = 10) -> list:
    """Get recent bank transactions."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, datetime, name, account, amount, reference, created_at
        FROM BankTransactions
        ORDER BY datetime DESC, created_at DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


if __name__ == "__main__":
    # Display recent transactions
    print("Recent transactions:")
    print("-" * 80)
    
    transactions = get_all_transactions(limit=5)
    if transactions:
        for tx in transactions:
            print(f"ID: {tx['id']} | {tx['datetime']} | {tx['name']:30s} | {tx['account']:15s} | ₪{tx['amount']:>8.2f}")
    else:
        print("(No transactions yet)")
