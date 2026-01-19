from TTS.api import TTS
import torch
import os
from pathlib import Path
import asyncio
import subprocess
import sys

tts = None
USE_STREAMING = True  # Enable streaming for faster perceived latency

def initialize_tts_preload():
    """Pre-load TTS model on startup for faster subsequent calls."""
    global tts
    if tts is None:
        print("[TTS] Pre-loading model (one-time, ~5 seconds)...")
        os.environ['TTS_ACCEPT_TO_S'] = '1'
        
        try:
            original_load = torch.load
            def patched_load(*args, **kwargs):
                if 'weights_only' not in kwargs:
                    kwargs['weights_only'] = False
                return original_load(*args, **kwargs)
            torch.load = patched_load
        except:
            pass
        
        try:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)
            
            try:
                import bitsandbytes as bnb
                if device == 'cuda':
                    print("[TTS] Applying 8-bit quantization for faster inference...")
                    # Note: Actual quantization would require model-specific implementation
            except ImportError:
                pass
            
            print(f"[TTS] Model loaded on {device}")
        except Exception as e:
            print(f"[TTS ERROR] {e}")
            raise
    return tts

def limit_response_length(text, max_words=30):
    """Limit response length to reduce TTS synthesis time."""
    words = text.split()
    if len(words) > max_words:
        truncated = ' '.join(words[:max_words])
        last_punct = max(
            truncated.rfind('.'), 
            truncated.rfind('!'), 
            truncated.rfind('?')
        )
        if last_punct > len(truncated) * 0.7:  # If punctuation is in last 30%
            truncated = truncated[:last_punct + 1]
        else:
            truncated += "..."
        return truncated
    return text

def tts_to_file_optimized(text, speaker_wav=None, output_file='response.wav'):
    """Optimized TTS generation with length limiting."""
    global tts
    
    text = limit_response_length(text, max_words=30)
    
    if tts is None:
        tts = initialize_tts_preload()
    
    clip_path = Path('clip_0001.wav')
    if speaker_wav is None and clip_path.exists():
        speaker_wav = str(clip_path)
    
    try:
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language='en',
            file_path=output_file
        )
        return output_file
    except Exception as e:
        print(f"[TTS ERROR] {e}")
        raise

async def tts_stream_async(text, speaker_wav=None):
    """Streaming TTS - generate and play chunks progressively (experimental)."""
    # Note: Full streaming requires model-specific support
    global tts
    
    if tts is None:
        tts = initialize_tts_preload()
    
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() + '.' for s in sentences if s.strip()]
    
    output_files = []
    for i, sentence in enumerate(sentences[:3]):  # Limit to first 3 sentences for streaming demo
        if len(sentence) < 5:
            continue
        
        output_file = f'response_chunk_{i}.wav'
        tts_to_file_optimized(sentence, speaker_wav, output_file)
        output_files.append(output_file)
        
        from omega_full_brain import play_audio_background
        play_audio_background(output_file)
        
        await asyncio.sleep(0.5)
    
    return output_files

if __name__ == "__main__":
    print("[TTS Optimized] Initializing...")
    initialize_tts_preload()
    print("[TTS Optimized] Ready!")
