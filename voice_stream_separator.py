#!/usr/bin/env python3
"""
Voice Stream Separator
Separates multiple voice streams from audio files
"""
import os
import sys
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

class VoiceStreamSeparator:
    """Separate different voices from audio files"""

    def __init__(self):
        self.output_dir = Path("H:/The Gatekeeper/separated_voices")
        self.output_dir.mkdir(exist_ok=True)
        print(f"📂 Output: {self.output_dir}\n")

    def analyze_audio(self, audio_path):
        """Analyze audio file for voice characteristics"""
        print(f"🔍 Analyzing: {Path(audio_path).name}")

        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=22050)
            duration = len(y) / sr

            print(f"  Duration: {duration:.1f}s, Sample Rate: {sr}Hz")

            # Extract features
            # 1. Spectral centroid (brightness)
            cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            avg_cent = np.mean(cent)

            # 2. Zero crossing rate (voice texture)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            avg_zcr = np.mean(zcr)

            # 3. RMS energy
            rms = librosa.feature.rms(y=y)[0]
            avg_rms = np.mean(rms)

            # 4. MFCCs for voice print
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)

            print(f"  Brightness: {avg_cent:.0f} Hz")
            print(f"  Energy: {avg_rms:.4f}")
            print(f"  Texture: {avg_zcr:.4f}")

            # Detect if likely multiple speakers
            # Look for variation in spectral features
            cent_std = np.std(cent)
            variation = cent_std / avg_cent if avg_cent > 0 else 0

            if variation > 0.3:
                print(f"  ⚠️ High variation detected ({variation:.2f}) - possible multiple speakers")
                return True, y, sr, mfccs
            else:
                print(f"  ✓ Single speaker likely ({variation:.2f})")
                return False, y, sr, mfccs

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False, None, None, None

    def separate_speakers(self, y, sr, mfccs, output_prefix, n_speakers=2):
        """Attempt to separate multiple speakers using clustering"""
        print(f"\n  🎙️ Attempting to separate {n_speakers} speakers...")

        try:
            # Use MFCCs for clustering
            # Transpose to get (time_frames, features)
            features = mfccs.T

            # Cluster the features
            kmeans = KMeans(n_clusters=n_speakers, random_state=42, n_init=10)
            labels = kmeans.fit_predict(features)

            # Separate audio based on clusters
            hop_length = 512

            for speaker_id in range(n_speakers):
                # Find frames belonging to this speaker
                speaker_frames = np.where(labels == speaker_id)[0]

                if len(speaker_frames) < 10:
                    continue

                # Create mask for this speaker
                mask = np.zeros(len(y))

                for frame_idx in speaker_frames:
                    start_sample = frame_idx * hop_length
                    end_sample = min(start_sample + hop_length, len(y))
                    mask[start_sample:end_sample] = 1

                # Apply mask
                speaker_audio = y * mask

                # Remove silence
                speaker_audio = speaker_audio[np.abs(speaker_audio) > 0.01]

                if len(speaker_audio) > sr:  # At least 1 second
                    output_file = f"{output_prefix}_speaker_{speaker_id+1}.wav"
                    sf.write(output_file, speaker_audio, sr)
                    duration = len(speaker_audio) / sr
                    print(f"    ✓ Speaker {speaker_id+1}: {duration:.1f}s saved")

            return True

        except Exception as e:
            print(f"    ❌ Separation failed: {e}")
            return False

    def extract_voice_only(self, y, sr, output_file):
        """Extract voice component using harmonic-percussive separation"""
        print(f"\n  🎵 Extracting voice component...")

        try:
            # Separate harmonic (voice/music) from percussive (drums/noise)
            y_harmonic, y_percussive = librosa.effects.hpss(y)

            # Further isolate voice frequencies (typically 85-255 Hz fundamental)
            # Apply bandpass filter
            from scipy import signal as scipy_signal

            # Design bandpass filter for voice range (80-3000 Hz)
            sos = scipy_signal.butter(10, [80, 3000], 'bandpass', fs=sr, output='sos')
            y_voice = scipy_signal.sosfilt(sos, y_harmonic)

            # Save voice-only audio
            sf.write(output_file, y_voice, sr)
            print(f"    ✓ Voice extracted: {output_file}")

            return True

        except Exception as e:
            print(f"    ❌ Extraction failed: {e}")
            return False

    def process_file(self, audio_path):
        """Process a single audio file"""
        print("=" * 70)

        # Analyze
        multi_speaker, y, sr, mfccs = self.analyze_audio(audio_path)

        if y is None:
            return

        # Create output prefix
        filename = Path(audio_path).stem
        output_prefix = self.output_dir / filename

        # Extract voice component
        voice_file = f"{output_prefix}_voice_only.wav"
        self.extract_voice_only(y, sr, voice_file)

        # If multiple speakers detected, try separation
        if multi_speaker:
            self.separate_speakers(y, sr, mfccs, str(output_prefix))

        print()

    def process_priority_files(self):
        """Process key voice files"""
        priority_files = [
            "H:/The Gatekeeper/omega_voice_best.wav",
            "H:/The Gatekeeper/omega_downloaded.wav",
            "H:/The Gatekeeper/gate_kitt_voice.wav",
            "H:/The Gatekeeper/clip_0001.wav",
        ]

        print("🎤 VOICE STREAM SEPARATOR")
        print("=" * 70)
        print("Processing priority voice files...\n")

        for file_path in priority_files:
            if os.path.exists(file_path):
                self.process_file(file_path)
            else:
                print(f"⚠️ Not found: {file_path}\n")

        print("=" * 70)
        print("✅ SEPARATION COMPLETE")
        print(f"📂 Output directory: {self.output_dir}")
        print("=" * 70)

if __name__ == "__main__":
    separator = VoiceStreamSeparator()
    separator.process_priority_files()
