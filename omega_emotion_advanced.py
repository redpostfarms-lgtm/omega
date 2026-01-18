"""
Advanced Emotion Detection for Omega Voice System
==================================================
Real-time emotion detection from audio using wav2vec2 models

Features:
- 7-emotion classification (neutral, happy, sad, angry, fear, disgust, surprise)
- Real-time audio analysis
- Integration with Omega voice system
- Confidence scoring
- Emotion history tracking

Requirements:
- transformers>=4.36.0
- torch>=2.0.0
- librosa>=0.10.0
- numpy>=1.24.0
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

try:
    import torch
    import librosa
    import numpy as np
    from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("Warning: Advanced emotion detection dependencies not available.")
    print("Install: py -3.11 -m pip install transformers torch librosa")


@dataclass
class EmotionResult:
    """Result from emotion detection"""
    emotion: str
    confidence: float
    all_scores: Dict[str, float]
    timestamp: datetime
    audio_duration: float

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'emotion': self.emotion,
            'confidence': self.confidence,
            'all_scores': self.all_scores,
            'timestamp': self.timestamp.isoformat(),
            'audio_duration': self.audio_duration
        }


class AdvancedEmotionDetector:
    """
    Advanced emotion detection using wav2vec2 models

    Uses: ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition
    Detects: neutral, happy, sad, angry, fear, disgust, surprise
    """

    # Model configuration
    DEFAULT_MODEL = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
    EMOTION_LABELS = ['neutral', 'happy', 'sad', 'angry', 'fear', 'disgust', 'surprise']

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: Optional[str] = None,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize advanced emotion detector

        Args:
            model_name: Hugging Face model identifier
            device: 'cuda', 'cpu', or None for auto-detect
            cache_dir: Directory for model cache
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.available = DEPENDENCIES_AVAILABLE

        if not self.available:
            self.logger.warning("Advanced emotion detection unavailable - missing dependencies")
            return

        # Auto-detect device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.logger.info(f"Using device: {self.device}")

        # Set cache directory
        if cache_dir:
            os.environ['TRANSFORMERS_CACHE'] = cache_dir

        # Initialize model and feature extractor
        try:
            self.logger.info(f"Loading model: {model_name}")
            self.model = AutoModelForAudioClassification.from_pretrained(model_name)
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            self.available = False
            self.model = None
            self.feature_extractor = None

        # Emotion history
        self.emotion_history: List[EmotionResult] = []
        self.max_history = 100

    def detect_from_file(self, audio_path: str) -> Optional[EmotionResult]:
        """
        Detect emotion from audio file

        Args:
            audio_path: Path to audio file (.wav, .mp3, etc.)

        Returns:
            EmotionResult with detected emotion and confidence
        """
        if not self.available:
            return self._fallback_result(0.0)

        try:
            # Load audio file
            audio, sample_rate = librosa.load(audio_path, sr=16000, mono=True)
            duration = len(audio) / sample_rate

            # Detect emotion
            result = self.detect_from_audio(audio, sample_rate)
            if result:
                result.audio_duration = duration

            return result

        except Exception as e:
            self.logger.error(f"Error detecting emotion from file: {e}")
            return self._fallback_result(0.0)

    def detect_from_audio(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000
    ) -> Optional[EmotionResult]:
        """
        Detect emotion from raw audio array

        Args:
            audio: Audio waveform (numpy array)
            sample_rate: Sample rate (should be 16000 for wav2vec2)

        Returns:
            EmotionResult with detected emotion and confidence
        """
        if not self.available:
            return self._fallback_result(len(audio) / sample_rate)

        try:
            # Resample if needed
            if sample_rate != 16000:
                audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)

            # Extract features
            inputs = self.feature_extractor(
                audio,
                sampling_rate=16000,
                return_tensors="pt",
                padding=True
            )

            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits

            # Get probabilities
            probs = torch.nn.functional.softmax(logits, dim=-1)
            probs = probs.cpu().numpy()[0]

            # Get emotion scores
            emotion_scores = {}
            for i, label in enumerate(self.EMOTION_LABELS):
                emotion_scores[label] = float(probs[i])

            # Get top emotion
            top_emotion_idx = np.argmax(probs)
            top_emotion = self.EMOTION_LABELS[top_emotion_idx]
            top_confidence = float(probs[top_emotion_idx])

            # Create result
            result = EmotionResult(
                emotion=top_emotion,
                confidence=top_confidence,
                all_scores=emotion_scores,
                timestamp=datetime.now(),
                audio_duration=len(audio) / 16000
            )

            # Add to history
            self._add_to_history(result)

            self.logger.info(
                f"Detected emotion: {top_emotion} "
                f"(confidence: {top_confidence:.2%})"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error detecting emotion: {e}")
            return self._fallback_result(len(audio) / sample_rate if len(audio) > 0 else 0.0)

    def get_emotion_trend(self, window: int = 5) -> Dict[str, float]:
        """
        Get emotion trend over recent detections

        Args:
            window: Number of recent detections to analyze

        Returns:
            Dictionary of average emotion scores
        """
        if not self.emotion_history:
            return {label: 0.0 for label in self.EMOTION_LABELS}

        # Get recent results
        recent = self.emotion_history[-window:]

        # Average scores
        avg_scores = {label: 0.0 for label in self.EMOTION_LABELS}
        for result in recent:
            for label, score in result.all_scores.items():
                avg_scores[label] += score

        # Normalize
        count = len(recent)
        for label in avg_scores:
            avg_scores[label] /= count

        return avg_scores

    def get_dominant_emotion(self, window: int = 5) -> str:
        """
        Get the dominant emotion over recent detections

        Args:
            window: Number of recent detections to analyze

        Returns:
            Dominant emotion label
        """
        trend = self.get_emotion_trend(window)
        return max(trend.items(), key=lambda x: x[1])[0]

    def clear_history(self):
        """Clear emotion history"""
        self.emotion_history.clear()
        self.logger.info("Emotion history cleared")

    def _add_to_history(self, result: EmotionResult):
        """Add result to history with size limit"""
        self.emotion_history.append(result)
        if len(self.emotion_history) > self.max_history:
            self.emotion_history.pop(0)

    def _fallback_result(self, duration: float) -> EmotionResult:
        """Create fallback result when detection unavailable"""
        return EmotionResult(
            emotion='neutral',
            confidence=0.0,
            all_scores={label: 0.0 for label in self.EMOTION_LABELS},
            timestamp=datetime.now(),
            audio_duration=duration
        )

    def save_history(self, filepath: str):
        """Save emotion history to JSON file"""
        history_data = [result.to_dict() for result in self.emotion_history]
        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2)
        self.logger.info(f"Saved {len(history_data)} emotion results to {filepath}")

    def get_stats(self) -> Dict:
        """Get statistics about emotion detection"""
        if not self.emotion_history:
            return {
                'total_detections': 0,
                'emotion_counts': {label: 0 for label in self.EMOTION_LABELS}
            }

        emotion_counts = {label: 0 for label in self.EMOTION_LABELS}
        for result in self.emotion_history:
            emotion_counts[result.emotion] += 1

        return {
            'total_detections': len(self.emotion_history),
            'emotion_counts': emotion_counts,
            'most_common': max(emotion_counts.items(), key=lambda x: x[1])[0],
            'average_confidence': np.mean([r.confidence for r in self.emotion_history])
        }


# Global instance for easy access
_detector_instance: Optional[AdvancedEmotionDetector] = None


def get_emotion_detector() -> AdvancedEmotionDetector:
    """Get or create global emotion detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = AdvancedEmotionDetector()
    return _detector_instance


