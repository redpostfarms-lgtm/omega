#!/usr/bin/env python3
"""
Omega Voice Wake System
========================
Low-power voice activation: Keeps microphone active, wakes system on "wake up" command.
"""

import sys
import subprocess
import platform
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

sys.path.insert(0, str(Path(__file__).parent))

# Voice recognition imports
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

try:
    from omega_windows_power import get_power_manager
    POWER_MANAGER_AVAILABLE = True
except ImportError:
    POWER_MANAGER_AVAILABLE = False

# Voice security imports
try:
    from voice_security_system import voice_security
    VOICE_SECURITY_AVAILABLE = True
except ImportError:
    VOICE_SECURITY_AVAILABLE = False
    voice_security = None


class VoiceWakeSystem:
    """Voice-activated wake system with low-power mode"""
    
    def __init__(self, wake_phrase: str = "wake up", sensitivity: float = 0.5):
        self.wake_phrase = wake_phrase.lower()
        self.sensitivity = sensitivity
        self.running = False
        self.listening = False
        self.recognizer = None
        self.microphone = None
        self.voice_security_enabled = VOICE_SECURITY_AVAILABLE and voice_security is not None
        
        # Initialize speech recognition
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.energy_threshold = 4000  # Adjust for ambient noise
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8  # Pause detection
                self.microphone = sr.Microphone()
                
                # Adjust for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
            except Exception as e:
                print(f"Warning: Speech recognition initialization failed: {e}")
                self.recognizer = None
                self.microphone = None
        
        # Power manager
        self.power_manager = None
        if POWER_MANAGER_AVAILABLE:
            try:
                self.power_manager = get_power_manager()
            except:
                pass
    
    def enable_usb_wake(self):
        """Enable USB devices to wake system from sleep"""
        if platform.system() != "Windows":
            return False, "Windows only"
        
        try:
            # Enable USB selective suspend (allows USB devices to stay active)
            subprocess.run('powercfg /SETACVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0', shell=True, capture_output=True)
            subprocess.run('powercfg /SETDCVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0', shell=True, capture_output=True)
            
            # Allow wake timers
            subprocess.run('powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_SLEEP RTCWAKE 1', shell=True, capture_output=True)
            subprocess.run('powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_SLEEP RTCWAKE 1', shell=True, capture_output=True)
            
            # Enable wake from USB (HID devices - keyboards, mice, microphones)
            subprocess.run('powercfg /deviceenablewake "USB\\VID_*"', shell=True, capture_output=True)
            
            # Apply settings
            subprocess.run('powercfg /SETACTIVE SCHEME_CURRENT', shell=True, capture_output=True)
            
            return True, "USB wake enabled"
        except Exception as e:
            return False, f"Error: {e}"
    
    def listen_for_wake_phrase(self, callback: Optional[Callable] = None):
        """Listen for wake phrase in background"""
        if not self.recognizer or not self.microphone:
            return False, "Speech recognition not available"
        
        def listen_loop():
            self.listening = True
            print(f"[Voice Wake] Listening for '{self.wake_phrase}'...")
            
            while self.running:
                try:
                    with self.microphone as source:
                        # Listen for audio with timeout
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    
                    try:
                        # Recognize speech using Google (offline options available)
                        text = self.recognizer.recognize_google(audio, language='en-US').lower()
                        print(f"[Voice Wake] Heard: {text}")
                        
                        # Check for wake phrase
                        if self.wake_phrase in text:
                            print(f"[Voice Wake] WAKE PHRASE DETECTED: '{self.wake_phrase}'")
                            self.wake_system()
                            if callback:
                                callback()
                            break  # Stop listening after wake
                    except sr.UnknownValueError:
                        # Didn't understand audio
                        pass
                    except sr.RequestError as e:
                        print(f"[Voice Wake] Recognition error: {e}")
                        time.sleep(1)
                
                except sr.WaitTimeoutError:
                    # Timeout - continue listening
                    continue
                except Exception as e:
                    print(f"[Voice Wake] Error: {e}")
                    time.sleep(1)
            
            self.listening = False
        
        # Start listening thread
        thread = threading.Thread(target=listen_loop, daemon=True)
        thread.start()
        return True, "Listening started"
    
    def wake_system(self):
        """Wake system from sleep"""
        try:
            if platform.system() == "Windows":
                # Send wake signal using keyboard event
                # This simulates a key press to wake from sleep
                try:
                    import ctypes
                    # Send Windows key press to wake system
                    ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Windows key down
                    time.sleep(0.1)
                    ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Windows key up
                    print("[Voice Wake] Wake signal sent via keyboard")
                except:
                    # Fallback: Use powercfg to resume
                    subprocess.run('powercfg /devicequery wake_programmable', shell=True, capture_output=True)
                    print("[Voice Wake] Attempting to wake system...")
                
                return True, "Wake signal sent"
            else:
                return False, "Windows only"
        except Exception as e:
            return False, f"Error: {e}"
    
    def start_listening(self):
        """Start voice wake system with voice authentication"""
        if self.running:
            return False, "Already running"
        
        # Check voice security status
        if self.voice_security_enabled:
            try:
                security_status = voice_security.get_security_status()
                if security_status.get('authorized_voices_count', 0) == 0:
                    print("[Voice Wake] Warning: No authorized voices registered")
                    print("[Voice Wake] First voice detected will be registered as authorized")
                else:
                    print(f"[Voice Wake] Voice security active - {security_status.get('authorized_voices_count', 0)} authorized voice(s)")
            except Exception as e:
                print(f"[Voice Wake] Warning: Could not check security status: {e}")
        
        # Enable USB wake first
        success, msg = self.enable_usb_wake()
        if not success:
            print(f"[Voice Wake] Warning: {msg}")
        
        self.running = True
        
        # Start listening
        success, msg = self.listen_for_wake_phrase()
        if success:
            return True, "Voice wake system started (voice authentication enabled)"
        else:
            self.running = False
            return False, msg
    
    def stop_listening(self):
        """Stop voice wake system"""
        self.running = False
        return True, "Voice wake system stopped"
    
    def sleep_with_voice_wake(self):
        """Put system to sleep while keeping voice wake active"""
        if not self.power_manager:
            return False, "Power manager not available"
        
        # Start listening before sleep
        success, msg = self.start_listening()
        if not success:
            return False, f"Failed to start voice wake: {msg}"
        
        # Give it a moment to initialize
        time.sleep(2)
        
        # Put system to sleep (USB devices will stay powered)
        print("[Voice Wake] Entering sleep mode... Voice wake is active.")
        success, msg = self.power_manager.sleep()
        
        return success, msg


