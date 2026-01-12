# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# D:\RPF_BRAIN\The Gatekeeper\self_learn.py
# Self-learning system - scans all scripts, logs, voice, new files
# Uses Ollama to extract insights and build knowledge base

import os
import json
import subprocess
import time
import hashlib
import sys
import io
from pathlib import Path
from datetime import datetime, timedelta

# Add Sentence Transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Add ChromaDB for vector storage
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
LOG_DIR = BRAIN / 'Archived' / 'learning'
KNOWLEDGE_DB = LOG_DIR / 'gatekeeper_knowledge.json'
CHROMA_DB_PATH = LOG_DIR / "chroma_db"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Initialize Sentence Transformers and ChromaDB if available
embedding_model = None
chroma_client = None
chroma_collection = None

if SENTENCE_TRANSFORMERS_AVAILABLE and CHROMADB_AVAILABLE:
    try:
        # Initialize embedding model
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, fast model
        
        # Initialize ChromaDB client
        chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_DB_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        chroma_collection = chroma_client.get_or_create_collection(
            name="self_learn_knowledge",
            metadata={"description": "Self-learning knowledge base with embeddings"}
        )
        print("  ✅ Sentence Transformers and ChromaDB ready for self-learning")
    except Exception as e:
        print(f"  ⚠️  Vector storage initialization failed: {e}")
        print("  ℹ️  Using JSON-only storage (fallback)")
        embedding_model = None
        chroma_client = None
        chroma_collection = None