def detect_emotion_from_file(audio_path: str) -> Optional[EmotionResult]:
    """
    Convenience function to detect emotion from file

    Args:
        audio_path: Path to audio file

    Returns:
        EmotionResult or None
    """
    detector = get_emotion_detector()
    return detector.detect_from_file(audio_path)


def detect_emotion_from_audio(
    audio: np.ndarray,
    sample_rate: int = 16000
) -> Optional[EmotionResult]:
    """
    Convenience function to detect emotion from audio array

    Args:
        audio: Audio waveform
        sample_rate: Sample rate

    Returns:
        EmotionResult or None
    """
    detector = get_emotion_detector()
    return detector.detect_from_audio(audio, sample_rate)


# Integration with existing emotion detection
def enhance_basic_emotion(
    basic_emotion: str,
    audio_path: Optional[str] = None
) -> str:
    """
    Enhance basic emotion detection with advanced detection

    Args:
        basic_emotion: Basic emotion from existing system
        audio_path: Optional audio file for advanced detection

    Returns:
        Enhanced emotion (advanced if available, else basic)
    """
    detector = get_emotion_detector()

    if not detector.available or not audio_path:
        return basic_emotion

    result = detector.detect_from_file(audio_path)
    if result and result.confidence > 0.5:
        return result.emotion

    return basic_emotion


if __name__ == "__main__":
    # Demo/test mode
    import argparse

    parser = argparse.ArgumentParser(description="Advanced Emotion Detection Demo")
    parser.add_argument('audio_file', nargs='?', help='Audio file to analyze')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    detector = get_emotion_detector()

    if not detector.available:
        print("\n❌ Advanced emotion detection unavailable")
        print("Install dependencies:")
        print("  py -3.11 -m pip install transformers torch librosa")
        sys.exit(1)

    print(f"\n✅ Advanced Emotion Detector Ready")
    print(f"Device: {detector.device}")
    print(f"Model: {detector.model_name}")

    if args.audio_file:
        print(f"\n🎤 Analyzing: {args.audio_file}")
        result = detector.detect_from_file(args.audio_file)

        if result:
            print(f"\n📊 Results:")
            print(f"  Emotion: {result.emotion.upper()}")
            print(f"  Confidence: {result.confidence:.2%}")
            print(f"  Duration: {result.audio_duration:.2f}s")
            print(f"\n  All Scores:")
            for emotion, score in sorted(
                result.all_scores.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                bar = '█' * int(score * 50)
                print(f"    {emotion:10s} {score:.2%} {bar}")

    if args.stats and detector.emotion_history:
        stats = detector.get_stats()
        print(f"\n📈 Statistics:")
        print(f"  Total detections: {stats['total_detections']}")
        print(f"  Most common: {stats['most_common']}")
        print(f"  Avg confidence: {stats['average_confidence']:.2%}")
        print(f"\n  Emotion counts:")
        for emotion, count in stats['emotion_counts'].items():
            if count > 0:
                print(f"    {emotion:10s}: {count}")

    if not args.audio_file and not args.stats:
        print("\nUsage:")
        print("  py -3.11 omega_emotion_advanced.py audio.wav")
        print("  py -3.11 omega_emotion_advanced.py audio.wav --stats")
