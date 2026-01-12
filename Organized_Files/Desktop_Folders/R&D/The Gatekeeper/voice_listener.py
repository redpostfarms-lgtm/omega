# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# Voice listener with voiceprint authentication
# Only responds to the master voice

import speech_recognition as sr
from voiceprint_auth import is_me
import sys
import io
import subprocess
import pyttsx3
import re
import time
import json
from pathlib import Path
from typing import Optional

# Add Vosk support for offline recognition
try:
    import vosk
    import pyaudio
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

# Import new voice modules
try:
    sys.path.insert(0, str(GATE))
    from voice_stt_offline import OfflineSTT, init_offline_stt
    from voice_tts_offline import OfflineTTS, init_offline_tts
    from voice_intent import IntentRecognizer
    from voice_skills import VoiceSkills
    from voice_multilang import MultiLanguage
    from voice_noise_cancel import NoiseCancellation
    VOICE_MODULES_AVAILABLE = True
except ImportError:
    VOICE_MODULES_AVAILABLE = False

# Initialize voice modules
if VOICE_MODULES_AVAILABLE:
    try:
        intent_recognizer = IntentRecognizer()
        voice_skills = VoiceSkills()
        multilang = MultiLanguage()
        noise_cancel = NoiseCancellation()
        offline_stt = None  # Will be initialized if model available
        offline_tts = init_offline_tts()
    except (ImportError, AttributeError, Exception) as e:
        print(f"  ⚠️  Voice module initialization error: {e}")
        intent_recognizer = None
        voice_skills = None
        multilang = None
        noise_cancel = None
        offline_stt = None
        offline_tts = None
else:
    intent_recognizer = None
    voice_skills = None
    multilang = None
    noise_cancel = None
    offline_stt = None
    offline_tts = None

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
VOSK_MODEL_PATH = GATE / 'models' / 'vosk' / 'vosk-model-small-en-us-0.15'

# Initialize Vosk if available
vosk_model = None
vosk_rec = None
if VOSK_AVAILABLE:
    try:
        if VOSK_MODEL_PATH.exists():
            vosk_model = vosk.Model(str(VOSK_MODEL_PATH))
            vosk_rec = vosk.KaldiRecognizer(vosk_model, 16000)
            print("  ✅ Vosk offline recognition ready")
        else:
            print(f"  ℹ️  Vosk model not found at {VOSK_MODEL_PATH}")
            print("  ℹ️  Download from: https://alphacephei.com/vosk/models")
            print("  ℹ️  Using speech_recognition fallback")
    except Exception as e:
        print(f"  ⚠️  Vosk initialization failed: {e}")
        print("  ℹ️  Using speech_recognition fallback")

def say(text: str) -> None:
    """
    Speak text using voice tuner settings.
    
    Args:
        text: The text to speak
    """
    try:
        from voice_tuner import load_tune, apply_tune
        tune = load_tune()
        apply_tune(tune)
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 110)
        engine.setProperty('volume', 0.7)
        engine.say(text)
        engine.runAndWait()
    except (ImportError, AttributeError, RuntimeError) as e:
        print(f"  ⚠️  TTS error: {e}")
        print(text)

