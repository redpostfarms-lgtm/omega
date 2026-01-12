# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# One-time voiceprint capture & live matcher
# Free, local, zero-cloud

import numpy as np
import speech_recognition as sr
from pathlib import Path
import pickle

# Add SpeechBrain support for advanced biometrics
try:
    import torch
    from speechbrain.inference.speaker import EncoderClassifier
    SPEECHBRAIN_AVAILABLE = True
except ImportError:
    SPEECHBRAIN_AVAILABLE = False

VOICE_DIR = Path(r'D:\RPF_BRAIN\Archived\voiceprint')
VOICE_DIR.mkdir(parents=True, exist_ok=True)

# Initialize SpeechBrain if available
speechbrain_model = None
if SPEECHBRAIN_AVAILABLE:
    try:
        # Use pre-trained speaker verification model
        speechbrain_model = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir=str(VOICE_DIR / "models" / "speechbrain")
        )
        print("  ✅ SpeechBrain biometrics ready")
    except Exception as e:
        print(f"  ⚠️  SpeechBrain initialization failed: {e}")
        print("  ℹ️  Using numpy-based fallback")

def capture_my_voice():
    """Capture the master voiceprint - one time setup."""
    print("Gatekeeper: Speak your name. Just you.")
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    with mic as src:
        r.adjust_for_ambient_noise(src)
        audio = r.listen(src, timeout=3)
        
        data = np.frombuffer(
            audio.get_raw_data(convert_rate=16000, convert_width=2),
            dtype=np.int16
        ).astype(np.float32) / 32768.0
        
        # Save numpy-based voiceprint (fallback)
        np.save(VOICE_DIR / 'me.npy', data)
        
        # Also save SpeechBrain embedding if available
        if speechbrain_model:
            try:
                # Convert audio to tensor for SpeechBrain
                raw_data = audio.get_raw_data(convert_rate=16000, convert_width=2)
                audio_tensor = torch.tensor(
                    np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
                ).unsqueeze(0)
                
                # Extract embedding
                embedding = speechbrain_model.encode_batch(audio_tensor)
                embedding_np = embedding.squeeze().cpu().numpy()
                
                # Save SpeechBrain embedding
                np.save(VOICE_DIR / 'me_speechbrain.npy', embedding_np)
                print("Voice captured with SpeechBrain. You're now the master.")
            except Exception as e:
                print(f"  ⚠️  SpeechBrain capture failed, using numpy: {e}")
                print("Voice captured. You're now the master.")
        else:
            print("Voice captured. You're now the master.")
        
        return data

def load_voiceprint():
    """Load the saved voiceprint or capture if missing."""
    if not (VOICE_DIR / 'me.npy').exists():
        return capture_my_voice()
    return np.load(VOICE_DIR / 'me.npy')

def is_me(audio: sr.AudioData) -> bool:
    """Check if audio matches the master voiceprint using SpeechBrain or numpy fallback."""
    # Try SpeechBrain first (more accurate)
    if speechbrain_model and (VOICE_DIR / 'me_speechbrain.npy').exists():
        try:
            # Load master embedding
            master_embedding = np.load(VOICE_DIR / 'me_speechbrain.npy')
            
            # Extract embedding from current audio
            raw_data = audio.get_raw_data(convert_rate=16000, convert_width=2)
            audio_tensor = torch.tensor(
                np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
            ).unsqueeze(0)
            
            current_embedding = speechbrain_model.encode_batch(audio_tensor)
            current_embedding_np = current_embedding.squeeze().cpu().numpy()
            
            # Calculate cosine similarity
            similarity = np.dot(master_embedding, current_embedding_np) / (
                np.linalg.norm(master_embedding) * np.linalg.norm(current_embedding_np)
            )
            
            # Threshold: 0.8 for high confidence match
            return similarity >= 0.8
        except Exception as e:
            print(f"  ⚠️  SpeechBrain verification failed, using numpy fallback: {e}")
    
    # Fallback to numpy-based method
    my_wave = load_voiceprint()
    r = sr.Recognizer()
    
    data = np.frombuffer(
        audio.get_raw_data(convert_rate=16000, convert_width=2),
        dtype=np.int16
    ).astype(np.float32) / 32768.0
    
    # Simple zero-crossing + RMS match — good enough for local auth
    if abs(len(data) - len(my_wave)) > 100:
        return False
    
    rms_my = np.sqrt(np.mean(my_wave**2))
    rms_now = np.sqrt(np.mean(data**2))
    
    if abs(rms_my - rms_now) > 0.15:
        return False
    
    cross_my = np.sum(np.diff(np.sign(my_wave)) != 0)
    cross_now = np.sum(np.diff(np.sign(data)) != 0)
    
    return abs(cross_my - cross_now) < 300  # tuned on farm noise

if __name__ == "__main__":
    # One-time setup: capture voiceprint
    print("=" * 60)
    print("Gatekeeper Voiceprint Setup")
    print("=" * 60)
    print("\nThis is a one-time setup. Speak your name when prompted.")
    print("The Gatekeeper will only respond to your voice.\n")
    
    voiceprint = capture_my_voice()
    print(f"\nVoiceprint saved to: {VOICE_DIR / 'me.npy'}")
    print("Setup complete. The Gatekeeper is now locked to your voice.")
    print("\nTo use in voice_listener.py:")
    print("  from voiceprint_auth import is_me")
    print("  if is_me(audio):")
    print("      print('The doors of knowledge opens.')")

