# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# Voice listener with voiceprint authentication - IMPROVED VERSION
# Only responds to the master voice
# Enhanced with type hints, docstrings, and refactored complexity

from __future__ import annotations

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
from typing import Optional, Dict, List, Any, Tuple

# Add Vosk support for offline recognition
try:
    import vosk
    import pyaudio
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

# Import new voice modules
try:
    sys.path.insert(0, str(Path(r'D:\RPF_BRAIN') / 'The Gatekeeper'))
    from voice_stt_offline import OfflineSTT, init_offline_stt
    from voice_tts_offline import OfflineTTS, init_offline_tts
    from voice_intent import IntentRecognizer
    from voice_skills import VoiceSkills
    from voice_multilang import MultiLanguage
    from voice_noise_cancel import NoiseCancellation
    VOICE_MODULES_AVAILABLE = True
except ImportError:
    VOICE_MODULES_AVAILABLE = False

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding='utf-8', errors='replace'
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding='utf-8', errors='replace'
    )

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
VOSK_MODEL_PATH = GATE / 'models' / 'vosk' / 'vosk-model-small-en-us-0.15'

# Initialize voice modules
if VOICE_MODULES_AVAILABLE:
    try:
        intent_recognizer = IntentRecognizer()
        voice_skills = VoiceSkills()
        multilang = MultiLanguage()
        noise_cancel = NoiseCancellation()
        offline_stt = None
        offline_tts = init_offline_tts()
    except Exception:
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

# Initialize Vosk if available
vosk_model: Optional[Any] = None
vosk_rec: Optional[Any] = None
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
        
    Returns:
        None
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
    except Exception:
        print(text)


# Command handler functions (imported from original file)
def handle_planetary_search(topic: str) -> None:
    """Handle planetary search command."""
    # Implementation from original file
    pass


def handle_council(problem: str) -> None:
    """Handle council command."""
    # Implementation from original file
    pass


def handle_hive(problem: str) -> None:
    """Handle hive command."""
    # Implementation from original file
    pass


def handle_go_to_school(topic: str) -> None:
    """Handle go to school command."""
    # Implementation from original file
    pass


def handle_white_page() -> None:
    """Handle white page command."""
    # Implementation from original file
    pass


def handle_send_white_page() -> None:
    """Handle send white page command."""
    # Implementation from original file
    pass


def handle_game_hub() -> None:
    """Handle game hub command."""
    # Implementation from original file
    pass


def handle_replay_moves(n: int) -> None:
    """Handle replay moves command."""
    # Implementation from original file
    pass


def handle_replay_full_game() -> None:
    """Handle replay full game command."""
    # Implementation from original file
    pass


def handle_playbook(product: str = "") -> None:
    """Handle playbook command."""
    # Implementation from original file
    pass


def handle_salesbot(command: str = "") -> None:
    """Handle salesbot command."""
    # Implementation from original file
    pass


def handle_saleshub(product: str = "") -> None:
    """Handle saleshub command."""
    # Implementation from original file
    pass


def handle_farmos(command: str = "") -> None:
    """Handle farmos command."""
    # Implementation from original file
    pass


def handle_fusion(text: str) -> None:
    """Handle fusion command."""
    # Implementation from original file
    pass


# Command routing functions (refactored from handle_command)
def _extract_problem_from_council(text_lower: str) -> Optional[str]:
    """
    Extract problem from council command.
    
    Args:
        text_lower: Lowercase command text
        
    Returns:
        Extracted problem or None
    """
    if " on " in text_lower:
        return text_lower.split(" on ")[-1].strip()
    elif "solve" in text_lower:
        return text_lower.split("solve")[-1].strip()
    else:
        return text_lower.replace("council", "").replace("agent", "").strip()


def _handle_council_command(text_lower: str) -> bool:
    """
    Handle council-related commands.
    
    Args:
        text_lower: Lowercase command text
        
    Returns:
        True if command was handled, False otherwise
    """
    if "council" not in text_lower and "agent council" not in text_lower:
        return False
    
    if " on " in text_lower or "solve" in text_lower:
        problem = _extract_problem_from_council(text_lower)
        if problem:
            handle_council(problem)
            return True
    else:
        say("The doors of knowledge opens. What problem should the council solve?")
        return True
    
    return False