def handle_planetary_search(topic: str) -> None:
    """
    Handle planetary search - scrapes entire open internet.
    
    Args:
        topic: The search topic
    """
    print(f"\n{'='*60}")
    print(f"GATEKEEPER - PLANETARY SEARCH")
    print(f"{'='*60}\n")
    
    say(f"The doors of knowledge opens. Worldwide deep search launched.")
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(GATE / 'planetary_search.py'),
                topic
            ],
            cwd=str(GATE),
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour max for comprehensive search
        )
        
        if result.returncode == 0:
            # Extract stats from output
            output = result.stdout
            facts_match = re.search(r'(\d+) new facts absorbed', output)
            repos_match = re.search(r'(\d+) repos', output)
            papers_match = re.search(r'(\d+) papers', output)
            docs_match = re.search(r'(\d+) docs', output)
            
            facts = facts_match.group(1) if facts_match else "0"
            repos = repos_match.group(1) if repos_match else "0"
            papers = papers_match.group(1) if papers_match else "0"
            docs = docs_match.group(1) if docs_match else "0"
            
            confirmation = f"Worldwide deep search complete. {facts} new facts absorbed."
            print(f"\n✅ {confirmation}")
            say(confirmation)
        else:
            print(f"  ⚠️  Search had issues: {result.stderr[:200]}")
            say("Search complete with some issues.")
    except Exception as e:
        print(f"  ❌ Search error: {e}")
        say("Search error occurred.")

def handle_go_to_school(topic: str) -> None:
    """
    Handle 'go to school/college on [topic]' command - triggers planetary search.
    
    Args:
        topic: The topic to learn about
    """
    handle_planetary_search(topic)

def handle_council(problem: str) -> None:
    """
    Handle Agent Council mode (v2).
    
    Args:
        problem: The problem to solve
    """
    print(f"\n{'='*60}")
    print(f"AGENT COUNCIL MODE v2")
    print(f"{'='*60}\n")
    
    try:
        # Use v2 for better debate and voting
        result = subprocess.run(
            [
                sys.executable,
                str(GATE / 'agent_council_v2.py'),
                problem
            ],
            cwd=str(GATE),
            timeout=600  # 10 minutes max for 3 rounds
        )
        if result.returncode == 0:
            print("\n✅ Council session complete.")
        else:
            print("\n⚠️  Council session had issues")
    except Exception as e:
        print(f"\n❌ Council error: {e}")

def handle_hive(problem: str) -> None:
    """
    Handle hive hibernation system - agents multiply, inherit, hibernate.
    
    Args:
        problem: The problem to solve
    """
    print(f"\n{'='*60}")
    print(f"GATEKEEPER – HIVE HIBERNATION MODE")
    print(f"{'='*60}\n")
    print(f"Problem: {problem}\n")
    
    try:
        # Use final hibernation system
        result = subprocess.run(
            [
                sys.executable,
                str(GATE / 'hive_hibernation_final.py'),
                problem
            ],
            cwd=str(GATE),
            timeout=1800  # 30 minutes max for hive
        )
        if result.returncode == 0:
            print("\n✅ Hive session complete. Agents hibernating.")
        else:
            print("\n⚠️  Hive session had issues")
    except Exception as e:
        print(f"\n❌ Hive error: {e}")

def handle_white_page() -> None:
    """Handle white page generation."""
    print(f"\n{'='*60}")
    print(f"WHITE PAGE GENERATOR")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(GATE / 'white_page.py')
            ],
            cwd=str(GATE),
            timeout=30
        )
        if result.returncode == 0:
            print("\n✅ White page created.")
        else:
            print("\n⚠️  White page creation had issues")
    except Exception as e:
        print(f"\n❌ White page error: {e}")

def handle_send_white_page() -> None:
    """Handle send white page (with download link)."""
    print(f"\n{'='*60}")
    print(f"WHITE PAGE - SEND MODE")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(GATE / 'white_page.py'),
                'send'
            ],
            cwd=str(GATE),
            timeout=30
        )
        if result.returncode == 0:
            print("\n✅ White page created. Link copied to clipboard.")
        else:
            print("\n⚠️  White page creation had issues")
    except Exception as e:
        print(f"\n❌ White page error: {e}")

