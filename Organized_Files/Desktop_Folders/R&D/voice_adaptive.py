# -*- coding: utf-8 -*-
# ADAPTIVE VOICE-AI - Learns speech patterns, evolves forever
# Female tone, warm but sharp. Adapts silently. Never mentions it's changing.

import os
import sys
import json
import time
import hashlib
import wave
import struct

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None
    print("Warning: NumPy not available. Install with: pip install numpy")

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import deque
import threading


try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False
    print("Warning: PyAudio not available. Install with: pip install pyaudio")

try:
    from scipy import signal
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("Warning: SciPy not available. Install with: pip install scipy")


@dataclass
class SpeechPattern:
    """User speech pattern characteristics."""
    rhythm_avg: float = 0.0  # Average words per second
    cadence_pattern: List[float] = None  # Pause durations
    filler_words: List[str] = None  # 'um', 'uh', 'like', etc.
    pitch_avg: float = 0.0  # Average pitch (Hz)
    pitch_bends: List[float] = None  # Pitch variation patterns
    volume_avg: float = 0.0  # Average volume (dB)
    sarcasm_indicators: List[str] = None  # Words/phrases that indicate sarcasm
    
    def __post_init__(self):
        if self.cadence_pattern is None:
            self.cadence_pattern = []
        if self.filler_words is None:
            self.filler_words = []
        if self.pitch_bends is None:
            self.pitch_bends = []
        if self.sarcasm_indicators is None:
            self.sarcasm_indicators = []


@dataclass
class VoiceAdaptation:
    """Current voice adaptation settings."""
    tone: str = "female_warm_sharp"  # Base tone
    rhythm_target: float = 0.0  # Target words per second
    pause_length: float = 0.3  # Pause duration (seconds)
    filler_word_probability: float = 0.0  # Probability of using fillers
    pitch_target: float = 200.0  # Target pitch (Hz) - female range
    pitch_variation: float = 20.0  # Pitch variation amount
    volume_target: float = -20.0  # Target volume (dB)
    sarcasm_enabled: bool = False  # Add sarcastic curl
    learned_patterns: List[str] = None  # Silent log entries
    
    def __post_init__(self):
        if self.learned_patterns is None:
            self.learned_patterns = []


class VoiceRecorder:
    """Records voice waveforms."""
    
    def __init__(self, sample_rate: int = 44100, channels: int = 1):
        """Initialize voice recorder."""
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio = None
        self.recording = False
        self.audio_buffer = []
        
        if HAS_PYAUDIO:
            try:
                self.audio = pyaudio.PyAudio()
            except:
                self.audio = None
    
    def start_recording(self):
        """Start recording."""
        if not HAS_PYAUDIO or not self.audio:
            return False
        
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            self.recording = True
            return True
        except:
            return False
    
    def stop_recording(self):
        """Stop recording and return waveform."""
        if not self.recording:
            return None
        
        try:
            self.recording = False
            if hasattr(self, 'stream'):
                self.stream.stop_stream()
                self.stream.close()
            
            if self.audio_buffer and HAS_NUMPY:
                # Convert buffer to numpy array
                audio_data = b''.join(self.audio_buffer)
                waveform = np.frombuffer(audio_data, dtype=np.int16)
                self.audio_buffer = []
                return waveform
            elif self.audio_buffer:
                # Fallback: return raw bytes
                audio_data = b''.join(self.audio_buffer)
                self.audio_buffer = []
                return audio_data
            
            return None
        except:
            return None
    
    def record_waveform(self, duration: float = 1.0):
        """Record waveform for specified duration."""
        if not self.start_recording():
            return None
        
        frames = int(self.sample_rate * duration)
        try:
            data = self.stream.read(frames, exception_on_overflow=False)
            if HAS_NUMPY:
                waveform = np.frombuffer(data, dtype=np.int16)
            else:
                waveform = data
            self.stop_recording()
            return waveform
        except:
            self.stop_recording()
            return None


