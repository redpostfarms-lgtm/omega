#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AZZ Voice Profile System
Complete voice synthesis with Azure Speech SDK and neural vocoders
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

# Voice profile paths
AZZ_VOICE_PATH = Path("H:/The Gatekeeper/voices/azz")
AZZ_SOURCE_AUDIO = Path("J:/audio files")
AZZ_VOICE_SAMPLE = AZZ_VOICE_PATH / "azz.wav"

# Ensure directories exist
AZZ_VOICE_PATH.mkdir(parents=True, exist_ok=True)
(AZZ_VOICE_PATH / "samples").mkdir(exist_ok=True)
(AZZ_VOICE_PATH / "processed").mkdir(exist_ok=True)
(AZZ_VOICE_PATH / "models").mkdir(exist_ok=True)


class AZZVoiceSystem:
    """
    AZZ Voice Profile System
    - Audio analysis and feature extraction
    - Azure Speech SDK integration
    - Neural vocoder synthesis
    - Multi-voice routing
    """

    def __init__(self):
        self.voice_path = AZZ_VOICE_PATH
        self.source_audio = AZZ_SOURCE_AUDIO
        self.config_file = self.voice_path / "azz_config.json"

        # Load or create config
        self.config = self.load_config()

        # Initialize Azure (if available)
        self.azure_speech = None
        self.initialize_azure()

    def load_config(self) -> Dict:
        """Load AZZ voice configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)

        # Default configuration
        return {
            "profile_name": "AZZ",
            "description": "AZZ voice profile for Omega system",
            "voice_features": {
                "pitch_range": [80, 250],
                "speaking_rate": 1.0,
                "volume": 1.0,
                "emotion": "neutral"
            },
            "azure_config": {
                "enabled": True,
                "voice_name": "en-US-AvaMultilingualNeural",
                "style": "chat",
                "language": "en-US"
            },
            "source_files": [],
            "processed_models": [],
            "synthesis_backend": "azure"  # azure, coqui-tts, or neural
        }

    def save_config(self):
        """Save AZZ voice configuration"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def initialize_azure(self):
        """Initialize Azure Speech SDK"""
        try:
            import azure.cognitiveservices.speech as speechsdk

            api_key = os.getenv("AZURE_SPEECH_KEY")
            region = os.getenv("AZURE_SPEECH_REGION", "eastus")

            if api_key:
                speech_config = speechsdk.SpeechConfig(
                    subscription=api_key,
                    region=region
                )

                # Configure voice
                speech_config.speech_synthesis_voice_name = (
                    self.config["azure_config"]["voice_name"]
                )

                self.azure_speech = speech_config
                self.log("✓ Azure Speech SDK initialized")
            else:
                self.log("⚠ Azure Speech API key not set (AZURE_SPEECH_KEY)")

        except ImportError:
            self.log("⚠ Azure Speech SDK not installed")
            self.log("  Install: pip install azure-cognitiveservices-speech")

    def log(self, message: str):
        """Log message"""
        print(f"[AZZ] {message}")

    # ============================================
    # AUDIO ANALYSIS
    # ============================================

    def analyze_audio_file(self, audio_path: Path) -> Dict:
        """Analyze audio file and extract features"""
        try:
            import librosa
            import scipy.io.wavfile as wavfile

            self.log(f"Analyzing: {audio_path.name}")

            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)

            # Extract features
            features = {
                "file": str(audio_path),
                "duration": len(y) / sr,
                "sample_rate": sr,
                "channels": 1 if len(y.shape) == 1 else y.shape[1],
            }

            # Pitch analysis
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []

            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)

            if pitch_values:
                features["pitch"] = {
                    "mean": float(np.mean(pitch_values)),
                    "min": float(np.min(pitch_values)),
                    "max": float(np.max(pitch_values)),
                    "std": float(np.std(pitch_values))
                }

            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features["spectral_centroid"] = {
                "mean": float(np.mean(spectral_centroids)),
                "std": float(np.std(spectral_centroids))
            }

            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            features["zero_crossing_rate"] = {
                "mean": float(np.mean(zcr)),
                "std": float(np.std(zcr))
            }

            # MFCCs
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features["mfcc_mean"] = mfccs.mean(axis=1).tolist()

            self.log(f"  Duration: {features['duration']:.2f}s")
            self.log(f"  Sample rate: {sr} Hz")
            if "pitch" in features:
                self.log(f"  Pitch range: {features['pitch']['min']:.1f}-{features['pitch']['max']:.1f} Hz")

            return features

        except ImportError as e:
            self.log(f"✗ Missing library: {e}")
            self.log("  Install: pip install librosa scipy")
            return {}
        except Exception as e:
            self.log(f"✗ Error analyzing {audio_path.name}: {e}")
            return {}

    def analyze_all_source_files(self) -> List[Dict]:
        """Analyze all source audio files"""
        self.log("Analyzing all source audio files...")

        analyses = []

        if not self.source_audio.exists():
            self.log(f"✗ Source directory not found: {self.source_audio}")
            return analyses

        wav_files = list(self.source_audio.glob("*.wav"))
        self.log(f"Found {len(wav_files)} WAV files")

        for wav_file in wav_files:
            analysis = self.analyze_audio_file(wav_file)
            if analysis:
                analyses.append(analysis)

        # Update config
        self.config["source_files"] = [str(f) for f in wav_files]
        self.save_config()

        return analyses

    def create_voice_profile_from_samples(self, sample_files: List[Path]) -> Dict:
        """Create voice profile from multiple samples"""
        self.log("Creating voice profile from samples...")

        all_features = []

        for sample in sample_files:
            features = self.analyze_audio_file(sample)
            if features:
                all_features.append(features)

        if not all_features:
            return {}

        # Aggregate features
        profile = {
            "num_samples": len(all_features),
            "total_duration": sum(f["duration"] for f in all_features),
            "sample_rate": all_features[0]["sample_rate"],
        }

        # Average pitch
        pitch_data = [f["pitch"] for f in all_features if "pitch" in f]
        if pitch_data:
            profile["pitch"] = {
                "mean": float(np.mean([p["mean"] for p in pitch_data])),
                "min": float(np.min([p["min"] for p in pitch_data])),
                "max": float(np.max([p["max"] for p in pitch_data])),
            }

        self.log(f"✓ Voice profile created from {len(all_features)} samples")

        # Save profile
        profile_file = self.voice_path / "voice_profile.json"
        with open(profile_file, "w") as f:
            json.dump(profile, f, indent=2)

        return profile

    # ============================================
    # VOICE SYNTHESIS
    # ============================================

    def synthesize_with_azure(self, text: str, output_path: Optional[Path] = None) -> bool:
        """Synthesize speech using Azure Speech SDK"""
        if not self.azure_speech:
            self.log("✗ Azure Speech not initialized")
            return False

        try:
            import azure.cognitiveservices.speech as speechsdk

            if output_path is None:
                output_path = self.voice_path / "processed" / f"output_{int(time.time())}.wav"

            # Create synthesizer
            audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.azure_speech,
                audio_config=audio_config
            )

            # Generate SSML
            ssml = self.generate_ssml(text)

            # Synthesize
            result = synthesizer.speak_ssml_async(ssml).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                self.log(f"✓ Synthesized to: {output_path}")
                return True
            else:
                self.log(f"✗ Synthesis failed: {result.reason}")
                return False

        except Exception as e:
            self.log(f"✗ Azure synthesis error: {e}")
            return False

    def generate_ssml(self, text: str) -> str:
        """Generate SSML for Azure synthesis"""
        voice_name = self.config["azure_config"]["voice_name"]
        style = self.config["azure_config"]["style"]
        speaking_rate = self.config["voice_features"]["speaking_rate"]
        pitch = "+0%"  # Can be adjusted based on analysis

        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
               xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{voice_name}">
                <mstts:express-as style="{style}">
                    <prosody rate="{speaking_rate}" pitch="{pitch}">
                        {text}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
        """

        return ssml.strip()

    def synthesize_with_coqui(self, text: str, output_path: Optional[Path] = None) -> bool:
        """Synthesize speech using Coqui TTS"""
        try:
            from TTS.api import TTS

            if output_path is None:
                output_path = self.voice_path / "processed" / f"output_{int(time.time())}.wav"

            # Initialize TTS (voice cloning)
            tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")

            # Get reference audio
            reference_audio = self.voice_path / "azz.wav"
            if not reference_audio.exists():
                self.log("✗ Reference audio not found: azz.wav")
                return False

            # Generate speech
            tts.tts_to_file(
                text=text,
                speaker_wav=str(reference_audio),
                language="en",
                file_path=str(output_path)
            )

            self.log(f"✓ Synthesized to: {output_path}")
            return True

        except ImportError:
            self.log("✗ Coqui TTS not installed")
            self.log("  Install: pip install TTS")
            return False
        except Exception as e:
            self.log(f"✗ Coqui synthesis error: {e}")
            return False

    def synthesize_speech(self, text: str, backend: Optional[str] = None) -> Optional[Path]:
        """Synthesize speech using configured backend"""
        backend = backend or self.config["synthesis_backend"]

        output_path = self.voice_path / "processed" / f"azz_output_{int(time.time())}.wav"

        if backend == "azure":
            success = self.synthesize_with_azure(text, output_path)
        elif backend == "coqui-tts":
            success = self.synthesize_with_coqui(text, output_path)
        else:
            self.log(f"✗ Unknown backend: {backend}")
            return None

        return output_path if success else None

    # ============================================
    # VOICE PROFILE MANAGEMENT
    # ============================================

    def copy_source_samples(self):
        """Copy source audio files to AZZ voice directory"""
        self.log("Copying source audio samples...")

        if not self.source_audio.exists():
            self.log(f"✗ Source directory not found: {self.source_audio}")
            return

        copied = 0
        for wav_file in self.source_audio.glob("*.wav"):
            dest = self.voice_path / "samples" / wav_file.name

            if not dest.exists():
                import shutil
                shutil.copy2(wav_file, dest)
                self.log(f"  ✓ Copied: {wav_file.name}")
                copied += 1

        self.log(f"✓ Copied {copied} audio files")

    def select_best_sample(self) -> Optional[Path]:
        """Select best sample for voice profile"""
        samples = list((self.voice_path / "samples").glob("*.wav"))

        if not samples:
            self.log("✗ No samples found")
            return None

        # Analyze all and pick the cleanest
        best_sample = None
        best_score = 0

        for sample in samples:
            features = self.analyze_audio_file(sample)
            if not features:
                continue

            # Simple scoring: longer duration + clear pitch
            score = features["duration"]
            if "pitch" in features and features["pitch"]["std"] < 50:
                score += 10

            if score > best_score:
                best_score = score
                best_sample = sample

        if best_sample:
            self.log(f"✓ Best sample: {best_sample.name}")

            # Create azz.wav as the primary reference
            import shutil
            shutil.copy2(best_sample, AZZ_VOICE_SAMPLE)

        return best_sample


def main():
    """Main entry point"""
    import time

    print("\n" + "=" * 70)
    print("  AZZ VOICE PROFILE SYSTEM")
    print("=" * 70 + "\n")

    azz = AZZVoiceSystem()

    print("Voice Profile Configuration:")
    print(f"  Profile: {azz.config['profile_name']}")
    print(f"  Voice path: {azz.voice_path}")
    print(f"  Source audio: {azz.source_audio}")
    print(f"  Synthesis backend: {azz.config['synthesis_backend']}")

    print("\nOptions:")
    print("  1. Analyze source audio files")
    print("  2. Copy source samples to voice directory")
    print("  3. Create voice profile from samples")
    print("  4. Test Azure synthesis")
    print("  5. Test Coqui TTS synthesis")
    print("  6. Complete setup (all steps)")

    choice = input("\nChoice (1-6): ").strip()

    if choice == "1":
        analyses = azz.analyze_all_source_files()
        print(f"\n✓ Analyzed {len(analyses)} files")

    elif choice == "2":
        azz.copy_source_samples()
        azz.select_best_sample()

    elif choice == "3":
        samples = list((azz.voice_path / "samples").glob("*.wav"))
        if samples:
            profile = azz.create_voice_profile_from_samples(samples)
            print(json.dumps(profile, indent=2))
        else:
            print("No samples found. Run option 2 first.")

    elif choice == "4":
        test_text = "Hello, I am AZZ, the voice profile for the Omega system."
        output = azz.synthesize_speech(test_text, backend="azure")
        if output:
            print(f"\n✓ Synthesis complete: {output}")

    elif choice == "5":
        test_text = "Hello, I am AZZ, powered by neural voice synthesis."
        output = azz.synthesize_speech(test_text, backend="coqui-tts")
        if output:
            print(f"\n✓ Synthesis complete: {output}")

    elif choice == "6":
        print("\nRunning complete setup...\n")

        # Step 1: Copy samples
        azz.copy_source_samples()
        best_sample = azz.select_best_sample()

        # Step 2: Analyze
        analyses = azz.analyze_all_source_files()
        print(f"\n✓ Analyzed {len(analyses)} files")

        # Step 3: Create profile
        samples = list((azz.voice_path / "samples").glob("*.wav"))
        profile = azz.create_voice_profile_from_samples(samples)
        print(f"\n✓ Voice profile created")

        # Step 4: Test synthesis
        test_text = "AZZ voice profile setup complete."
        output = azz.synthesize_speech(test_text)
        if output:
            print(f"\n✓ Test synthesis: {output}")

        print("\n" + "=" * 70)
        print("  AZZ VOICE PROFILE SETUP COMPLETE")
        print("=" * 70)


if __name__ == "__main__":
    import time
    main()