def handle_game_hub() -> None:
    """Handle game hub launch."""
    print(f"\n{'='*60}")
    print(f"GAME HUB FINAL v3")
    print(f"{'='*60}\n")
    
    say("The doors of knowledge opens. Opening game hub.")
    
    try:
        # Try final version first, fallback to regular
        hub_file = GATE / 'game_hub_final.py'
        if not hub_file.exists():
            hub_file = GATE / 'game_hub.py'
        
        result = subprocess.run(
            [
                sys.executable,
                str(hub_file)
            ],
            cwd=str(GATE),
            timeout=None  # No timeout - user controls when to quit
        )
        if result.returncode == 0:
            print("\n✅ Game hub closed.")
        else:
            print("\n⚠️  Game hub had issues")
    except Exception as e:
        print(f"\n❌ Game hub error: {e}")

def handle_replay_full_game() -> None:
    """Handle replay full AI vs AI game."""
    print(f"\n{'='*60}")
    print(f"CHESS REPLAY - Full Game")
    print(f"{'='*60}\n")
    
    say("The doors of knowledge opens. Replaying AI versus AI chess. Like watching a security tape.")
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(GATE / 'chess_replay.py'),
                'full'
            ],
            cwd=str(GATE),
            timeout=None
        )
        if result.returncode == 0:
            print("\n✅ Replay complete.")
        else:
            print("\n⚠️  Replay had issues")
    except Exception as e:
        print(f"\n❌ Replay error: {e}")

def handle_replay_moves(n: int = 10) -> None:
    """
    Handle replay last N moves.
    
    Args:
        n: Number of moves to replay (default: 10)
    """
    print(f"\n{'='*60}")
    print(f"CHESS REPLAY - Last {n} Moves")
    print(f"{'='*60}\n")
    
    say(f"The doors of knowledge opens. Replaying last {n} moves. Showing evolution.")
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(GATE / 'chess_replay.py'),
                'last',
                str(n)
            ],
            cwd=str(GATE),
            timeout=None
        )
        if result.returncode == 0:
            print(f"\n✅ Last {n} moves replayed.")
        else:
            print("\n⚠️  Replay had issues")
    except Exception as e:
        print(f"\n❌ Replay error: {e}")

def handle_playbook(command: str = "") -> None:
    """
    Handle Marketing Playbook - 57 battle-tested hooks.
    
    Args:
        command: Optional command string
    """
    print(f"\n{'='*60}")
    print(f"MARKETING PLAYBOOK 2026")
    print(f"{'='*60}\n")
    
    say("Playbook loaded. Say your product.")
    
    try:
        playbook_path = Path(r'D:\RPF_BRAIN\Sales\Marketing_Playbook.py')
        if not playbook_path.exists():
            say("Playbook not found. Please deploy first.")
            return
        
        if command:
            # Run with command
            result = subprocess.run(
                [
                    sys.executable,
                    str(playbook_path)
                ],
                cwd=str(playbook_path.parent),
                input=f"{command}\nquit\n",
                text=True,
                timeout=30
            )
        else:
            # Launch interactive mode
            result = subprocess.run(
                [
                    sys.executable,
                    str(playbook_path)
                ],
                cwd=str(playbook_path.parent),
                timeout=None
            )
        
        if result.returncode == 0:
            print("\n✅ Playbook complete.")
        else:
            print("\n⚠️  Playbook had issues")
    except Exception as e:
        print(f"\n❌ Playbook error: {e}")
        say("Playbook error occurred.")

def handle_salesbot(command: str = "") -> None:
    """
    Handle SalesBot - chatbot and logistics.
    
    Args:
        command: Optional command string
    """
    print(f"\n{'='*60}")
    print(f"SALESBOT + LOGISTICS HUB 2026")
    print(f"{'='*60}\n")
    
    say("SalesBot plus logistics live. Orders rolling. Tracking pinging.")
    
    try:
        salesbot_path = Path(r'D:\RPF_BRAIN\Sales\ChatbotLogistics.py')
        if not salesbot_path.exists():
            say("SalesBot not found. Please deploy first.")
            return
        
        if command:
            # Run with command
            result = subprocess.run(
                [
                    sys.executable,
                    str(salesbot_path)
                ],
                cwd=str(salesbot_path.parent),
                input=f"{command}\nquit\n",
                text=True,
                timeout=30
            )
        else:
            # Launch interactive mode
            result = subprocess.run(
                [
                    sys.executable,
                    str(salesbot_path)
                ],
                cwd=str(salesbot_path.parent),
                timeout=None
            )
        
        if result.returncode == 0:
            print("\n✅ SalesBot complete.")
        else:
            print("\n⚠️  SalesBot had issues")
    except Exception as e:
        print(f"\n❌ SalesBot error: {e}")
        say("SalesBot error occurred.")