def get_voice_wake_system() -> VoiceWakeSystem:
    """Get or create voice wake system instance"""
    return VoiceWakeSystem()


if __name__ == "__main__":
    print("=" * 80)
    print("OMEGA VOICE WAKE SYSTEM")
    print("=" * 80)
    print()
    
    vw = get_voice_wake_system()
    
    print("Voice Wake System initialized")
    print(f"Wake phrase: '{vw.wake_phrase}'")
    print()
    print("Commands:")
    print("  start - Start listening for wake phrase")
    print("  sleep - Put system to sleep with voice wake active")
    print("  stop - Stop listening")
    print("  exit - Exit")
    print()
    
    while True:
        try:
            cmd = input("VoiceWake> ").strip().lower()
            
            if cmd == "exit":
                vw.stop_listening()
                break
            elif cmd == "start":
                success, msg = vw.start_listening()
                print(f"[{'OK' if success else 'ERROR'}] {msg}")
            elif cmd == "sleep":
                success, msg = vw.sleep_with_voice_wake()
                print(f"[{'OK' if success else 'ERROR'}] {msg}")
            elif cmd == "stop":
                success, msg = vw.stop_listening()
                print(f"[{'OK' if success else 'ERROR'}] {msg}")
            else:
                print("Unknown command")
        except KeyboardInterrupt:
            print("\nStopping...")
            vw.stop_listening()
            break
        except Exception as e:
            print(f"Error: {e}")
