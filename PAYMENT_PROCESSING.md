# VaadBot Payment Processing System

## Overview
VaadBot processes payment screenshots using OCR + LLM reasoning to automatically extract and record transactions.

## Vaad Bayit Information
- **Bank Account:** 12-701-12341
  - Bank: Hapoalim (12)
  - Branch: 701
  - Account: 12341

## Account Format
All bank accounts in the system use the format: **bank-branch-account**
- Example: `12-701-12341` (Bank Hapoalim, Branch 701, Account 12341)
- Example: `10-500-98765` (Bank Leumi, Branch 500, Account 98765)

## Payment Screenshot Processing Workflow

### 1. Upload Screenshot
Place payment screenshots in the `Input/` folder.

### 2. OCR Extraction
The system uses the `doc2md` MCP tool to extract text from images.

### 3. LLM Parsing
The `payment_parser.py` module uses pattern matching and reasoning to extract:
- **Transaction datetime** (ISO format: YYYY-MM-DD)
- **Payer name** (Hebrew or English)
- **Bank account** (bank-branch-account format)
- **Amount** (in ILS/₪)
- **Reference/description**

### 4. Database Storage
Parsed data is inserted into the `BankTransactions` table:
```sql
CREATE TABLE BankTransactions (
    id INTEGER PRIMARY KEY,
    datetime TEXT NOT NULL,
    name TEXT NOT NULL,
    account TEXT NOT NULL,  -- Format: bank-branch-account
    amount REAL,
    reference TEXT,
    created_at TEXT NOT NULL
)
```

### 5. Archiving
Processed screenshots are moved to `Documents/` folder with timestamped filenames.

## Files

### Core Scripts
- `init_db.py` - Initialize database with all tables
- `payment_parser.py` - LLM-based payment details parser
- `process_payments.py` - Main payment processing script
- `db_helpers.py` - Database utility functions
- `migrate_accounts.py` - Migrate account format to bank-branch-account

### Folders
- `Input/` - Place payment screenshots here
- `Output/` - Converted markdown documents
- `Documents/` - Archived payment screenshots
- `doc2md_mcp/` - MCP server for document conversion

### Database
- `vaadbot.db` - SQLite database
  - BankTransactions
  - Residents
  - Suppliers
  - DuePayments

## Usage

### View Recent Transactions
```bash
python process_payments.py
```

### Process Payment Screenshot (manual)
```python
from process_payments import process_payment_screenshot
from pathlib import Path

# Assume OCR text extracted
ocr_text = "..."
image_path = Path("Input/payment.jpg")

tx_id = process_payment_screenshot(image_path, ocr_text)
```

### Query Database
```python
from db_helpers import get_resident_by_flat, get_late_payers

# Get resident info
resident = get_resident_by_flat("42")

# Get all late payers
late_payers = get_late_payers()
```

## Example Output
```
✅ Payment recorded (ID: 1)
   Amount: ₪460.00
   From: Unknown Resident
   Account: 12-701-12341
   Date: 2026-02-11
   Screenshot archived to: payment_20260216_181926_1.jpeg
```

## Security & Privacy
- Bank account numbers are stored in structured format for reconciliation
- Sensitive data (branch/account) is logged only for admin operations
- Screenshots are archived separately from database records
- Never store bank credentials or passwords