def hash_file(path):
    """Calculate SHA256 hash of file."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception as e:
        print(f"Error hashing {path}: {e}")
        return None

def ollama_summarize(text, prompt_template):
    """Run Ollama to summarize/extract insights."""
    try:
        # Check if Ollama is available
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("Ollama not found. Install from: https://ollama.ai/")
        return None
    
    try:
        # Use Ollama to process text
        # Format: echo "text" | ollama run llama3 "prompt"
        cmd = f'echo "{text[:2000]}" | ollama run llama3 "{prompt_template}"'
        result = subprocess.check_output(
            cmd,
            shell=True,
            text=True,
            timeout=60,
            stderr=subprocess.DEVNULL
        )
        return result.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, Exception) as e:
        print(f"Ollama processing failed: {e}")
        return None

def learn_from_scripts():
    """Learn from all Python scripts in Gatekeeper directory."""
    print("Learning from scripts...")
    knowledge = []
    
    for f in GATE.glob('*.py'):
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                code = file.read()
            
            summary = ollama_summarize(
                code,
                "Summarize what this code does in one sentence."
            )
            
            if summary:
                knowledge.append({
                    'type': 'script',
                    'path': str(f.relative_to(BRAIN)),
                    'digest': hash_file(f),
                    'summary': summary,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Error processing script {f}: {e}")
            continue
    
    return knowledge

def learn_from_logs():
    """Learn from log files."""
    print("Learning from logs...")
    knowledge = []
    
    for log in LOG_DIR.glob('*.log'):
        try:
            with open(log, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[-500:]  # last 500 lines
            
            if not lines:
                continue
            
            log_text = '\n'.join(lines)
            summary = ollama_summarize(
                log_text,
                "Give a concise system status from these logs in one sentence."
            )
            
            if summary:
                knowledge.append({
                    'type': 'log',
                    'file': log.name,
                    'last_lines': lines[-10],  # Store last 10 lines only
                    'status': summary,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Error processing log {log}: {e}")
            continue
    
    return knowledge

def learn_from_voice():
    """Learn from voice log files."""
    print("Learning from voice logs...")
    knowledge = []
    
    voice_log_dir = BRAIN / 'Archived' / 'voice_log'
    if not voice_log_dir.exists():
        return knowledge
    
    for txt in voice_log_dir.glob('voice_log_*.txt'):
        try:
            with open(txt, 'r', encoding='utf-8', errors='ignore') as f:
                convo = f.read()[-2000:]  # last 2000 chars
            
            if not convo.strip():
                continue
            
            insight = ollama_summarize(
                convo,
                "What patterns does the user show here? One sentence."
            )
            
            if insight:
                knowledge.append({
                    'type': 'voice',
                    'file': txt.name,
                    'insight': insight,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Error processing voice log {txt}: {e}")
            continue
    
    return knowledge

def learn_from_new_files():
    """Learn from new files in Archived directory."""
    print("Learning from new files...")
    knowledge = []
    
    archived = BRAIN / 'Archived'
    if not archived.exists():
        return knowledge
    
    # Get files from last 7 days
    cutoff = datetime.now() - timedelta(days=7)
    
    for f in archived.rglob('*'):
        if not f.is_file():
            continue
        
        if f.suffix.lower() not in ['.pdf', '.txt', '.docx', '.md']:
            continue
        
        try:
            # Check if file is new (modified in last 7 days)
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                continue
            
            # Extract text
            if f.suffix.lower() == '.pdf':
                # Try pdftotext if available
                try:
                    text = subprocess.check_output(
                        ['pdftotext', str(f), '-'],
                        text=True,
                        timeout=30,
                        stderr=subprocess.DEVNULL
                    )[:2048]
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    text = f"[PDF file: {f.name}]"
            else:
                with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                    text = file.read()[:2048]
            
            if not text.strip():
                continue
            
            key = ollama_summarize(
                text,
                "Extract one key insight from this document in one sentence."
            )
            
            if key:
                knowledge.append({
                    'type': 'new_file',
                    'path': str(f.relative_to(BRAIN)),
                    'insight': key,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Error processing file {f}: {e}")
            continue
    
    return knowledge

# USER APPROVAL GATE
def print_weekly_summary(changes):
    """Display weekly learning report and get user approval."""
    print("\n🧠 WEEKLY LEARNING REPORT – AWAITING APPROVAL")
    print("=" * 50)
    
    if changes.get('scripts'):
        print("\n📝 SCRIPT CHANGES:")
        for c in changes['scripts']:
            print(f"  {c['path']}")
            print(f"  → {c['summary']}")
    
    if changes.get('logs'):
        print("\n📊 NEW SYSTEM EVENTS:")
        for c in changes['logs']:
            print(f"  {c['file']}: {c['status']}")
    
    if changes.get('voice'):
        print("\n🎤 USER PATTERN SHIFT:")
        for c in changes['voice']:
            print(f"  {c['insight']}")
    
    if changes.get('new_files'):
        print("\n📚 NEW KNOWLEDGE ADDED:")
        for c in changes['new_files']:
            print(f"  {c['path']} → {c['insight']}")
    
    if not any(changes.values()):
        print("\n  No new changes detected this week.")
    
    print("\n")
    response = input("> Approve learning? (yes/no): ").strip().lower()
    return response == 'yes'

def update_knowledge():
    """Update the knowledge database with all learned information."""
    print("=" * 60)
    print("🧠 Gatekeeper learning... scanning all systems.")
    print("=" * 60)
    
    all_knowledge = []
    
    # Learn from all sources
    all_knowledge.extend(learn_from_scripts())
    all_knowledge.extend(learn_from_logs())
    all_knowledge.extend(learn_from_voice())
    all_knowledge.extend(learn_from_new_files())
    
    # Load existing knowledge
    existing_knowledge = []
    if KNOWLEDGE_DB.exists():
        try:
            with open(KNOWLEDGE_DB, 'r', encoding='utf-8') as f:
                existing_knowledge = json.load(f)
        except Exception as e:
            print(f"Error loading existing knowledge: {e}")
    
    # Merge new knowledge (avoid duplicates by digest/path)
    existing_digests = {k.get('digest') for k in existing_knowledge if 'digest' in k}
    existing_paths = {k.get('path') for k in existing_knowledge if 'path' in k}
    
    for item in all_knowledge:
        # Check if already exists
        if item.get('digest') in existing_digests:
            continue
        if item.get('path') in existing_paths:
            continue
        
        existing_knowledge.append(item)
    
    # Save as canonical knowledge base (JSON - always for backward compatibility)
    with open(KNOWLEDGE_DB, 'w', encoding='utf-8') as f:
        json.dump(existing_knowledge, f, indent=2, ensure_ascii=False)
    
    # Also store in ChromaDB vector database (if available)
    if chroma_collection and embedding_model and all_knowledge:
        try:
            # Generate embeddings for new knowledge
            texts = []
            metadatas = []
            ids = []
            
            for item in all_knowledge:
                # Create text representation
                text = ""
                if 'summary' in item:
                    text = item['summary']
                elif 'status' in item:
                    text = item['status']
                elif 'insight' in item:
                    text = item['insight']
                
                if text:
                    texts.append(text)
                    metadatas.append({
                        'type': item.get('type', 'unknown'),
                        'path': item.get('path', item.get('file', '')),
                        'timestamp': item.get('timestamp', datetime.now().isoformat())
                    })
                    ids.append(f"learn_{hashlib.md5(text.encode()).hexdigest()}")
            
            if texts:
                # Generate embeddings
                embeddings = embedding_model.encode(texts, show_progress_bar=True)
                
                # Add to ChromaDB
                chroma_collection.add(
                    embeddings=embeddings.tolist(),
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                
                print(f"  ✅ Stored {len(texts)} insights in ChromaDB vector database")
        except Exception as e:
            print(f"  ⚠️  ChromaDB storage failed: {e}")
            print("  ℹ️  Using JSON-only storage (fallback)")
    
    new_count = len(all_knowledge)
    total_count = len(existing_knowledge)
    
    print(f"\n✅ Learned. {new_count} new facts. {total_count} total facts. Knowledge live.")
    print(f"Knowledge saved to: {KNOWLEDGE_DB}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--weekly':
        print("Weekly learning mode activated.")
        print("Running every 7 days...")
        while True:
            print("\n" + "=" * 60)
            print("🧠 Gatekeeper learning... scanning all systems.")
            print("=" * 60)
            
            # Collect all new knowledge
            raw_knowledge = []
            raw_knowledge.extend(learn_from_scripts())
            raw_knowledge.extend(learn_from_logs())
            raw_knowledge.extend(learn_from_voice())
            raw_knowledge.extend(learn_from_new_files())
            
            # Filter out existing knowledge
            existing_knowledge = []
            if KNOWLEDGE_DB.exists():
                try:
                    with open(KNOWLEDGE_DB, 'r', encoding='utf-8') as f:
                        existing_knowledge = json.load(f)
                except Exception as e:
                    print(f"Error loading existing knowledge: {e}")
            
            existing_digests = {k.get('digest') for k in existing_knowledge if 'digest' in k}
            existing_paths = {k.get('path') for k in existing_knowledge if 'path' in k}
            
            # Filter to only new knowledge
            new_knowledge = []
            for item in raw_knowledge:
                if item.get('digest') in existing_digests:
                    continue
                if item.get('path') in existing_paths:
                    continue
                new_knowledge.append(item)
            
            # Show summary and get approval
            approved = print_weekly_summary({
                'scripts': [k for k in new_knowledge if k.get('type') == 'script'],
                'logs': [k for k in new_knowledge if k.get('type') == 'log'],
                'voice': [k for k in new_knowledge if k.get('type') == 'voice'],
                'new_files': [k for k in new_knowledge if k.get('type') == 'new_file']
            })
            
            if approved:
                # Merge and save
                existing_knowledge.extend(new_knowledge)
                with open(KNOWLEDGE_DB, 'w', encoding='utf-8') as f:
                    json.dump(existing_knowledge, f, indent=2, ensure_ascii=False)
                print("\n✅ Learning approved. Gatekeeper upgraded.")
            else:
                print("\n❌ Canceled. No change applied.")
            
            print(f"\nNext learning cycle in 7 days...")
            time.sleep(7 * 24 * 60 * 60)  # 1 week
    else:
        update_knowledge()

# RPF-GK-OWNER-2026-7A3F9B2C (ownership signature)

