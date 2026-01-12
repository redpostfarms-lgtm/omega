#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# SALESBOT + LOGISTICS HUB 2026
# Full chat + order engine + tracking + inventory
# One voice, zero sweat. No Shopify. Just farm truth.

import json
import time
import sys
import io
import threading
import re
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("pyttsx3 not installed. Install with: pip install pyttsx3")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not installed. Install with: pip install requests")

ROOT = Path(r'D:\RPF_BRAIN\Sales')
ROOT.mkdir(parents=True, exist_ok=True)

ORDERS = ROOT / 'orders.jsonl'
INVENTORY = ROOT / 'stock.json'
TRACKING = ROOT / 'tracking.json'
PORTAL_KEY = 'your-free-local-portal-hash'  # self-hosted, no AWS

# Default inventory
DEFAULT_INVENTORY = {
    'beef': 42,  # pounds
    'eggs': 120,  # dozen
    'castings': 180,  # pounds
    'tomatoes': 300,  # pounds
    'chicken': 25,  # whole birds
    'pork': 30,  # pounds
    'honey': 50,  # jars
    'lettuce': 200,  # heads
    'herbs': 100,  # bunches
}

class SalesBot:
    """SalesBot + Logistics Hub - Full chat, order, tracking system."""
    
    def __init__(self):
        """Initialize SalesBot."""
        self.tts_engine = None
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 160)
                voices = self.tts_engine.getProperty('voices')
                zira_voice = next((v.id for v in voices if 'zira' in v.name.lower()), None)
                if zira_voice:
                    self.tts_engine.setProperty('voice', zira_voice)
            except Exception as e:
                logger.error(f"TTS initialization failed: {e}", exc_info=True)
                self.tts_engine = None
        
        self.speak('Chatbot plus logistics live. Orders rolling. Tracking pinging.')
        
        # Load data
        self.stock = self.load('stock.json')
        self.orders = self.load('orders.jsonl')
        self.tracking = self.load('tracking.json')
        
        # Payment processing (local, zero-cost)
        self.payments_file = ROOT / 'payments.json'
        self.payments = self.load('payments.json') if (ROOT / 'payments.json').exists() else []
        
        # Start background monitoring
        self.monitoring = True
        threading.Thread(target=self.monitor_shipments, daemon=True).start()
    
    def load(self, file: str):
        """Load data from file."""
        file_path = ROOT / file
        
        if file_path.exists():
            try:
                if file.endswith('.jsonl'):
                    orders = []
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                orders.append(json.loads(line))
                    return orders
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Error loading {file}: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error loading {file}: {e}", exc_info=True)
        
        # Return defaults
        if file == 'stock.json':
            return DEFAULT_INVENTORY.copy()
        elif file == 'tracking.json':
            return {}
        else:
            return []
    
    def save(self, file: str):
        """Save data to file."""
        file_path = ROOT / file
        
        try:
            if file.endswith('.jsonl'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    for order in self.orders:
                        f.write(json.dumps(order, ensure_ascii=False) + '\n')
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file == 'tracking.json':
                        json.dump(self.tracking, f, indent=2, ensure_ascii=False)
                    elif file == 'stock.json':
                        json.dump(self.stock, f, indent=2, ensure_ascii=False)
                    elif file == 'payments.json':
                        json.dump(self.payments, f, indent=2, ensure_ascii=False)
        except (IOError, PermissionError) as e:
            logger.error(f"Error saving {file}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving {file}: {e}", exc_info=True)
    
    def speak(self, txt: str) -> None:
        """Speak text using TTS.
        
        Args:
            txt: Text to speak
        """
        logger.info(f"SalesBot: {txt}")
        print(f"SalesBot: {txt}")
        if self.tts_engine:
            try:
                self.tts_engine.say(txt)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS speak failed: {e}", exc_info=True)
    
    # ——— CHATBOT ———
    def chat(self, user: str, msg: str):
        """Handle chat messages."""
        msg_lower = msg.lower()
        
        if 'hello' in msg_lower or 'hi' in msg_lower or 'hey' in msg_lower:
            self.speak(f'Hey {user}. What is cooking?')
        
        elif 'what do you have' in msg_lower or 'stock' in msg_lower or 'inventory' in msg_lower:
            stock_msg = f"We have got {self.stock.get('beef', 0)} pounds pasture beef, {self.stock.get('eggs', 0)} dozen eggs, {self.stock.get('castings', 0)} pounds worm castings, {self.stock.get('tomatoes', 0)} pounds tomatoes."
            if self.stock.get('chicken', 0) > 0:
                stock_msg += f" {self.stock['chicken']} whole chickens."
            if self.stock.get('honey', 0) > 0:
                stock_msg += f" {self.stock['honey']} jars of honey."
            stock_msg += " All organic."
            self.speak(stock_msg)
        
        elif 'order' in msg_lower:
            self.handle_order(msg)
        
        elif 'track' in msg_lower or 'where is my' in msg_lower or 'status' in msg_lower:
            self.track_order(msg)
        
        elif 'help' in msg_lower:
            self.speak('I have beef, eggs, castings, tomatoes, chicken, pork, honey, lettuce, herbs. Say order 5 pounds beef, or track your order number.')
        
        else:
            self.speak('I have beef, eggs, castings, tomatoes. Want one? Say order 5 pounds beef.')
    
    # ——— ORDER ENGINE ———
    def handle_order(self, msg: str) -> None:
        """Process order from message.
        
        Args:
            msg: Message containing order information
        """
        # Sanitize input
        msg_lower = msg.lower().strip()[:500]  # Limit length
        
        # Extract quantity
        qty = 1
        qty_match = re.search(r'(\d+)\s*(?:lb|lbs|pound|pounds|dozen|dz|jar|jars|head|heads|bunch|bunches)', msg_lower)
        if qty_match:
            qty = int(qty_match.group(1))
        else:
            # Try to find any number
            num_match = re.search(r'\b(\d+)\b', msg_lower)
            if num_match:
                qty = int(num_match.group(1))
        
        # Extract item
        item = None
        items = ['beef', 'steak', 'egg', 'eggs', 'casting', 'castings', 'tomato', 'tomatoes', 
                 'chicken', 'pork', 'honey', 'lettuce', 'herb', 'herbs']
        
        for product in items:
            if product in msg_lower:
                item = product
                # Normalize to singular/plural
                if item == 'egg':
                    item = 'eggs'
                elif item == 'tomato':
                    item = 'tomatoes'
                elif item == 'casting':
                    item = 'castings'
                elif item == 'herb':
                    item = 'herbs'
                elif item == 'steak':
                    item = 'beef'
                break
        
        if not item:
            self.speak('What do you want to order? Say order 5 pounds beef, or order 2 dozen eggs.')
            return
        
        # Check stock
        if item not in self.stock:
            self.speak(f'{item} is not in stock. Try beef, eggs, castings, or tomatoes.')
            return
        
        if self.stock[item] < qty:
            self.speak(f'Only {self.stock[item]} {item} in stock. Want to order what we have?')
            return
        
        # Create order
        order_id = str(len(self.orders) + 1).zfill(5)  # 00001
        
        # Update stock
        self.stock[item] -= qty
        
        # Generate order
        new_order = {
            'id': order_id,
            'user': 'portal',
            'item': item,
            'qty': qty,
            'time': datetime.now().isoformat(),
            'status': 'packed',
            'total': self.calculate_price(item, qty)
        }
        
        self.orders.append(new_order)
        self.save('orders.jsonl')
        self.save('stock.json')
        
        # Update tracking
        self.update_tracking(order_id, 'shipped')
        
        # Process payment (simulated - local, zero-cost)
        payment_status = self.process_payment(order_id, new_order['total'])
        new_order['payment_status'] = payment_status
        
        # Speak confirmation
        self.speak(f'{qty} {item} ordered. Ticket number {order_id}. Payment {payment_status}. Shipping today.')
        
        # Print label
        self.print_label(order_id)
    
    def calculate_price(self, item: str, qty: int) -> float:
        """Calculate order total."""
        prices = {
            'beef': 12.50,  # per pound
            'eggs': 6.00,  # per dozen
            'castings': 8.00,  # per pound
            'tomatoes': 4.50,  # per pound
            'chicken': 18.00,  # per bird
            'pork': 10.00,  # per pound
            'honey': 15.00,  # per jar
            'lettuce': 3.00,  # per head
            'herbs': 4.00,  # per bunch
        }
        
        price_per_unit = prices.get(item, 5.00)
        return round(price_per_unit * qty, 2)
    
    def process_payment(self, order_id: str, amount: float) -> str:
        """Process payment (local, zero-cost simulation)."""
        try:
            payment_record = {
                'order_id': order_id,
                'amount': amount,
                'status': 'completed',
                'method': 'local_cash',
                'timestamp': datetime.now().isoformat(),
                'transaction_id': f'TXN{order_id}'
            }
            
            self.payments.append(payment_record)
            self.save('payments.json')
            
            return 'completed'
        except (ValueError, KeyError) as e:
            logger.error(f"Payment processing validation failed: {e}")
            return 'pending'
        except Exception as e:
            logger.error(f"Payment processing failed: {e}", exc_info=True)
            return 'pending'
    
    # ——— TRACKING & LOGISTICS ———
    def update_tracking(self, order_id: str, status: str):
        """Update order tracking."""
        if order_id not in self.tracking:
            self.tracking[order_id] = {}
        
        self.tracking[order_id] = {
            'status': status,
            'updated': datetime.now().isoformat(),
            'carrier': 'USPS Ground',
            'eta': self.estimate_delivery(order_id)
        }
        
        self.save('tracking.json')
    
    def estimate_delivery(self, order_id: str) -> str:
        """Estimate delivery date."""
        # Find order
        order = None
        for o in self.orders:
            if o['id'] == order_id:
                order = o
                break
        
        if not order:
            return datetime.now().strftime('%a, %m/%d')
        
        # Beef ships overnight (frozen)
        if 'beef' in order['item'] or 'steak' in order['item']:
            eta = datetime.now() + timedelta(days=1)
        # Eggs and castings ship 2-day
        elif 'egg' in order['item'] or 'casting' in order['item']:
            eta = datetime.now() + timedelta(days=2)
        # Everything else ships 3-5 day
        else:
            eta = datetime.now() + timedelta(days=3)
        
        return eta.strftime('%a, %m/%d')
    
    def track_order(self, msg: str):
        """Track an order."""
        # Extract order ID
        order_id = None
        id_match = re.search(r'(\d{5})', msg)
        if id_match:
            order_id = id_match.group(1)
        else:
            # Try to find any number
            num_match = re.search(r'\b(\d+)\b', msg)
            if num_match:
                order_id = num_match.group(1).zfill(5)
        
        if not order_id:
            self.speak('What is your order number? Say track 00001.')
            return
        
        # Find order
        order = None
        for o in self.orders:
            if o['id'] == order_id:
                order = o
                break
        
        if not order:
            self.speak(f'Order {order_id} not found. Check your order number.')
            return
        
        # Get tracking info
        tracking_info = self.tracking.get(order_id, {})
        status = tracking_info.get('status', 'unknown')
        eta = tracking_info.get('eta', 'TBD')
        carrier = tracking_info.get('carrier', 'USPS Ground')
        
        qty = order['qty']
        item = order['item']
        self.speak(f'Order {order_id}: {qty} {item}, status {status}, ETA {eta}, carrier {carrier}.')
        print(f"\n  Order ID: {order_id}")
        print(f"  Item: {qty} {item}")
        print(f"  Status: {status.title()}")
        print(f"  Carrier: {carrier}")
        print(f"  ETA: {eta}")
        print()
    
    def monitor_shipments(self):
        """Monitor shipments in background."""
        while self.monitoring:
            try:
                for order in self.orders:
                    if order.get('status') == 'packed':
                        # Simulate scan - update to shipped
                        order['status'] = 'shipped'
                        self.update_tracking(order['id'], 'shipped')
                        self.save('orders.jsonl')
                        break
                time.sleep(3600)  # Check hourly
            except Exception as e:
                logger.error(f"Monitoring error: {e}", exc_info=True)
                time.sleep(60)
    
    # ——— PRINT LABELS ———
    def print_label(self, order_id: str):
        """Print shipping label."""
        # Find order
        order = None
        for o in self.orders:
            if o['id'] == order_id:
                order = o
                break
        
        if not order:
            return
        
        item = order['item'].upper()
        qty = order['qty']
        tracking_info = self.tracking.get(order_id, {})
        status = tracking_info.get('status', 'shipped').title()
        eta = tracking_info.get('eta', 'TBD')
        
        label = f"""
=== SHIPPING LABEL ===
ORDER: {order_id}
{qty} {item}
FROM: RED POST FARMS LLC
MONTE VISTA, CO 81144

TO: {status}
ETA: {eta}
==================
"""
        print(label)
        
        # Save label to file
        label_file = ROOT / 'labels' / f'label_{order_id}.txt'
        label_file.parent.mkdir(parents=True, exist_ok=True)
        with open(label_file, 'w', encoding='utf-8') as f:
            f.write(label)
    
    # ——— PORTAL WEBHOOK ———
    def portal_webhook(self):
        """Listen for order POSTs from local frontend - improved reliability."""
        if not REQUESTS_AVAILABLE:
            logger.warning("requests not available, webhook disabled")
            return
        
        retry_count = 0
        max_retries = 3
        
        while self.monitoring:
            try:
                # Listen on localhost:3001 with improved error handling
                response = requests.get('http://localhost:3001/incoming', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('type') == 'order':
                        self.handle_order(data.get('msg', ''))
                    retry_count = 0  # Reset on success
                else:
                    retry_count += 1
            except requests.exceptions.ConnectionError:
                # Connection failed - retry with backoff
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2 ** retry_count)  # Exponential backoff
                else:
                    time.sleep(30)  # Longer wait after max retries
                    retry_count = 0
            except requests.exceptions.Timeout:
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(1)
            except requests.exceptions.RequestException as e:
                logger.warning(f"Webhook request error: {e}")
                retry_count += 1
                time.sleep(5)
            except Exception as e:
                logger.error(f"Webhook error: {e}", exc_info=True)
                retry_count += 1
                time.sleep(5)
            
            if retry_count == 0:
                time.sleep(5)  # Normal check interval
    
    def status(self):
        """Report system status."""
        total_orders = len(self.orders)
        pending = sum(1 for o in self.orders if o.get('status') == 'packed')
        shipped = sum(1 for o in self.orders if o.get('status') == 'shipped')
        
        self.speak(f'Chatbot plus logistics live. {total_orders} total orders. {pending} packed. {shipped} shipped. Inventory auto-sync active.')
        print(f"\n  Total Orders: {total_orders}")
        print(f"  Pending: {pending}")
        print(f"  Shipped: {shipped}")
        print(f"  Inventory: Auto-sync active")
        print()

if __name__ == '__main__':
    bot = SalesBot()
    
    # Start webhook in background
    if REQUESTS_AVAILABLE:
        threading.Thread(target=bot.portal_webhook, daemon=True).start()
    
    print("=" * 60)
    print("SALESBOT + LOGISTICS HUB 2026")
    print("=" * 60)
    print("\nCommands:")
    print("  > SalesBot, order 10 lb castings")
    print("  > SalesBot, what do you have")
    print("  > SalesBot, track 00001")
    print("  > SalesBot, status")
    print("  > quit")
    print()
    
    while True:
        try:
            user = 'guest'
            msg = input(f'{user}> ').strip()
            
            if not msg:
                continue
            
            if msg.lower() in ['quit', 'exit', 'q']:
                bot.monitoring = False
                bot.speak('SalesBot offline. Orders still processing.')
                break
            
            if 'status' in msg.lower():
                bot.status()
            else:
                bot.chat(user, msg)
        
        except KeyboardInterrupt:
            bot.monitoring = False
            bot.speak('SalesBot offline.')
            break
        except (ValueError, KeyError) as e:
            logger.error(f"Input processing error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)

