#!/usr/bin/env python3
# Voice Security System - Voice authentication and communication lock-on
import json
import hashlib
import numpy as np
import librosa
from pathlib import Path
from datetime import datetime
import pickle
import base64
from functools import lru_cache

SECURITY_DIR = Path('voice_security')
SECURITY_DIR.mkdir(exist_ok=True)

VOICE_SIGNATURE_FILE = SECURITY_DIR / 'authorized_voice_signatures.pkl'
UNAUTHORIZED_LEARNINGS_FILE = SECURITY_DIR / 'unauthorized_patterns.json'
SECURITY_LOG = SECURITY_DIR / 'security_log.json'

class VoiceSecuritySystem:
    def __init__(self):
        self.authorized_voices = self.load_authorized_voices()
        self.unauthorized_patterns = self.load_unauthorized_patterns()
        self.security_log = []
        self.lock_on_threshold = 0.85  # 85% match required for authorization
        self.learning_mode = True  # Learn from all voices initially
        self._signature_cache = {}  # Cache extracted signatures by file path
        
    def load_authorized_voices(self):
        """Load authorized voice signatures."""
        if VOICE_SIGNATURE_FILE.exists():
            try:
                with open(VOICE_SIGNATURE_FILE, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading voice signatures: {e}")
        return {}  # {voice_id: {'features': {...}, 'created': timestamp, 'name': '...'}}
    
    def save_authorized_voices(self):
        """Save authorized voice signatures securely."""
        try:
            with open(VOICE_SIGNATURE_FILE, 'wb') as f:
                pickle.dump(self.authorized_voices, f)
            # Set file permissions (Windows)
            import os
            os.chmod(VOICE_SIGNATURE_FILE, 0o600)  # Read/write for owner only
        except Exception as e:
            print(f"Error saving voice signatures: {e}")
    
    def load_unauthorized_patterns(self):
        """Load patterns learned from unauthorized speakers."""
        if UNAUTHORIZED_LEARNINGS_FILE.exists():
            try:
                with open(UNAUTHORIZED_LEARNINGS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_unauthorized_patterns(self):
        """Save unauthorized speaker patterns."""
        try:
            with open(UNAUTHORIZED_LEARNINGS_FILE, 'w') as f:
                json.dump(self.unauthorized_patterns, f, indent=2)
        except Exception as e:
            print(f"Error saving unauthorized patterns: {e}")
    
    def extract_voice_signature(self, audio_path):
        """Extract optimized voice signature (reduced features for speed)."""
        # Check cache first
        audio_path_str = str(audio_path)
        if audio_path_str in self._signature_cache:
            return self._signature_cache[audio_path_str]
        
        try:
            audio, sr = librosa.load(str(audio_path), sr=16000)
            
            # OPTIMIZED: Only extract essential features
            # 1. Pitch/Fundamental Frequency (wavelength characteristic) - KEEP
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr, threshold=0.1)
            pitch_values = pitches[pitches > 0]
            
            # 2. Spectral Centroid (most important spectral feature) - KEEP
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            
            # 3. MFCCs (voice timbre fingerprint) - REDUCED from 13 to 8 coefficients
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=8)  # OPTIMIZED: 8 instead of 13
            
            # OPTIMIZED: Skip chroma (15% weight, slower to compute)
            # OPTIMIZED: Skip harmonic separation (expensive)
            # OPTIMIZED: Skip tempo/beat tracking (expensive)
            # OPTIMIZED: Skip spectral envelope (redundant with centroid)
            
            # Create optimized signature (reduced feature set)
            signature = {
                'pitch': {
                    'mean': float(np.mean(pitch_values)) if len(pitch_values) > 0 else 0,
                    'std': float(np.std(pitch_values)) if len(pitch_values) > 0 else 0,
                },
                'spectral': {
                    'centroid_mean': float(np.mean(spectral_centroids)),
                },
                'mfccs_mean': [float(x) for x in np.mean(mfccs, axis=1)],  # Only 8 coefficients
            }
            
            # Cache the signature
            self._signature_cache[audio_path_str] = signature
            return signature
        except Exception as e:
            print(f"Error extracting voice signature: {e}")
            return None
    
    def compare_voice_signatures(self, sig1, sig2):
        """Compare two voice signatures (optimized - fewer features)."""
        if not sig1 or not sig2:
            return 0.0
        
        similarities = []
        
        # 1. Pitch comparison (40% weight - increased since we removed chroma)
        if 'pitch' in sig1 and 'pitch' in sig2:
            pitch1 = sig1['pitch']
            pitch2 = sig2['pitch']
            pitch_sim = 1.0 - min(abs(pitch1['mean'] - pitch2['mean']) / 200.0, 1.0)
            similarities.append(pitch_sim * 0.4)  # Increased from 30% to 40%
        
        # 2. MFCC comparison (50% weight - most important, now primary)
        if 'mfccs_mean' in sig1 and 'mfccs_mean' in sig2:
            mfcc1 = np.array(sig1['mfccs_mean'])
            mfcc2 = np.array(sig2['mfccs_mean'])
            mfcc_diff = np.linalg.norm(mfcc1 - mfcc2)
            mfcc_sim = 1.0 / (1.0 + mfcc_diff / 10.0)
            similarities.append(mfcc_sim * 0.5)  # Increased from 40% to 50%
        
        # 3. Spectral centroid (10% weight - reduced)
        if 'spectral' in sig1 and 'spectral' in sig2:
            spec1 = sig1['spectral']
            spec2 = sig2['spectral']
            centroid_sim = 1.0 - min(abs(spec1['centroid_mean'] - spec2['centroid_mean']) / 2000.0, 1.0)
            similarities.append(centroid_sim * 0.1)  # Reduced from 15% to 10%
        
        # OPTIMIZED: Removed chroma comparison (was 15% weight, slower to compute)
        
        # Overall similarity (weighted average)
        overall_sim = sum(similarities) if similarities else 0.0
        return min(max(overall_sim, 0.0), 1.0)
    
    def verify_voice(self, audio_path):
        """Verify if voice matches authorized signatures."""
        if not self.authorized_voices:
            # No authorized voices yet - learning mode
            return {'authorized': True, 'confidence': 1.0, 'voice_id': None, 'learning_mode': True}
        
        # Extract signature from audio
        signature = self.extract_voice_signature(audio_path)
        if not signature:
            return {'authorized': False, 'confidence': 0.0, 'voice_id': None, 'error': 'Could not extract signature'}
        
        # Compare with all authorized voices
        best_match = None
        best_score = 0.0
        
        for voice_id, voice_data in self.authorized_voices.items():
            score = self.compare_voice_signatures(signature, voice_data['features'])
            if score > best_score:
                best_score = score
                best_match = voice_id
        
        # Check if match is above threshold
        authorized = best_score >= self.lock_on_threshold
        voice_id = best_match if authorized else None
        
        # Log security event
        self.log_security_event('voice_verification', {
            'authorized': authorized,
            'confidence': best_score,
            'voice_id': voice_id,
            'timestamp': datetime.now().isoformat(),
            'audio_file': str(audio_path)
        })
        
        return {
            'authorized': authorized,
            'confidence': best_score,
            'voice_id': voice_id,
            'threshold': self.lock_on_threshold,
            'learning_mode': False
        }
    
    def register_authorized_voice(self, audio_path, name="Primary User"):
        """Register a new authorized voice."""
        signature = self.extract_voice_signature(audio_path)
        if not signature:
            return False
        
        # Create voice ID from hash of signature
        sig_str = json.dumps(signature, sort_keys=True)
        voice_id = hashlib.sha256(sig_str.encode()).hexdigest()[:16]
        
        self.authorized_voices[voice_id] = {
            'features': signature,
            'created': datetime.now().isoformat(),
            'name': name,
            'source_audio': str(audio_path)
        }
        
        self.save_authorized_voices()
        
        self.log_security_event('voice_registered', {
            'voice_id': voice_id,
            'name': name,
            'timestamp': datetime.now().isoformat()
        })
        
        # Silent registration - no print statement
        return True
    
    def learn_from_unauthorized_speaker(self, audio_path, detected_features=None):
        """Learn patterns from unauthorized speaker but don't respond."""
        signature = detected_features or self.extract_voice_signature(audio_path)
        if not signature:
            return
        
        # Store pattern (without identifying info)
        pattern = {
            'timestamp': datetime.now().isoformat(),
            'features': {
                'pitch_mean': signature.get('pitch', {}).get('mean', 0),
                'spectral_centroid': signature.get('spectral', {}).get('centroid_mean', 0),
                'mfccs_sample': signature.get('mfccs_mean', [])[:5],  # Sample only
            },
            'source': 'unauthorized_detection'
        }
        
        self.unauthorized_patterns.append(pattern)
        
        # Keep only last 100 patterns
        if len(self.unauthorized_patterns) > 100:
            self.unauthorized_patterns = self.unauthorized_patterns[-100:]
        
        self.save_unauthorized_patterns()
        
        self.log_security_event('unauthorized_speaker_detected', {
            'timestamp': datetime.now().isoformat(),
            'action': 'learned_pattern_no_response'
        })
        
        # Silent detection - no print statement
    
    def log_security_event(self, event_type, data):
        """Log security events."""
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.security_log.append(event)
        
        # Keep last 1000 events
        if len(self.security_log) > 1000:
            self.security_log = self.security_log[-1000:]
        
        # Save log
        try:
            with open(SECURITY_LOG, 'w') as f:
                json.dump(self.security_log, f, indent=2)
        except:
            pass
    
    def get_security_status(self):
        """Get current security status."""
        return {
            'authorized_voices_count': len(self.authorized_voices),
            'lock_on_threshold': self.lock_on_threshold,
            'learning_mode': self.learning_mode and len(self.authorized_voices) == 0,
            'unauthorized_patterns_learned': len(self.unauthorized_patterns),
            'security_events_logged': len(self.security_log)
        }

# Global instance
voice_security = VoiceSecuritySystem()

if __name__ == "__main__":
    print("=" * 70)
    print("  VOICE SECURITY SYSTEM")
    print("=" * 70)
    
    status = voice_security.get_security_status()
    print(f"\nSecurity Status:")
    print(f"  Authorized voices: {status['authorized_voices_count']}")
    print(f"  Lock-on threshold: {status['lock_on_threshold']*100:.0f}%")
    print(f"  Learning mode: {status['learning_mode']}")
    print(f"  Unauthorized patterns learned: {status['unauthorized_patterns_learned']}")
    print()
