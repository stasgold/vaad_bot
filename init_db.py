import sqlite3
from pathlib import Path
from datetime import datetime

# Database path
DB_PATH = Path(__file__).parent / "vaadbot.db"


def init_database():
    """Initialize the VaadBot SQLite database with all required tables."""
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # 1. BankTransactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BankTransactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL,
            name TEXT NOT NULL,
            account TEXT NOT NULL,
            amount REAL,
            reference TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    # 2. Residents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Residents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            flat TEXT NOT NULL UNIQUE,
            sum_to_pay REAL DEFAULT 0,
            accounts TEXT,
            is_late_to_pay INTEGER DEFAULT 0,
            phone TEXT,
            email TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # 3. Suppliers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            service TEXT NOT NULL,
            account TEXT NOT NULL,
            contact TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    # 4. DuePayments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DuePayments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL,
            service_id INTEGER,
            sum REAL NOT NULL,
            description TEXT,
            paid INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (service_id) REFERENCES Suppliers(id)
        )
    """)
    
    # Create indexes for better query performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_datetime ON BankTransactions(datetime)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_residents_flat ON Residents(flat)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_residents_late ON Residents(is_late_to_pay)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_duepayments_datetime ON DuePayments(datetime)")
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized at: {DB_PATH}")


if __name__ == "__main__":
    init_database()