def handle_saleshub(product: str = "") -> None:
    """
    Handle SalesHub - marketing agent.
    
    Args:
        product: Optional product name
    """
    print(f"\n{'='*60}")
    print(f"SALESHUB 2026 - Marketing Agent")
    print(f"{'='*60}\n")
    
    say("SalesHub online. Say your product.")
    
    try:
        saleshub_path = Path(r'D:\RPF_BRAIN\Sales\SalesHub.py')
        if not saleshub_path.exists():
            say("SalesHub not found. Please deploy first.")
            return
        
        if product:
            # Run with product command
            result = subprocess.run(
                [
                    sys.executable,
                    str(saleshub_path)
                ],
                cwd=str(saleshub_path.parent),
                input=f"SalesHub, pitch {product}\nquit\n",
                text=True,
                timeout=30
            )
        else:
            # Launch interactive mode
            result = subprocess.run(
                [
                    sys.executable,
                    str(saleshub_path)
                ],
                cwd=str(saleshub_path.parent),
                timeout=None
            )
        
        if result.returncode == 0:
            print("\n✅ SalesHub complete.")
        else:
            print("\n⚠️  SalesHub had issues")
    except Exception as e:
        print(f"\n❌ SalesHub error: {e}")
        say("SalesHub error occurred.")

def handle_fusion(command: str) -> None:
    """
    Handle FUSION mode - multi-model orchestration.
    
    Args:
        command: The command to process
    """
    print(f"\n{'='*60}")
    print(f"GATEKEEPER FUSION - Multi-Model Brain")
    print(f"{'='*60}\n")
    
    say("The doors of knowledge opens. Four brains awaken. Grok, Cursor, DeepSeek, and Llama are ready.")
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(GATE / 'gatekeeper_fusion.py'),
                command
            ],
            cwd=str(GATE),
            timeout=600  # 10 minutes max for fusion
        )
        if result.returncode == 0:
            print("\n✅ Fusion complete. All four brains have spoken.")
            say("Fusion complete. Code is ready.")
        else:
            print("\n⚠️  Fusion had issues")
            say("Fusion complete with some issues.")
    except Exception as e:
        print(f"\n❌ Fusion error: {e}")
        say("Fusion error occurred.")

def handle_farmos(command: str = "") -> None:
    """
    Handle FarmOS 2026 - unified inter-agent neural farm OS.
    
    Args:
        command: Optional command string
    """
    print(f"\n{'='*60}")
    print(f"FARMOS 2026 – FINAL MASTER EDITION")
    print(f"{'='*60}\n")
    
    say("FarmOS 2026 fully awake. All agents online. Knowledge base: 18 TB and growing.")
    
    try:
        farmos_path = GATE / 'FarmOS_2026.py'
        if not farmos_path.exists():
            say("FarmOS not found. Please deploy first.")
            return
        
        if command:
            # Run with command (non-interactive)
            result = subprocess.run(
                [
                    sys.executable,
                    str(farmos_path)
                ],
                cwd=str(GATE),
                input=f"{command}\nquit\n",
                text=True,
                timeout=300  # 5 minutes max
            )
        else:
            # Launch interactive mode
            result = subprocess.run(
                [
                    sys.executable,
                    str(farmos_path)
                ],
                cwd=str(GATE),
                timeout=None  # No timeout - user controls when to quit
            )
        
        if result.returncode == 0:
            print("\n✅ FarmOS session complete.")
        else:
            print("\n⚠️  FarmOS had issues")
    except Exception as e:
        print(f"\n❌ FarmOS error: {e}")
        say("FarmOS error occurred.")

