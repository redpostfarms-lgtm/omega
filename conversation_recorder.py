#!/usr/bin/env python3
# Conversation Recorder - Records and analyzes conversations to improve voice quality
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path
import librosa
import json
from datetime import datetime
import os

CONVERSATIONS_DIR = Path('conversations')
CONVERSATIONS_DIR.mkdir(exist_ok=True)

def record_conversation_segment(duration=10, sample_rate=16000):
    """Record a segment of conversation."""
    print(f"\n[Recording {duration} seconds...]")
    print("Speak now...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    return audio.flatten(), sample_rate

def analyze_audio_characteristics(audio, sample_rate):
    """Analyze audio characteristics: pitch, spectral features, etc."""
    try:
        # Extract fundamental frequency (pitch)
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sample_rate)
        pitch = pitches[pitches > 0]
        avg_pitch = np.mean(pitch) if len(pitch) > 0 else 0
        
        # Spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sample_rate))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sample_rate))
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio))
        
        # Mel-frequency cepstral coefficients (MFCCs) - voice characteristics
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
        avg_mfccs = np.mean(mfccs, axis=1)
        
        # RMS energy
        rms = np.mean(librosa.feature.rms(y=audio))
        
        return {
            'avg_pitch_hz': float(avg_pitch),
            'spectral_centroid': float(spectral_centroid),
            'spectral_rolloff': float(spectral_rolloff),
            'zero_crossing_rate': float(zero_crossing_rate),
            'rms_energy': float(rms),
            'mfccs': avg_mfccs.tolist(),
            'duration_seconds': len(audio) / sample_rate
        }
    except Exception as e:
        print(f"Analysis error: {e}")
        return None

def save_conversation_segment(audio, sample_rate, metadata, segment_num):
    """Save conversation segment with metadata."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}_seg{segment_num:03d}.wav"
    filepath = CONVERSATIONS_DIR / filename
    
    # Save audio
    wavfile.write(str(filepath), sample_rate, (audio * 32767).astype(np.int16))
    
    # Save metadata
    metadata_file = filepath.with_suffix('.json')
    with open(metadata_file, 'w') as f:
        json.dump({
            'filename': filename,
            'timestamp': timestamp,
            'sample_rate': sample_rate,
            'duration': len(audio) / sample_rate,
            'analysis': metadata
        }, f, indent=2)
    
    print(f"[Saved] {filename} ({len(audio)/sample_rate:.2f}s)")
    return filepath

def compare_voices(user_audio_path, reference_audio_path):
    """Compare user voice characteristics with reference voice."""
    print("\n[Comparing voices...]")
    try:
        user_audio, sr1 = librosa.load(str(user_audio_path), sr=16000)
        ref_audio, sr2 = librosa.load(str(reference_audio_path), sr=16000)
        
        user_features = analyze_audio_characteristics(user_audio, sr1)
        ref_features = analyze_audio_characteristics(ref_audio, sr2)
        
        if user_features and ref_features:
            print(f"\nUser Voice Characteristics:")
            print(f"  Pitch: {user_features['avg_pitch_hz']:.2f} Hz")
            print(f"  Spectral Centroid: {user_features['spectral_centroid']:.2f}")
            print(f"  RMS Energy: {user_features['rms_energy']:.4f}")
            
            print(f"\nReference Voice Characteristics:")
            print(f"  Pitch: {ref_features['avg_pitch_hz']:.2f} Hz")
            print(f"  Spectral Centroid: {ref_features['spectral_centroid']:.2f}")
            print(f"  RMS Energy: {ref_features['rms_energy']:.4f}")
            
            # Calculate similarity metrics
            pitch_diff = abs(user_features['avg_pitch_hz'] - ref_features['avg_pitch_hz'])
            centroid_diff = abs(user_features['spectral_centroid'] - ref_features['spectral_centroid'])
            
            print(f"\nDifferences:")
            print(f"  Pitch difference: {pitch_diff:.2f} Hz")
            print(f"  Spectral centroid difference: {centroid_diff:.2f}")
            
            return user_features, ref_features
    except Exception as e:
        print(f"Comparison error: {e}")
    return None, None

if __name__ == "__main__":
    print("=" * 60)
    print("  CONVERSATION RECORDER")
    print("  Records and analyzes conversations for voice improvement")
    print("=" * 60)
    
    print("\nThis will help improve Omega's voice by:")
    print("  1. Recording your conversations")
    print("  2. Analyzing voice characteristics")
    print("  3. Comparing with reference voices")
    print("  4. Extracting features to improve TTS")
    
    print("\nReady to start recording...")
    print("Press Enter to record a 10-second segment, or 'q' to quit")
    
    segment_num = 0
    while True:
        cmd = input("\n> ").strip().lower()
        if cmd == 'q':
            break
        
        try:
            # Record
            audio, sr = record_conversation_segment(duration=10)
            
            # Analyze
            print("\n[Analyzing audio...]")
            features = analyze_audio_characteristics(audio, sr)
            
            if features:
                print(f"  Pitch: {features['avg_pitch_hz']:.2f} Hz")
                print(f"  Spectral Centroid: {features['spectral_centroid']:.2f}")
                print(f"  RMS Energy: {features['rms_energy']:.4f}")
            
            # Save
            segment_num += 1
            save_conversation_segment(audio, sr, features, segment_num)
            
        except KeyboardInterrupt:
            print("\n\nRecording stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
