# VaadBot - Building Committee Assistant 🏢

AI-powered bookkeeping and money-collection assistant for an 80-unit residential building in Israel.

## Features

### 🤖 VaadBot Agent
- Building management and billing assistant
- Resident balance inquiries and payment tracking
- Admin tools for charges, expenses, and reports
- Utility-focused interactions following WhatsApp policy compliance

### 📄 Document Processing
- **doc2md MCP Server**: Convert any document (PDF/DOCX/XLSX/Images/Email) to Markdown
- **Hebrew + English OCR**: Full support for Israeli documents
- Automatic payment screenshot parsing
- Extract transaction details from bank statements

### 💾 Database Management
SQLite database with structured tables:
- **BankTransactions**: Payment records with bank-branch-account format
- **Residents**: Unit information, balances, payment status
- **Suppliers**: Service providers and vendors
- **DuePayments**: Scheduled payments and expenses

### 🔍 Payment Screenshot Processing
- Automated OCR extraction (Hebrew + English)
- LLM-based parsing of payment details
- Extracts: date, payer name, account (bank-branch-account), amount
- Archives processed screenshots automatically

## Installation

### Prerequisites

**1. Tesseract OCR with Hebrew support:**
```bash
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-heb
```

**2. Python 3.10+**

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/VaadBait.git
cd VaadBait
```

2. Create virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r doc2md_mcp/requirements.txt
```

3. Initialize database:
```bash
python init_db.py
```

## Usage

### Process Payment Screenshots
Place payment screenshots in the `Input/` folder, then:
```bash
python process_payments.py
```

### View Recent Transactions
```python
from process_payments import get_all_transactions

transactions = get_all_transactions(limit=10)
for tx in transactions:
    print(f"{tx['datetime']} | {tx['name']} | ₪{tx['amount']}")
```

### Database Operations
```python
from db_helpers import (
    add_resident,
    get_resident_by_flat,
    update_resident_balance,
    get_late_payers
)

# Add a new resident
add_resident(
    name="משה כהן",
    flat="42",
    sum_to_pay=460.00,
    phone="+972-50-1234567"
)

# Check balance
resident = get_resident_by_flat("42")
print(f"Balance: ₪{resident['sum_to_pay']}")

# Get late payers
late_payers = get_late_payers()
```

## Project Structure

```
VaadBait/
├── .github/
│   └── agents/
│       └── VaadBot.agent.md       # Agent definition for VS Code
├── doc2md_mcp/
│   ├── server.py                  # MCP server for document conversion
│   ├── requirements.txt           # Python dependencies
│   └── README.md                  # doc2md documentation
├── Input/                         # Place files to process here
├── Output/                        # Converted markdown files
├── Documents/                     # Archived payment screenshots
├── init_db.py                     # Database initialization
├── db_helpers.py                  # Database utility functions
├── payment_parser.py              # LLM-based payment parser
├── process_payments.py            # Payment processing workflow
├── PAYMENT_PROCESSING.md          # Payment processing documentation
└── vaadbot.db                     # SQLite database (auto-generated)
```

## Vaad Bayit Information

- **Bank Account**: 12-701-12341
  - Bank: Hapoalim (12)
  - Branch: 701 - Har HaCarmel
  - Account: 12341

## Security & Compliance

✅ **Safe Practices:**
- Never stores bank credentials, CVV, or passwords
- Redacts sensitive data in outputs
- All financial actions require admin authorization
- Logging for all money-moving operations

❌ **Never:**
- Attempts to login to bank portals
- Bypasses security measures
- Stores unencrypted sensitive data

## Account Format

All bank accounts use the format: **bank-branch-account**

Examples:
- `12-701-12341` - Bank Hapoalim, Branch 701
- `10-500-98765` - Bank Leumi, Branch 500

## Documentation

- [Payment Processing Guide](PAYMENT_PROCESSING.md)
- [doc2md MCP Server](doc2md_mcp/README.md)
- [VaadBot Agent](.github/agents/VaadBot.agent.md)

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ for Israeli residential building committees