def _handle_council_command(text_lower: str) -> bool:
    """Handle council-related commands. Returns True if handled."""
    if "council" not in text_lower and "agent council" not in text_lower:
        return False
    if " on " in text_lower or "solve" in text_lower:
        if " on " in text_lower:
            problem = text_lower.split(" on ")[-1].strip()
        elif "solve" in text_lower:
            problem = text_lower.split("solve")[-1].strip()
        else:
            problem = text_lower.replace("council", "").replace("agent", "").strip()
        if problem:
            handle_council(problem)
            return True
    else:
        say("The doors of knowledge opens. What problem should the council solve?")
        return True
    return False


def _handle_solve_command(text_lower: str) -> bool:
    """Handle solve (hive) commands. Returns True if handled."""
    if "solve" not in text_lower or "council" in text_lower:
        return False
    parts = text_lower.split("solve", 1)
    if len(parts) > 1:
        problem = parts[1].strip()
        problem = problem.lstrip("why ").lstrip("how ").lstrip("the ")
        problem = problem.lstrip("a ").lstrip("an ")
        if problem and len(problem) > 3:
            handle_hive(problem)
            return True
    return False


def _handle_hive_command(text_lower: str) -> bool:
    """Handle hive commands. Returns True if handled."""
    if "hive" not in text_lower:
        return False
    if "solve" in text_lower:
        problem = text_lower.split("solve")[-1].strip()
        if problem:
            handle_hive(problem)
            return True
    else:
        say("The doors of knowledge opens. What problem should the hive solve?")
        return True
    return False


def _handle_search_command(text_lower: str) -> bool:
    """Handle search commands. Returns True if handled."""
    search_commands = ["search", "look up", "lookup", "find", "research"]
    for cmd in search_commands:
        if cmd in text_lower:
            parts = text_lower.split(cmd, 1)
            if len(parts) > 1:
                topic = parts[1].strip()
                topic = re.sub(r'\s+(for|about|on|regarding)$', '', topic)
                if topic:
                    handle_planetary_search(topic)
                    return True
            else:
                say("The doors of knowledge opens. What should I search for?")
                return True
    return False


def _handle_school_command(text_lower: str) -> bool:
    """Handle go to school/college commands. Returns True if handled."""
    if "go to school" not in text_lower and "go to college" not in text_lower:
        return False
    if " on " in text_lower:
        topic = text_lower.split(" on ")[-1].strip()
        if topic:
            handle_go_to_school(topic)
            return True
    else:
        say("The doors of knowledge opens. What topic should I learn?")
        return True
    return False


def _handle_white_page_command(text_lower: str) -> bool:
    """Handle white page commands. Returns True if handled."""
    if "white page" not in text_lower:
        return False
    if "send" in text_lower:
        handle_send_white_page()
    else:
        handle_white_page()
    return True


def _handle_game_hub_command(text_lower: str) -> bool:
    """Handle game hub commands. Returns True if handled."""
    keywords = ["game hub", "open game hub", "resume game"]
    if any(keyword in text_lower for keyword in keywords):
        handle_game_hub()
        return True
    return False


def _handle_replay_command(text_lower: str) -> bool:
    """Handle replay commands. Returns True if handled."""
    if "replay" not in text_lower:
        return False
    if "last" in text_lower and "move" in text_lower:
        num_match = re.search(r'(\d+)\s*(?:move|moves)', text_lower)
        n = int(num_match.group(1)) if num_match else 10
        handle_replay_moves(n)
        return True
    elif any(phrase in text_lower for phrase in ["ai vs ai", "aivsai", "ai versus ai"]):
        handle_replay_full_game()
        return True
    else:
        handle_replay_full_game()
        return True


