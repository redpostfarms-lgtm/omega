#!/usr/bin/env python3
"""
Simple Voice Analyzer & Separator
Analyzes voice files and creates separated streams without heavy dependencies
"""
import os
import sys
from pathlib import Path
import subprocess
import json
from datetime import datetime

class SimpleVoiceSeparator:
    """Simple voice analysis and separation using FFmpeg"""

    def __init__(self):
        self.output_dir = Path("H:/The Gatekeeper/separated_voices")
        self.output_dir.mkdir(exist_ok=True)
        self.report = {
            "date": datetime.now().isoformat(),
            "processed_files": []
        }

    def get_audio_info(self, audio_path):
        """Get audio file information using FFprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return None
        except Exception as e:
            print(f"  ⚠️ FFprobe failed: {e}")
            return None

    def extract_voice_frequency_range(self, input_file, output_file):
        """Extract voice frequency range (85-255 Hz fundamental, harmonics up to 3kHz)"""
        try:
            # Apply highpass and lowpass filters to isolate voice
            cmd = [
                'ffmpeg', '-i', input_file,
                '-af', 'highpass=f=80,lowpass=f=3000,volume=2.0',
                '-y', output_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"  ❌ Voice extraction failed: {e}")
            return False

    def reduce_noise(self, input_file, output_file):
        """Apply noise reduction"""
        try:
            # Use FFmpeg's anlmdn filter for noise reduction
            cmd = [
                'ffmpeg', '-i', input_file,
                '-af', 'anlmdn=s=10:p=0.002:r=0.002:m=15,volume=1.5',
                '-y', output_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"  ❌ Noise reduction failed: {e}")
            return False

    def normalize_audio(self, input_file, output_file):
        """Normalize audio levels"""
        try:
            cmd = [
                'ffmpeg', '-i', input_file,
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                '-y', output_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"  ❌ Normalization failed: {e}")
            return False

    def process_file(self, audio_path):
        """Process a single audio file"""
        print("=" * 70)
        print(f"🎙️ Processing: {Path(audio_path).name}")

        if not os.path.exists(audio_path):
            print(f"  ❌ File not found!")
            return

        # Get file info
        info = self.get_audio_info(audio_path)
        if info:
            format_info = info.get('format', {})
            duration = float(format_info.get('duration', 0))
            size_mb = float(format_info.get('size', 0)) / (1024 * 1024)
            print(f"  Duration: {duration:.1f}s")
            print(f"  Size: {size_mb:.2f} MB")

        # Create output files
        filename = Path(audio_path).stem

        # 1. Extract voice frequency range
        voice_only = self.output_dir / f"{filename}_voice_only.wav"
        print(f"\n  🎵 Extracting voice frequencies...")
        if self.extract_voice_frequency_range(audio_path, str(voice_only)):
            print(f"    ✓ Saved: {voice_only.name}")

        # 2. Apply noise reduction
        clean_voice = self.output_dir / f"{filename}_clean.wav"
        print(f"  🧹 Reducing noise...")
        if os.path.exists(voice_only):
            if self.reduce_noise(str(voice_only), str(clean_voice)):
                print(f"    ✓ Saved: {clean_voice.name}")

        # 3. Normalize audio
        normalized = self.output_dir / f"{filename}_normalized.wav"
        print(f"  📊 Normalizing levels...")
        if os.path.exists(clean_voice):
            if self.normalize_audio(str(clean_voice), str(normalized)):
                print(f"    ✓ Saved: {normalized.name}")

        # Add to report
        self.report["processed_files"].append({
            "source": audio_path,
            "outputs": [
                str(voice_only),
                str(clean_voice),
                str(normalized)
            ]
        })

        print()

    def process_all_voices(self):
        """Process all key voice files"""
        print("\n" + "=" * 70)
        print("🌍 VOICE STREAM SEPARATOR & ANALYZER")
        print("=" * 70)
        print(f"📂 Output: {self.output_dir}\n")

        # Priority voice files to process
        voice_files = [
            ("Omega Primary", "H:/The Gatekeeper/omega_voice_best.wav"),
            ("Omega Original", "H:/The Gatekeeper/omega_downloaded.wav"),
            ("GATE/KITT Voice", "H:/The Gatekeeper/gate_kitt_voice.wav"),
            ("Sample Clip", "H:/The Gatekeeper/clip_0001.wav"),
        ]

        for name, path in voice_files:
            if os.path.exists(path):
                print(f"\n🎤 {name}")
                self.process_file(path)
            else:
                print(f"\n⚠️ {name}: Not found at {path}")

        # Save report
        report_file = self.output_dir / "separation_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.report, f, indent=2)

        print("=" * 70)
        print("✅ VOICE SEPARATION COMPLETE")
        print("=" * 70)
        print(f"\n📂 All processed voices saved to: {self.output_dir}")
        print(f"📄 Report: {report_file}")
        print(f"\nProcessed {len(self.report['processed_files'])} voice files")
        print("\nEach voice has 3 versions:")
        print("  1. _voice_only.wav  - Voice frequency range extracted")
        print("  2. _clean.wav       - Noise reduced")
        print("  3. _normalized.wav  - Volume normalized (ready for use)")
        print()

if __name__ == "__main__":
    separator = SimpleVoiceSeparator()
    separator.process_all_voices()
