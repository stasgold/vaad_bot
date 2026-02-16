"""
Helper functions for VaadBot database operations.
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

DB_PATH = Path(__file__).parent / "vaadbot.db"


def get_connection():
    """Get a database connection."""
    return sqlite3.connect(str(DB_PATH))


def add_bank_transaction(
    transaction_datetime: str,
    name: str,
    account: str,
    amount: Optional[float] = None,
    reference: Optional[str] = None
) -> int:
    """
    Add a bank transaction to the database.
    
    Returns:
        Transaction ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO BankTransactions (datetime, name, account, amount, reference, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (transaction_datetime, name, account, amount, reference, datetime.utcnow().isoformat()))
    
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return transaction_id


def get_resident_by_flat(flat: str) -> Optional[Dict[str, Any]]:
    """Get resident information by flat number."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Residents WHERE flat = ?", (flat,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def add_resident(
    name: str,
    flat: str,
    sum_to_pay: float = 0.0,
    accounts: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None
) -> int:
    """Add a new resident."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO Residents (name, flat, sum_to_pay, accounts, is_late_to_pay, phone, email, created_at, updated_at)
        VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?)
    """, (name, flat, sum_to_pay, accounts, phone, email, now, now))
    
    resident_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return resident_id


def update_resident_balance(flat: str, amount: float, is_late: bool = False):
    """Update resident balance and late payment status."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE Residents 
        SET sum_to_pay = ?, is_late_to_pay = ?, updated_at = ?
        WHERE flat = ?
    """, (amount, 1 if is_late else 0, datetime.utcnow().isoformat(), flat))
    
    conn.commit()
    conn.close()


def get_late_payers() -> List[Dict[str, Any]]:
    """Get all residents with late payments."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Residents WHERE is_late_to_pay = 1 ORDER BY flat")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def add_supplier(name: str, service: str, account: str, contact: Optional[str] = None) -> int:
    """Add a new supplier."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO Suppliers (name, service, account, contact, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, service, account, contact, datetime.utcnow().isoformat()))
    
    supplier_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return supplier_id


def add_due_payment(
    payment_datetime: str,
    sum_amount: float,
    service_id: Optional[int] = None,
    description: Optional[str] = None
) -> int:
    """Add a due payment."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO DuePayments (datetime, service_id, sum, description, paid, created_at)
        VALUES (?, ?, ?, ?, 0, ?)
    """, (payment_datetime, service_id, sum_amount, description, datetime.utcnow().isoformat()))
    
    payment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return payment_id


def mark_payment_paid(payment_id: int):
    """Mark a due payment as paid."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE DuePayments SET paid = 1 WHERE id = ?", (payment_id,))
    
    conn.commit()
    conn.close()


def get_unpaid_dues() -> List[Dict[str, Any]]:
    """Get all unpaid due payments."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT dp.*, s.name as supplier_name, s.service 
        FROM DuePayments dp
        LEFT JOIN Suppliers s ON dp.service_id = s.id
        WHERE dp.paid = 0
        ORDER BY dp.datetime
    """)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