def _handle_playbook_command(text_lower: str, text: str) -> bool:
    """Handle playbook commands. Returns True if handled."""
    if "playbook" not in text_lower and "marketing playbook" not in text_lower:
        return False
    if "pitch" in text_lower or "sell" in text_lower:
        handle_playbook(text)
    else:
        handle_playbook("")
    return True


def _handle_salesbot_command(text_lower: str, text: str) -> bool:
    """Handle salesbot commands. Returns True if handled."""
    if "salesbot" not in text_lower and "sales bot" not in text_lower:
        return False
    if "order" in text_lower or "track" in text_lower or "status" in text_lower:
        handle_salesbot(text)
    else:
        handle_salesbot("")
    return True


def _handle_saleshub_command(text_lower: str) -> bool:
    """Handle saleshub commands. Returns True if handled."""
    keywords = ["saleshub", "sales hub", "pitch", "sell"]
    if not any(keyword in text_lower for keyword in keywords):
        return False
    product = ""
    if "pitch" in text_lower:
        product = text_lower.split("pitch")[-1].strip()
    elif "sell" in text_lower:
        product = text_lower.split("sell")[-1].strip()
    elif "saleshub" in text_lower or "sales hub" in text_lower:
        split_keyword = "saleshub" if "saleshub" in text_lower else "sales hub"
        parts = text_lower.split(split_keyword, 1)
        if len(parts) > 1:
            product = parts[1].strip()
    product = product.lstrip("for ").lstrip("a ").lstrip("an ").lstrip("the ").strip()
    if product:
        handle_saleshub(product)
    else:
        handle_saleshub()
    return True


def _handle_farmos_command(text_lower: str, text: str) -> bool:
    """Handle FarmOS commands. Returns True if handled."""
    farmos_keywords = [
        "farmos", "farm os", "harriet", "hr", "bob", "build", "barn", "battery",
        "apothecary", "pest", "blight", "herb", "feedmaster", "feed", "chicken",
        "pig", "worm", "medical", "fall", "bleed", "cpr", "salesbot", "order",
        "beef", "egg", "pricemaster", "price", "pricing", "market", "optimal",
        "competitor"
    ]
    if any(keyword in text_lower for keyword in farmos_keywords):
        handle_farmos(text)
        return True
    return False


def _handle_code_command(text_lower: str, text: str) -> bool:
    """Handle code/write/build commands (FUSION). Returns True if handled."""
    code_keywords = ["write", "code", "build", "create", "program", "develop", "implement"]
    if any(keyword in text_lower for keyword in code_keywords):
        handle_fusion(text)
        return True
    return False


def handle_command(text: str) -> None:
    """
    Process the recognized command.
    
    Routes voice commands to appropriate handlers. Refactored to reduce
    complexity by breaking into smaller functions.
    
    Args:
        text: The recognized command text
    """
    text_lower = text.lower()
    print(f"Command: {text}")
    
    # Route to appropriate handler (order matters for some commands)
    handlers = [
        _handle_council_command,
        _handle_solve_command,
        _handle_hive_command,
        _handle_search_command,
        _handle_school_command,
        _handle_white_page_command,
        _handle_game_hub_command,
        _handle_replay_command,
        lambda tl, t=None: _handle_playbook_command(tl, text),
        lambda tl, t=None: _handle_salesbot_command(tl, text),
        _handle_saleshub_command,
        lambda tl, t=None: _handle_farmos_command(tl, text),
        lambda tl, t=None: _handle_code_command(tl, text),
    ]
    
    for handler in handlers:
        try:
            if handler(text_lower, text) if handler.__code__.co_argcount > 1 else handler(text_lower):
                return
        except Exception as e:
            print(f"Error in handler: {e}")
            continue
    
    # Default handling
    if "gatekeeper" in text_lower or "hey gatekeeper" in text_lower:
        print("The doors of knowledge opens.")
    else:
        print("Listening...")