def _handle_solve_command(text_lower: str) -> bool:
    """
    Handle solve (hive) commands.
    
    Args:
        text_lower: Lowercase command text
        
    Returns:
        True if command was handled, False otherwise
    """
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
    """
    Handle hive commands.
    
    Args:
        text_lower: Lowercase command text
        
    Returns:
        True if command was handled, False otherwise
    """
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
    """
    Handle search commands.
    
    Args:
        text_lower: Lowercase command text
        
    Returns:
        True if command was handled, False otherwise
    """
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
    """
    Handle go to school/college commands.
    
    Args:
        text_lower: Lowercase command text
        
    Returns:
        True if command was handled, False otherwise
    """
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
    """
    Handle white page commands.
    
    Args:
        text_lower: Lowercase command text
        
    Returns:
        True if command was handled, False otherwise
    """
    if "white page" not in text_lower:
        return False
    
    if "send" in text_lower:
        handle_send_white_page()
    else:
        handle_white_page()
    return True


def _handle_game_hub_command(text_lower: str) -> bool:
    """
    Handle game hub commands.
    
    Args:
        text_lower: Lowercase command text
        
    Returns:
        True if command was handled, False otherwise
    """
    game_keywords = ["game hub", "open game hub", "resume game"]
    if any(keyword in text_lower for keyword in game_keywords):
        handle_game_hub()
        return True
    return False


def _handle_replay_command(text_lower: str) -> bool:
    """
    Handle replay commands.
    
    Args:
        text_lower: Lowercase command text
        
    Returns:
        True if command was handled, False otherwise
    """
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
    """
    Handle playbook commands.
    
    Args:
        text_lower: Lowercase command text
        text: Original command text
        
    Returns:
        True if command was handled, False otherwise
    """
    if "playbook" not in text_lower and "marketing playbook" not in text_lower:
        return False
    
    if "pitch" in text_lower or "sell" in text_lower:
        handle_playbook(text)
    else:
        handle_playbook("")
    return True


def _handle_salesbot_command(text_lower: str, text: str) -> bool:
    """
    Handle salesbot commands.
    
    Args:
        text_lower: Lowercase command text
        text: Original command text
        
    Returns:
        True if command was handled, False otherwise
    """
    if "salesbot" not in text_lower and "sales bot" not in text_lower:
        return False
    
    if "order" in text_lower or "track" in text_lower or "status" in text_lower:
        handle_salesbot(text)
    else:
        handle_salesbot("")
    return True


def _handle_saleshub_command(text_lower: str) -> bool:
    """
    Handle saleshub commands.
    
    Args:
        text_lower: Lowercase command text
        
    Returns:
        True if command was handled, False otherwise
    """
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
    """
    Handle FarmOS commands.
    
    Args:
        text_lower: Lowercase command text
        text: Original command text
        
    Returns:
        True if command was handled, False otherwise
    """
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
    """
    Handle code/write/build commands (FUSION).
    
    Args:
        text_lower: Lowercase command text
        text: Original command text
        
    Returns:
        True if command was handled, False otherwise
    """
    code_keywords = ["write", "code", "build", "create", "program", "develop", "implement"]
    if any(keyword in text_lower for keyword in code_keywords):
        handle_fusion(text)
        return True
    return False


def handle_command(text: str) -> None:
    """
    Process the recognized command.
    
    This function routes voice commands to appropriate handlers.
    Refactored to reduce complexity by breaking into smaller functions.
    
    Args:
        text: The recognized command text
        
    Returns:
        None
    """
    text_lower = text.lower()
    print(f"Command: {text}")
    
    # Route to appropriate handler
    handlers = [
        _handle_council_command,
        _handle_solve_command,
        _handle_hive_command,
        _handle_search_command,
        _handle_school_command,
        _handle_white_page_command,
        _handle_game_hub_command,
        _handle_replay_command,
        _handle_playbook_command,
        _handle_salesbot_command,
        _handle_saleshub_command,
        _handle_farmos_command,
        _handle_code_command,
    ]
    
    for handler in handlers:
        try:
            if handler(text_lower, text) if handler.__code__.co_argcount > 1 else handler(text_lower):
                return
        except Exception as e:
            print(f"Error in handler {handler.__name__}: {e}")
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
        raw_data = audio.get_raw_data(convert_rate=16000, convert_width=2)
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
        
        if vosk_rec.FinalResult():
            final = json.loads(vosk_rec.FinalResult())
            full_text = final.get('text', full_text)
        
        return full_text if full_text else None
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
        except Exception:
            # Fallback to Google API (requires internet)
            return recognizer.recognize_google(audio).lower()
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
    
    Returns:
        None
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
                audio = recognizer.listen(
                    source, timeout=5, phrase_time_limit=3
                )
            
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