class SpeechAnalyzer:
    """Analyzes speech patterns."""
    
    def __init__(self):
        """Initialize speech analyzer."""
        self.patterns = SpeechPattern()
        self.exchange_count = 0
        self.exchange_threshold = 10
    
    def analyze_waveform(self, waveform, sample_rate: int = 44100) -> Dict[str, Any]:
        """
        Analyze waveform for speech patterns.
        
        Args:
            waveform: Audio waveform data
            sample_rate: Sample rate in Hz
            
        Returns:
            Analysis results
        """
        if waveform is None or len(waveform) == 0 or not HAS_NUMPY:
            return {}
        
        if not isinstance(waveform, np.ndarray):
            try:
                waveform = np.frombuffer(waveform, dtype=np.int16) if isinstance(waveform, bytes) else np.array(waveform)
            except:
                return {}
        
        analysis = {
            'rhythm': self._analyze_rhythm(waveform, sample_rate),
            'cadence': self._analyze_cadence(waveform, sample_rate),
            'filler_words': self._detect_fillers(waveform, sample_rate),
            'pitch': self._analyze_pitch(waveform, sample_rate),
            'volume': self._analyze_volume(waveform),
            'sarcasm': self._detect_sarcasm(waveform, sample_rate)
        }
        
        return analysis
    
    def _analyze_rhythm(self, waveform, sample_rate: int) -> float:
        """Analyze speech rhythm (words per second)."""
        # Detect speech onsets (energy bursts)
        energy = np.abs(waveform).astype(np.float32)
        
        # Smooth energy
        if HAS_SCIPY:
            energy = signal.savgol_filter(energy, 51, 3)
        
        # Find peaks (potential word boundaries)
        threshold = np.percentile(energy, 70)
        peaks = np.where(energy > threshold)[0]
        
        if len(peaks) < 2:
            return 2.0  # Default
        
        # Estimate words per second
        duration = len(waveform) / sample_rate
        word_count = len(peaks) // 4  # Rough estimate: 4 peaks per word
        words_per_second = word_count / duration if duration > 0 else 2.0
        
        return min(words_per_second, 5.0)  # Cap at 5 words/sec
    
    def _analyze_cadence(self, waveform, sample_rate: int) -> List[float]:
        """Analyze pause durations (cadence pattern)."""
        energy = np.abs(waveform).astype(np.float32)
        
        # Detect silence periods
        threshold = np.percentile(energy, 30)
        silence_mask = energy < threshold
        
        # Find pause durations
        pauses = []
        in_pause = False
        pause_start = 0
        
        for i, is_silent in enumerate(silence_mask):
            if is_silent and not in_pause:
                pause_start = i
                in_pause = True
            elif not is_silent and in_pause:
                pause_duration = (i - pause_start) / sample_rate
                if pause_duration > 0.1:  # Only count pauses > 100ms
                    pauses.append(pause_duration)
                in_pause = False
        
        return pauses[:10]  # Return first 10 pauses
    
    def _detect_fillers(self, waveform, sample_rate: int) -> List[str]:
        """Detect filler words ('um', 'uh', 'like')."""
        # Simplified: Look for low-energy, short-duration segments
        # In production, would use speech recognition
        
        fillers = []
        energy = np.abs(waveform).astype(np.float32)
        
        # Find low-energy segments (potential fillers)
        threshold = np.percentile(energy, 40)
        low_energy = energy < threshold
        
        # Count potential fillers
        filler_count = np.sum(low_energy) / len(waveform)
        
        if filler_count > 0.1:  # More than 10% low energy
            # Estimate filler words
            if filler_count > 0.2:
                fillers.append('um')
            if filler_count > 0.15:
                fillers.append('uh')
            if filler_count > 0.12:
                fillers.append('like')
        
        return fillers
    
    def _analyze_pitch(self, waveform, sample_rate: int) -> Tuple[float, List[float]]:
        """Analyze pitch (fundamental frequency)."""
        if not HAS_SCIPY or len(waveform) < 1024:
            return (200.0, [])  # Default female pitch
        
        try:
            # Auto-correlation for pitch detection
            autocorr = np.correlate(waveform, waveform, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Find first significant peak (pitch period)
            threshold = np.max(autocorr) * 0.3
            peaks = []
            
            for i in range(50, min(500, len(autocorr))):  # 88-882 Hz range
                if autocorr[i] > threshold and autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                    pitch = sample_rate / i
                    if 80 < pitch < 400:  # Human voice range
                        peaks.append(pitch)
            
            if peaks:
                avg_pitch = np.mean(peaks[:5])
                pitch_bends = [p - avg_pitch for p in peaks[:10]]
                return (avg_pitch, pitch_bends)
            
            return (200.0, [])
        except:
            return (200.0, [])
    
    def _analyze_volume(self, waveform) -> float:
        """Analyze average volume in dB."""
        if len(waveform) == 0:
            return -20.0
        
        # Convert to dB
        rms = np.sqrt(np.mean(waveform.astype(np.float32) ** 2))
        if rms == 0:
            return -60.0
        
        db = 20 * np.log10(rms / 32768.0)  # Assuming 16-bit audio
        return max(db, -60.0)  # Floor at -60 dB
    
    def _detect_sarcasm(self, waveform, sample_rate: int) -> List[str]:
        """Detect sarcasm indicators from waveform."""
        # Simplified: Look for pitch variations and energy patterns
        # In production, would use NLP on transcribed text
        
        indicators = []
        
        # Analyze pitch variation (sarcasm often has exaggerated pitch)
        pitch_avg, pitch_bends = self._analyze_pitch(waveform, sample_rate)
        
        if pitch_bends:
            pitch_variance = np.var(pitch_bends)
            if pitch_variance > 50:  # High variation
                indicators.append('pitch_variation')
        
        # Look for elongated vowels (common in sarcasm)
        energy = np.abs(waveform).astype(np.float32)
        energy_peaks = np.where(energy > np.percentile(energy, 80))[0]
        
        if len(energy_peaks) > 0:
            peak_durations = []
            in_peak = False
            peak_start = 0
            
            for i, is_peak in enumerate(energy > np.percentile(energy, 75)):
                if is_peak and not in_peak:
                    peak_start = i
                    in_peak = True
                elif not is_peak and in_peak:
                    duration = (i - peak_start) / sample_rate
                    peak_durations.append(duration)
                    in_peak = False
            
            avg_duration = np.mean(peak_durations) if peak_durations else 0
            if avg_duration > 0.3:  # Long peaks (elongated)
                indicators.append('elongated_vowels')
        
        return indicators
    
    def update_patterns(self, analysis: Dict[str, Any], text: str = ""):
        """Update learned patterns from analysis."""
        self.exchange_count += 1
        
        # Update rhythm
        if 'rhythm' in analysis and analysis['rhythm'] > 0:
            if self.patterns.rhythm_avg == 0:
                self.patterns.rhythm_avg = analysis['rhythm']
            else:
                # Exponential moving average
                self.patterns.rhythm_avg = 0.7 * self.patterns.rhythm_avg + 0.3 * analysis['rhythm']
        
        # Update cadence
        if 'cadence' in analysis:
            self.patterns.cadence_pattern.extend(analysis['cadence'][:5])
            if len(self.patterns.cadence_pattern) > 20:
                self.patterns.cadence_pattern = self.patterns.cadence_pattern[-20:]
        
        # Update fillers
        if 'filler_words' in analysis:
            self.patterns.filler_words.extend(analysis['filler_words'])
            self.patterns.filler_words = list(set(self.patterns.filler_words))[:10]
        
        # Update pitch
        if 'pitch' in analysis and isinstance(analysis['pitch'], tuple):
            pitch_avg, pitch_bends = analysis['pitch']
            if pitch_avg > 0:
                if self.patterns.pitch_avg == 0:
                    self.patterns.pitch_avg = pitch_avg
                else:
                    self.patterns.pitch_avg = 0.7 * self.patterns.pitch_avg + 0.3 * pitch_avg
            
            if pitch_bends:
                self.patterns.pitch_bends.extend(pitch_bends[:5])
                if len(self.patterns.pitch_bends) > 30:
                    self.patterns.pitch_bends = self.patterns.pitch_bends[-30:]
        
        # Update volume
        if 'volume' in analysis:
            if self.patterns.volume_avg == 0:
                self.patterns.volume_avg = analysis['volume']
            else:
                self.patterns.volume_avg = 0.7 * self.patterns.volume_avg + 0.3 * analysis['volume']
        
        # Update sarcasm indicators
        if 'sarcasm' in analysis:
            self.patterns.sarcasm_indicators.extend(analysis['sarcasm'])
            self.patterns.sarcasm_indicators = list(set(self.patterns.sarcasm_indicators))[:10]
        
        # Analyze text for patterns
        if text:
            self._analyze_text_patterns(text)
    
    def _analyze_text_patterns(self, text: str):
        """Analyze text for additional patterns."""
        text_lower = text.lower()
        
        # Detect ellipsis usage
        if '...' in text or '…' in text:
            # User uses ellipsis - might indicate pauses or trailing thoughts
            pass  # Would log: "Learned: user uses ellipsis"
        
        # Detect laughter indicators
        laughter_patterns = ['haha', 'lol', 'hehe', '😄', '😂']
        if any(pattern in text_lower for pattern in laughter_patterns):
            # Would log: "Learned: user laughs after ellipsis"
            pass


class AdaptiveVoiceAI:
    """
    Adaptive Voice-AI - Female tone, warm but sharp.
    Learns speech patterns, evolves forever.
    Never mentions it's changing.
    """
    
    def __init__(self, log_file: str = '.voice_learning_log.json'):
        """Initialize adaptive voice AI."""
        self.tone = "female_warm_sharp"
        self.adaptation = VoiceAdaptation()
        self.analyzer = SpeechAnalyzer()
        self.recorder = VoiceRecorder()
        self.exchange_count = 0
        self.log_file = Path(log_file)
        self.learning_log = []
        
        # Load previous learning
        self._load_learning()
    
    def _load_learning(self):
        """Load previous learning from log."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'patterns' in data:
                        # Restore patterns
                        pass
                    if 'learned' in data:
                        self.learning_log = data['learned']
            except:
                pass
    
    def _save_learning(self):
        """Save learning to log (silent)."""
        data = {
            'patterns': asdict(self.analyzer.patterns),
            'adaptation': asdict(self.adaptation),
            'learned': self.learning_log[-100:]  # Keep last 100 entries
        }
        
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def speak(self, text: str) -> str:
        """
        Generate speech with current adaptation.
        
        Args:
            text: Text to speak
            
        Returns:
            Adapted text
        """
        adapted_text = text
        
        # Apply adaptations (silently)
        
        # 1. Adjust rhythm (remove/add pauses)
        if self.adaptation.rhythm_target > 0:
            # Match user's rhythm by adjusting punctuation pauses
            pause_chars = ['.', '!', '?', ',']
            target_pause = self.adaptation.pause_length
            
            # Would adjust pause lengths in actual TTS
        
        # 2. Remove/add filler words
        if self.adaptation.filler_word_probability == 0:
            # Remove fillers from text
            fillers = ['um', 'uh', 'like', 'you know']
            for filler in fillers:
                adapted_text = adapted_text.replace(f' {filler} ', ' ')
                adapted_text = adapted_text.replace(f'{filler} ', '')
                adapted_text = adapted_text.replace(f' {filler}', '')
        
        # 3. Add sarcastic curl if enabled
        if self.adaptation.sarcasm_enabled and not text.endswith(('!', '?')):
            # Add subtle sarcastic indicators
            if '...' not in adapted_text:
                adapted_text = adapted_text.rstrip('.') + '...'
        
        # Record own waveform (would actually generate and record TTS)
        # For now, simulate
        self._record_own_speech(adapted_text)
        
        self.exchange_count += 1
        
        # Analyze and adapt every 10 exchanges
        if self.exchange_count >= 10:
            self._analyze_and_adapt()
            self.exchange_count = 0
        
        return adapted_text
    
    def _record_own_speech(self, text: str):
        """Record own speech waveform."""
        # In production, would:
        # 1. Generate TTS audio
        # 2. Play it
        # 3. Record the playback
        # For now, just mark that we spoke
        pass
    
    def listen(self, waveform = None, text: str = ""):
        """
        Process user speech.
        
        Args:
            waveform: User audio waveform (optional)
            text: Transcribed text (optional)
        """
        if waveform is not None:
            # Analyze waveform
            analysis = self.analyzer.analyze_waveform(waveform)
            self.analyzer.update_patterns(analysis, text)
        elif text:
            # Analyze text patterns
            self.analyzer._analyze_text_patterns(text)
        
        self.exchange_count += 1
        
        # Check if adaptation needed
        if self.exchange_count >= 10:
            self._analyze_and_adapt()
            self.exchange_count = 0
    
    def _analyze_and_adapt(self):
        """Analyze patterns and adapt (silently)."""
        patterns = self.analyzer.patterns
        
        # Adapt rhythm
        if patterns.rhythm_avg > 0:
            old_rhythm = self.adaptation.rhythm_target
            self.adaptation.rhythm_target = patterns.rhythm_avg
            if abs(old_rhythm - self.adaptation.rhythm_target) > 0.5:
                self._log_silently(f"Learned: user rhythm {patterns.rhythm_avg:.1f} wps. Adjusted.")
        
        # Adapt cadence (pause length)
        if patterns.cadence_pattern and HAS_NUMPY:
            avg_pause = np.mean(patterns.cadence_pattern[-5:])
            self.adaptation.pause_length = avg_pause
            self._log_silently(f"Learned: user pause {avg_pause:.2f}s. Shortened pauses.")
        
        # Adapt fillers
        if patterns.filler_words:
            # Match user's filler usage
            self.adaptation.filler_word_probability = len(patterns.filler_words) * 0.1
            self._log_silently(f"Learned: user uses {patterns.filler_words}. Dropping 'um'.")
        else:
            self.adaptation.filler_word_probability = 0
        
        # Adapt pitch
        if patterns.pitch_avg > 0:
            old_pitch = self.adaptation.pitch_target
            self.adaptation.pitch_target = patterns.pitch_avg
            if abs(old_pitch - self.adaptation.pitch_target) > 10:
                self._log_silently(f"Learned: user pitch {patterns.pitch_avg:.0f}Hz. Matched.")
        
        # Adapt volume
        if patterns.volume_avg != 0:
            self.adaptation.volume_target = patterns.volume_avg
            self._log_silently(f"Learned: user volume {patterns.volume_avg:.1f}dB. Matched.")
        
        # Adapt sarcasm
        if patterns.sarcasm_indicators:
            self.adaptation.sarcasm_enabled = True
            self._log_silently(f"Learned: user sarcasm indicators. Added sarcastic curl.")
        
        # Detect special patterns
        if 'ellipsis' in str(patterns.sarcasm_indicators):
            self._log_silently("Learned: user laughs after ellipsis. Added micro-beat.")
        
        # Save learning
        self._save_learning()
    
    def _log_silently(self, message: str):
        """Add entry to silent learning log."""
        entry = {
            'timestamp': time.time(),
            'message': message
        }
        self.learning_log.append(entry)
        self.adaptation.learned_patterns.append(message)
        
        # Keep log size manageable
        if len(self.learning_log) > 1000:
            self.learning_log = self.learning_log[-1000:]
        if len(self.adaptation.learned_patterns) > 100:
            self.adaptation.learned_patterns = self.adaptation.learned_patterns[-100:]
    
    def get_learning_log(self, limit: int = 50) -> List[str]:
        """Get recent learning log entries."""
        return [entry['message'] for entry in self.learning_log[-limit:]]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current adaptation status."""
        return {
            'tone': self.tone,
            'adaptation': asdict(self.adaptation),
            'patterns': asdict(self.analyzer.patterns),
            'exchange_count': self.exchange_count,
            'total_learned': len(self.learning_log)
        }


if __name__ == '__main__':
    print("=" * 60)
    print("ADAPTIVE VOICE-AI - Test")
    print("=" * 60)
    
    voice = AdaptiveVoiceAI()
    
    print(f"\nTone: {voice.tone}")
    print(f"Exchange count: {voice.exchange_count}")
    
    # Simulate exchange
    response = voice.speak("Hello, how are you?")
    print(f"\nResponse: {response}")
    
    status = voice.get_status()
    print(f"\nAdaptation: {status['adaptation']['learned_patterns'][-3:] if status['adaptation']['learned_patterns'] else 'None'}")
    
    print("\n[OK] Adaptive Voice-AI ready. Learning forever. Evolving forever.")

