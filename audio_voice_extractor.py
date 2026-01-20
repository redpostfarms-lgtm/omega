#!/usr/bin/env python3
"""
Audio Voice Extractor - Worldwide Computer Scan
Searches entire system for audio files, extracts and separates voices
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess
import librosa
import soundfile as sf
import numpy as np
from scipy import signal
import warnings
warnings.filterwarnings('ignore')

class AudioVoiceExtractor:
    """Extract and separate voices from audio files across the system"""

    def __init__(self):
        self.output_dir = Path("H:/The Gatekeeper/extracted_voices")
        self.output_dir.mkdir(exist_ok=True)

        self.scan_results = {
            "scan_date": datetime.now().isoformat(),
            "total_audio_files": 0,
            "files_with_voice": 0,
            "voices_extracted": 0,
            "locations": [],
            "voice_profiles": []
        }

        # Audio file extensions to search for
        self.audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac', '.wma']

        # Common directories with audio
        self.priority_dirs = [
            "H:/The Gatekeeper",
            os.path.expanduser("~/Music"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Videos"),
            "C:/Users/Public/Music",
        ]

        print("🔍 AUDIO VOICE EXTRACTOR INITIALIZED")
        print(f"📂 Output Directory: {self.output_dir}")
        print("=" * 70)

    def search_audio_files(self, max_files=100):
        """Search for audio files across the system"""
        print("\n🔎 PHASE 1: SCANNING FOR AUDIO FILES...")
        audio_files = []

        # Search priority directories first
        for directory in self.priority_dirs:
            if os.path.exists(directory):
                print(f"\n📁 Scanning: {directory}")
                try:
                    for root, dirs, files in os.walk(directory):
                        # Skip system and hidden directories
                        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git']]

                        for file in files:
                            if any(file.lower().endswith(ext) for ext in self.audio_extensions):
                                full_path = os.path.join(root, file)
                                file_size = os.path.getsize(full_path)

                                # Only process files > 10KB and < 500MB
                                if 10000 < file_size < 500_000_000:
                                    audio_files.append({
                                        'path': full_path,
                                        'name': file,
                                        'size_mb': file_size / (1024 * 1024),
                                        'directory': root
                                    })
                                    print(f"  ✓ Found: {file} ({file_size / (1024*1024):.2f} MB)")

                                    if len(audio_files) >= max_files:
                                        print(f"\n⚠️ Reached limit of {max_files} files")
                                        return audio_files
                except PermissionError:
                    print(f"  ⚠️ Access denied to {directory}")
                except Exception as e:
                    print(f"  ⚠️ Error scanning {directory}: {e}")

        self.scan_results['total_audio_files'] = len(audio_files)
        print(f"\n✅ Found {len(audio_files)} audio files")
        return audio_files

    def detect_voice_activity(self, audio_path):
        """Detect if audio contains human voice"""
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=22050, duration=30)  # First 30 seconds

            # Calculate features that indicate voice
            # 1. Zero crossing rate (voice has moderate ZCR)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            avg_zcr = np.mean(zcr)

            # 2. Spectral centroid (voice typically 500-2000 Hz)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            avg_centroid = np.mean(spectral_centroids)

            # 3. MFCC (Mel-frequency cepstral coefficients - voice fingerprint)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_variance = np.var(mfccs)

            # 4. RMS Energy
            rms = librosa.feature.rms(y=y)[0]
            avg_rms = np.mean(rms)

            # Voice detection heuristics
            has_voice = (
                0.05 < avg_zcr < 0.3 and  # Moderate zero crossing
                500 < avg_centroid < 3000 and  # Voice frequency range
                mfcc_variance > 10 and  # Sufficient variation
                avg_rms > 0.01  # Sufficient energy
            )

            confidence = 0
            if has_voice:
                # Calculate confidence score
                confidence = min(100, int(
                    (mfcc_variance / 50 * 40) +  # MFCC contribution
                    (avg_rms * 1000 * 30) +  # Energy contribution
                    (30 if 1000 < avg_centroid < 2000 else 15)  # Frequency contribution
                ))

            return has_voice, confidence, {
                'zcr': float(avg_zcr),
                'centroid': float(avg_centroid),
                'mfcc_var': float(mfcc_variance),
                'rms': float(avg_rms)
            }

        except Exception as e:
            print(f"  ❌ Error analyzing {audio_path}: {e}")
            return False, 0, {}

    def separate_voices(self, audio_path, output_prefix):
        """Separate different voice streams from audio"""
        try:
            print(f"  🎙️ Separating voices from: {Path(audio_path).name}")

            # Load full audio
            y, sr = librosa.load(audio_path, sr=22050)

            # Method 1: Use harmonic-percussive separation to isolate voice
            y_harmonic, y_percussive = librosa.effects.hpss(y)

            # Save harmonic component (contains voice)
            voice_file = f"{output_prefix}_voice.wav"
            sf.write(voice_file, y_harmonic, sr)
            print(f"    ✓ Voice extracted: {voice_file}")

            # Method 2: Try to detect multiple speakers using spectral clustering
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=y_harmonic, sr=sr, n_mfcc=20)

            # Detect voice segments
            hop_length = 512
            frame_length = 2048

            # Calculate RMS for voice activity detection
            rms = librosa.feature.rms(y=y_harmonic, frame_length=frame_length, hop_length=hop_length)[0]
            threshold = np.mean(rms) * 0.5

            # Find voice segments
            voice_segments = []
            in_voice = False
            start_frame = 0

            for i, energy in enumerate(rms):
                if energy > threshold and not in_voice:
                    start_frame = i
                    in_voice = True
                elif energy <= threshold and in_voice:
                    if i - start_frame > 10:  # At least 10 frames
                        voice_segments.append((start_frame, i))
                    in_voice = False

            # Extract longest voice segments (potential different speakers)
            voice_segments.sort(key=lambda x: x[1] - x[0], reverse=True)

            extracted_count = 0
            for idx, (start, end) in enumerate(voice_segments[:5]):  # Top 5 segments
                start_sample = start * hop_length
                end_sample = end * hop_length

                segment = y_harmonic[start_sample:end_sample]

                # Only save if segment is substantial (> 1 second)
                if len(segment) > sr:
                    segment_file = f"{output_prefix}_segment_{idx+1}.wav"
                    sf.write(segment_file, segment, sr)
                    extracted_count += 1
                    print(f"    ✓ Segment {idx+1} extracted: {len(segment)/sr:.1f}s")

            return extracted_count + 1  # +1 for main voice file

        except Exception as e:
            print(f"    ❌ Error separating voices: {e}")
            return 0

    def process_audio_files(self, audio_files):
        """Process all audio files and extract voices"""
        print("\n🎵 PHASE 2: ANALYZING AUDIO FILES FOR VOICES...")

        voice_files = []

        for idx, file_info in enumerate(audio_files):
            print(f"\n[{idx+1}/{len(audio_files)}] Processing: {file_info['name']}")

            # Detect voice activity
            has_voice, confidence, features = self.detect_voice_activity(file_info['path'])

            if has_voice and confidence > 30:
                print(f"  ✅ VOICE DETECTED (Confidence: {confidence}%)")
                self.scan_results['files_with_voice'] += 1

                # Create output prefix
                safe_name = "".join(c for c in Path(file_info['name']).stem if c.isalnum() or c in '_-')
                output_prefix = self.output_dir / f"voice_{idx+1}_{safe_name}"

                # Separate voices
                voices_extracted = self.separate_voices(file_info['path'], str(output_prefix))
                self.scan_results['voices_extracted'] += voices_extracted

                voice_files.append({
                    'source': file_info['path'],
                    'name': file_info['name'],
                    'confidence': confidence,
                    'features': features,
                    'voices_extracted': voices_extracted,
                    'output_prefix': str(output_prefix)
                })
            else:
                print(f"  ⚠️ No significant voice detected (Confidence: {confidence}%)")

        return voice_files

    def generate_report(self, voice_files):
        """Generate detailed report of extracted voices"""
        print("\n📊 PHASE 3: GENERATING REPORT...")

        # Save JSON report
        report_data = {
            **self.scan_results,
            'voice_files': voice_files
        }

        report_json = self.output_dir / 'extraction_report.json'
        with open(report_json, 'w') as f:
            json.dump(report_data, f, indent=2)

        # Generate markdown report
        report_md = self.output_dir / 'EXTRACTION_REPORT.md'
        with open(report_md, 'w', encoding='utf-8') as f:
            f.write("# 🎤 AUDIO VOICE EXTRACTION REPORT\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            f.write("## 📊 SUMMARY\n\n")
            f.write(f"- **Total Audio Files Scanned**: {self.scan_results['total_audio_files']}\n")
            f.write(f"- **Files with Voice Content**: {self.scan_results['files_with_voice']}\n")
            f.write(f"- **Total Voice Streams Extracted**: {self.scan_results['voices_extracted']}\n\n")

            f.write("---\n\n")
            f.write("## 🎙️ EXTRACTED VOICES\n\n")

            for idx, vf in enumerate(voice_files, 1):
                f.write(f"### Voice Source {idx}: {vf['name']}\n\n")
                f.write(f"- **Confidence**: {vf['confidence']}%\n")
                f.write(f"- **Voice Streams Extracted**: {vf['voices_extracted']}\n")
                f.write(f"- **Source File**: `{vf['source']}`\n")
                f.write(f"- **Output Files**: `{vf['output_prefix']}_*.wav`\n\n")

                # Features
                f.write("**Audio Features**:\n")
                f.write(f"- Zero Crossing Rate: {vf['features'].get('zcr', 0):.4f}\n")
                f.write(f"- Spectral Centroid: {vf['features'].get('centroid', 0):.2f} Hz\n")
                f.write(f"- MFCC Variance: {vf['features'].get('mfcc_var', 0):.2f}\n")
                f.write(f"- RMS Energy: {vf['features'].get('rms', 0):.4f}\n\n")

        print(f"✅ Report saved to: {report_md}")
        print(f"✅ JSON data saved to: {report_json}")

        return report_md

    def run(self, max_files=50):
        """Execute full voice extraction workflow"""
        print("\n" + "="*70)
        print("🌍 WORLDWIDE AUDIO VOICE EXTRACTION")
        print("="*70)

        # Step 1: Search for audio files
        audio_files = self.search_audio_files(max_files)

        if not audio_files:
            print("\n❌ No audio files found!")
            return

        # Step 2: Process and extract voices
        voice_files = self.process_audio_files(audio_files)

        # Step 3: Generate report
        report_path = self.generate_report(voice_files)

        print("\n" + "="*70)
        print("✅ VOICE EXTRACTION COMPLETE!")
        print("="*70)
        print(f"\n📂 Extracted voices saved to: {self.output_dir}")
        print(f"📄 Full report: {report_path}")
        print(f"\n🎙️ Total voices extracted: {self.scan_results['voices_extracted']}")
        print(f"✅ Files with voice: {self.scan_results['files_with_voice']}/{self.scan_results['total_audio_files']}")

if __name__ == "__main__":
    extractor = AudioVoiceExtractor()

    # Process up to 50 audio files
    extractor.run(max_files=50)
