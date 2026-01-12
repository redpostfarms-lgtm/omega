# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# QUICK WALLET ACCESS - GUI Interface

import sys
import io
import json
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
            if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
            if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

ROOT = Path(r'D:\RPF_BRAIN\Omega')
WALLET_FILE = ROOT / 'crypto_wallets.json'
CONFIG_FILE = ROOT / 'limbo_config.json'


class WalletAccessGUI:
    """GUI for wallet access."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Omega - Wallet Access")
        self.root.geometry("800x600")
        
        self.wallets = self.load_wallets()
        self.config = self.load_config()
        
        self.create_widgets()
    
    def load_wallets(self):
        """Load wallets."""
        if WALLET_FILE.exists():
            try:
                with open(WALLET_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def load_config(self):
        """Load config."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def create_widgets(self):
        """Create GUI widgets."""
        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Wallet Addresses
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Wallet Addresses")
        self.create_addresses_tab(tab1)
        
        # Tab 2: Check Balances
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Check Balances")
        self.create_balances_tab(tab2)
        
        # Tab 3: Payment Info
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Payment Info")
        self.create_payment_tab(tab3)
        
        # Tab 4: Private Keys (with warning)
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Private Keys")
        self.create_keys_tab(tab4)
    
    def create_addresses_tab(self, parent):
        """Create addresses tab."""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        if self.wallets:
            # Bitcoin
            ttk.Label(frame, text="Bitcoin Address:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
            btc_frame = ttk.Frame(frame)
            btc_frame.pack(fill=tk.X, pady=5)
            btc_entry = ttk.Entry(btc_frame, width=60, font=('Courier', 9))
            btc_entry.insert(0, self.wallets['bitcoin']['address'])
            btc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(btc_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.wallets['bitcoin']['address'])).pack(side=tk.LEFT, padx=5)
            
            # Ethereum
            ttk.Label(frame, text="Ethereum Address:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
            eth_frame = ttk.Frame(frame)
            eth_frame.pack(fill=tk.X, pady=5)
            eth_entry = ttk.Entry(eth_frame, width=60, font=('Courier', 9))
            eth_entry.insert(0, self.wallets['ethereum']['address'])
            eth_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(eth_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.wallets['ethereum']['address'])).pack(side=tk.LEFT, padx=5)
            
            # Testnet
            ttk.Label(frame, text="Testnet Address:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
            test_frame = ttk.Frame(frame)
            test_frame.pack(fill=tk.X, pady=5)
            test_entry = ttk.Entry(test_frame, width=60, font=('Courier', 9))
            test_entry.insert(0, self.wallets['testnet']['address'])
            test_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(test_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.wallets['testnet']['address'])).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Label(frame, text="No wallets found. Run wallet generator first.", foreground='red').pack(pady=20)
    
    def create_balances_tab(self, parent):
        """Create balances tab."""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        if self.wallets:
            ttk.Label(frame, text="Check Wallet Balances:", font=('Arial', 12, 'bold')).pack(pady=10)
            
            ttk.Button(frame, text="Check Bitcoin Balance", command=self.open_btc_explorer, width=30).pack(pady=5)
            ttk.Button(frame, text="Check Ethereum Balance", command=self.open_eth_explorer, width=30).pack(pady=5)
            ttk.Button(frame, text="Check Testnet Balance", command=self.open_testnet_explorer, width=30).pack(pady=5)
        else:
            ttk.Label(frame, text="No wallets found.", foreground='red').pack(pady=20)
    
    def create_payment_tab(self, parent):
        """Create payment info tab."""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Payment Methods:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        if self.config and self.config.get('paypal_email'):
            ttk.Label(frame, text="PayPal:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
            paypal_frame = ttk.Frame(frame)
            paypal_frame.pack(fill=tk.X, pady=5)
            paypal_entry = ttk.Entry(paypal_frame, width=40)
            paypal_entry.insert(0, self.config['paypal_email'])
            paypal_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(paypal_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.config['paypal_email'])).pack(side=tk.LEFT, padx=5)
    
    def create_keys_tab(self, parent):
        """Create private keys tab."""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        warning = ttk.Label(frame, text="⚠️ WARNING: Never share private keys with anyone!", 
                           font=('Arial', 10, 'bold'), foreground='red')
        warning.pack(pady=10)
        
        if self.wallets:
            text = scrolledtext.ScrolledText(frame, width=70, height=15, font=('Courier', 9))
            text.pack(fill=tk.BOTH, expand=True, pady=10)
            
            content = f"""Bitcoin Private Key:
{self.wallets['bitcoin']['private_key']}

Ethereum Private Key:
{self.wallets['ethereum']['private_key']}

Testnet Private Key:
{self.wallets['testnet']['private_key']}
"""
            text.insert('1.0', content)
            text.config(state=tk.DISABLED)
        else:
            ttk.Label(frame, text="No wallets found.", foreground='red').pack(pady=20)
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "Address copied to clipboard!")
    
    def open_btc_explorer(self):
        """Open Bitcoin explorer."""
        if self.wallets:
            url = f'https://blockstream.info/address/{self.wallets["bitcoin"]["address"]}'
            webbrowser.open(url)
    
    def open_eth_explorer(self):
        """Open Ethereum explorer."""
        if self.wallets:
            url = f'https://etherscan.io/address/{self.wallets["ethereum"]["address"]}'
            webbrowser.open(url)
    
    def open_testnet_explorer(self):
        """Open testnet explorer."""
        if self.wallets:
            url = f'https://sepolia.etherscan.io/address/{self.wallets["testnet"]["address"]}'
            webbrowser.open(url)


def main():
    """Main function."""
    root = tk.Tk()
    app = WalletAccessGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
