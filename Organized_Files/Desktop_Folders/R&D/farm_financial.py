"""
Farm Financial System
Track farm finances and expenses.

Red Post Farms, LLC - 2026
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
FARM_DIR = BRAIN_DIR / "Archived" / "farm_data"
FARM_DIR.mkdir(parents=True, exist_ok=True)

class FarmFinancial:
    def __init__(self):
        self.transactions = []
        self._load_transactions()
    
    def _load_transactions(self):
        """Load transactions."""
        transactions_file = FARM_DIR / "transactions.json"
        if transactions_file.exists():
            try:
                with open(transactions_file, 'r', encoding='utf-8') as f:
                    self.transactions = json.load(f)
            except: pass
    
    def _save_transactions(self):
        """Save transactions."""
        transactions_file = FARM_DIR / "transactions.json"
        with open(transactions_file, 'w', encoding='utf-8') as f:
            json.dump(self.transactions, f, indent=2)
    
    def add_transaction(self, description: str, amount: float, transaction_type: str = "expense"):
        """Add a transaction."""
        self.transactions.append({
            "description": description,
            "amount": amount,
            "type": transaction_type,
            "date": datetime.now().isoformat()
        })
        self._save_transactions()
    
    def get_balance(self) -> float:
        """Get current balance."""
        income = sum(t["amount"] for t in self.transactions if t["type"] == "income")
        expenses = sum(t["amount"] for t in self.transactions if t["type"] == "expense")
        return income - expenses
    
    def get_transactions(self) -> List[Dict]:
        """Get all transactions."""
        return self.transactions

def main():
    ff = FarmFinancial()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python farm_financial.py <command> [args...]")
        print("Commands: add <description> <amount> [type], balance, list")
        return
    cmd = sys.argv[1].lower()
    if cmd == "add":
        if len(sys.argv) < 4: print("Error: add requires description and amount"); return
        ttype = sys.argv[4] if len(sys.argv) > 4 else "expense"
        ff.add_transaction(sys.argv[2], float(sys.argv[3]), ttype)
        print("OK Transaction added")
    elif cmd == "balance":
        balance = ff.get_balance()
        print(f"Balance: ${balance:.2f}")
    elif cmd == "list":
        transactions = ff.get_transactions()
        print(f"Transactions ({len(transactions)}):")
        for t in transactions[-10:]: print(f"  {t['date']} - {t['type']} - {t['description']} - ${t['amount']:.2f}")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