def recognize_with_vosk(audio: sr.AudioData) -> Optional[str]:
    """
    Recognize speech using Vosk (offline) from speech_recognition AudioData.
    
    Args:
        audio: AudioData object from speech_recognition
        
    Returns:
        Recognized text or None if recognition fails
    """
    if not vosk_rec:
        return None
    
    try:
        # Convert AudioData to raw bytes for Vosk
        raw_data = audio.get_raw_data(convert_rate=16000, convert_width=2)
        
        # Process audio in chunks
        chunk_size = 4000
        full_text = ""
        
        for i in range(0, len(raw_data), chunk_size):
            chunk = raw_data[i:i+chunk_size]
            if vosk_rec.AcceptWaveform(chunk):
                result = json.loads(vosk_rec.Result())
                text = result.get('text', '')
                if text:
                    full_text = text
            elif vosk_rec.PartialResult():
                partial = json.loads(vosk_rec.PartialResult())
                # Can use for real-time feedback
        
        # Get final result
        if vosk_rec.AcceptWaveform(b''):
            result = json.loads(vosk_rec.Result())
            text = result.get('text', '')
            if text:
                full_text = text
        
        return full_text.lower() if full_text else None
    except Exception as e:
        print(f"  ⚠️  Vosk recognition error: {e}")
        return None

def recognize_speech(audio: sr.AudioData) -> Optional[str]:
    """
    Recognize speech with Vosk (offline) or fallback to speech_recognition.
    
    Args:
        audio: AudioData object from speech_recognition
        
    Returns:
        Recognized text or None if recognition fails
    """
    # Try Vosk first (offline)
    if vosk_rec:
        try:
            text = recognize_with_vosk(audio)
            if text:
                return text
        except Exception as e:
            print(f"  ⚠️  Vosk failed, using fallback: {e}")
    
    # Fallback to speech_recognition
    recognizer = sr.Recognizer()
    try:
        # Try offline first (PocketSphinx)
        try:
            return recognizer.recognize_sphinx(audio).lower()
        except (sr.UnknownValueError, OSError, AttributeError) as e:
            # Fallback to Google API (requires internet)
            try:
                return recognizer.recognize_google(audio).lower()
            except sr.RequestError as api_error:
                print(f"  ⚠️  Google API error: {api_error}")
                return None
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"  ⚠️  Speech recognition error: {e}")
        return None

def listen_forever() -> None:
    """
    Main listening loop with voiceprint authentication.
    
    Continuously listens for 'Hey, Gatekeeper' wake word and processes
    commands only from authenticated voice.
    """
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    print("=" * 60)
    print("Gatekeeper Voice Listener")
    print("=" * 60)
    if vosk_rec:
        print("Mode: Vosk (offline) + Speech Recognition (fallback)")
    else:
        print("Mode: Speech Recognition (Google API)")
    print("Listening for 'Hey, Gatekeeper'...")
    print("Only responds to master voice.\n")
    
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
    
    while True:
        try:
            with mic as source:
                print("Listening... (say 'Hey, Gatekeeper')")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            # Check if it's the master voice
            if is_me(audio):
                print("Voiceprint match. Processing...")
                try:
                    text = recognize_speech(audio)
                    if text and ("gatekeeper" in text or "hey gatekeeper" in text):
                        print("The doors of knowledge opens.")
                        handle_command(text)
                    else:
                        print("Command not recognized.")
                except Exception as e:
                    print(f"Recognition error: {e}")
            else:
                # Stranger — nothing. No sound. No log.
                print("Voiceprint mismatch. Ignoring.")
                pass
                
        except sr.WaitTimeoutError:
            continue
        except KeyboardInterrupt:
            print("\nStopping listener...")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

if __name__ == "__main__":
    listen_forever()

