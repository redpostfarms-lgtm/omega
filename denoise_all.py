# denoise_all.py — Batch audio denoising
import noisereduce as nr
import librosa
import soundfile as sf
import os
from pathlib import Path

def denoise_all(max_files=100):
    """Denoise all clip files in sequence."""
    processed = 0
    skipped = 0
    
    for i in range(1, max_files + 1):
        f = f"clip_{i:04d}.wav"
        
        if not os.path.exists(f):
            # Stop if we hit a gap and haven't processed anything recently
            if processed == 0:
                break
            skipped += 1
            if skipped > 10:  # Stop after 10 consecutive missing files
                break
            continue
        
        skipped = 0  # Reset skip counter
        
        try:
            print(f"Processing: {f}")
            y, sr = librosa.load(f, sr=22050)
            reduced = nr.reduce_noise(y=y, sr=sr, stationary=True)
            # Use soundfile instead of deprecated librosa.output.write_wav
            sf.write(f, reduced, sr)
            print(f"Clean: {f}")
            processed += 1
        except Exception as e:
            print(f"Error processing {f}: {e}")
            continue
    
    print(f"Processed {processed} files")

if __name__ == "__main__":
    denoise_all()
