"""
Tests for Advanced Emotion Detection
=====================================
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime


class TestAdvancedEmotionDetector:
    """Test advanced emotion detection functionality"""

    @pytest.fixture
    def mock_model(self):
        """Mock transformer model"""
        model = Mock()
        model.to = Mock(return_value=model)
        model.eval = Mock()

        # Mock model output
        logits = Mock()
        logits.cpu = Mock(return_value=logits)
        logits.numpy = Mock(return_value=np.array([[0.1, 0.6, 0.1, 0.1, 0.05, 0.03, 0.02]]))

        output = Mock()
        output.logits = logits
        model.return_value = output

        return model

    @pytest.fixture
    def mock_feature_extractor(self):
        """Mock feature extractor"""
        extractor = Mock()
        extractor.return_value = {
            'input_values': Mock(to=Mock(return_value=Mock()))
        }
        return extractor

    @patch('omega_emotion_advanced.DEPENDENCIES_AVAILABLE', True)
    @patch('omega_emotion_advanced.torch')
    @patch('omega_emotion_advanced.AutoModelForAudioClassification')
    @patch('omega_emotion_advanced.AutoFeatureExtractor')
    def test_detector_initialization(
        self,
        mock_extractor_class,
        mock_model_class,
        mock_torch,
        mock_feature_extractor,
        mock_model
    ):
        """Test detector initialization"""
        from omega_emotion_advanced import AdvancedEmotionDetector

        mock_torch.cuda.is_available.return_value = False
        mock_model_class.from_pretrained.return_value = mock_model
        mock_extractor_class.from_pretrained.return_value = mock_feature_extractor

        detector = AdvancedEmotionDetector()

        assert detector.available == True
        assert detector.device == "cpu"
        mock_model_class.from_pretrained.assert_called_once()

    @patch('omega_emotion_advanced.DEPENDENCIES_AVAILABLE', True)
    @patch('omega_emotion_advanced.torch')
    @patch('omega_emotion_advanced.librosa')
    @patch('omega_emotion_advanced.AutoModelForAudioClassification')
    @patch('omega_emotion_advanced.AutoFeatureExtractor')
    def test_detect_from_audio(
        self,
        mock_extractor_class,
        mock_model_class,
        mock_librosa,
        mock_torch,
    ):
        """Test emotion detection from audio array"""
        from omega_emotion_advanced import AdvancedEmotionDetector

        # Setup mocks
        mock_torch.cuda.is_available.return_value = False
        mock_torch.nn.functional.softmax = Mock(
            return_value=Mock(
                cpu=Mock(
                    return_value=Mock(
                        numpy=Mock(
                            return_value=np.array([[0.1, 0.6, 0.1, 0.1, 0.05, 0.03, 0.02]])
                        )
                    )
                )
            )
        )

        model = Mock()
        model.to = Mock(return_value=model)
        model.eval = Mock()
        model.return_value = Mock(logits=Mock())
        mock_model_class.from_pretrained.return_value = model

        extractor = Mock()
        extractor.return_value = {'input_values': Mock(to=Mock(return_value=Mock()))}
        mock_extractor_class.from_pretrained.return_value = extractor

        # Create detector
        detector = AdvancedEmotionDetector()

        # Test audio
        audio = np.random.randn(16000)  # 1 second of audio
        result = detector.detect_from_audio(audio, sample_rate=16000)

        assert result is not None
        assert result.emotion == 'happy'  # Index 1 has highest score (0.6)
        assert result.confidence > 0.5
        assert len(result.all_scores) == 7
        assert result.audio_duration > 0

    @patch('omega_emotion_advanced.DEPENDENCIES_AVAILABLE', True)
    @patch('omega_emotion_advanced.torch')
    @patch('omega_emotion_advanced.librosa')
    @patch('omega_emotion_advanced.AutoModelForAudioClassification')
    @patch('omega_emotion_advanced.AutoFeatureExtractor')
    def test_detect_from_file(
        self,
        mock_extractor_class,
        mock_model_class,
        mock_librosa,
        mock_torch,
        tmp_path
    ):
        """Test emotion detection from audio file"""
        from omega_emotion_advanced import AdvancedEmotionDetector

        # Setup mocks
        mock_torch.cuda.is_available.return_value = False
        mock_torch.nn.functional.softmax = Mock(
            return_value=Mock(
                cpu=Mock(
                    return_value=Mock(
                        numpy=Mock(
                            return_value=np.array([[0.1, 0.1, 0.7, 0.05, 0.03, 0.02, 0.1]])
                        )
                    )
                )
            )
        )

        model = Mock()
        model.to = Mock(return_value=model)
        model.eval = Mock()
        model.return_value = Mock(logits=Mock())
        mock_model_class.from_pretrained.return_value = model

        extractor = Mock()
        extractor.return_value = {'input_values': Mock(to=Mock(return_value=Mock()))}
        mock_extractor_class.from_pretrained.return_value = extractor

        # Mock librosa load
        mock_librosa.load.return_value = (np.random.randn(16000), 16000)

        # Create detector
        detector = AdvancedEmotionDetector()

        # Test file
        test_file = tmp_path / "test.wav"
        test_file.write_text("dummy")

        result = detector.detect_from_file(str(test_file))

        assert result is not None
        assert result.emotion == 'sad'  # Index 2 has highest score (0.7)
        assert result.confidence > 0.5

    @patch('omega_emotion_advanced.DEPENDENCIES_AVAILABLE', True)
    @patch('omega_emotion_advanced.torch')
    @patch('omega_emotion_advanced.AutoModelForAudioClassification')
    @patch('omega_emotion_advanced.AutoFeatureExtractor')
    def test_emotion_history(
        self,
        mock_extractor_class,
        mock_model_class,
        mock_torch
    ):
        """Test emotion history tracking"""
        from omega_emotion_advanced import AdvancedEmotionDetector, EmotionResult

        mock_torch.cuda.is_available.return_value = False

        model = Mock()
        model.to = Mock(return_value=model)
        model.eval = Mock()
        mock_model_class.from_pretrained.return_value = model

        extractor = Mock()
        mock_extractor_class.from_pretrained.return_value = extractor

        detector = AdvancedEmotionDetector()
        detector.max_history = 3

        # Add results manually
        for i, emotion in enumerate(['happy', 'sad', 'angry', 'happy']):
            result = EmotionResult(
                emotion=emotion,
                confidence=0.8,
                all_scores={label: 0.1 for label in detector.EMOTION_LABELS},
                timestamp=datetime.now(),
                audio_duration=1.0
            )
            detector._add_to_history(result)

        # Should keep only last 3
        assert len(detector.emotion_history) == 3
        assert detector.emotion_history[0].emotion == 'sad'
        assert detector.emotion_history[-1].emotion == 'happy'

    @patch('omega_emotion_advanced.DEPENDENCIES_AVAILABLE', True)
    @patch('omega_emotion_advanced.torch')
    @patch('omega_emotion_advanced.AutoModelForAudioClassification')
    @patch('omega_emotion_advanced.AutoFeatureExtractor')
    def test_emotion_trend(
        self,
        mock_extractor_class,
        mock_model_class,
        mock_torch
    ):
        """Test emotion trend calculation"""
        from omega_emotion_advanced import AdvancedEmotionDetector, EmotionResult

        mock_torch.cuda.is_available.return_value = False

        model = Mock()
        model.to = Mock(return_value=model)
        model.eval = Mock()
        mock_model_class.from_pretrained.return_value = model

        extractor = Mock()
        mock_extractor_class.from_pretrained.return_value = extractor

        detector = AdvancedEmotionDetector()

        # Add results with varying scores
        for i in range(5):
            result = EmotionResult(
                emotion='happy',
                confidence=0.8,
                all_scores={
                    'neutral': 0.1,
                    'happy': 0.6,
                    'sad': 0.1,
                    'angry': 0.1,
                    'fear': 0.05,
                    'disgust': 0.03,
                    'surprise': 0.02
                },
                timestamp=datetime.now(),
                audio_duration=1.0
            )
            detector._add_to_history(result)

        trend = detector.get_emotion_trend(window=5)

        assert 'happy' in trend
        assert trend['happy'] > 0.5  # Should be dominant
        assert sum(trend.values()) == pytest.approx(1.0, abs=0.01)

    @patch('omega_emotion_advanced.DEPENDENCIES_AVAILABLE', True)
    @patch('omega_emotion_advanced.torch')
    @patch('omega_emotion_advanced.AutoModelForAudioClassification')
    @patch('omega_emotion_advanced.AutoFeatureExtractor')
    def test_dominant_emotion(
        self,
        mock_extractor_class,
        mock_model_class,
        mock_torch
    ):
        """Test dominant emotion detection"""
        from omega_emotion_advanced import AdvancedEmotionDetector, EmotionResult

        mock_torch.cuda.is_available.return_value = False

        model = Mock()
        model.to = Mock(return_value=model)
        model.eval = Mock()
        mock_model_class.from_pretrained.return_value = model

        extractor = Mock()
        mock_extractor_class.from_pretrained.return_value = extractor

        detector = AdvancedEmotionDetector()

        # Add mostly angry emotions
        for emotion in ['angry', 'angry', 'angry', 'happy', 'sad']:
            result = EmotionResult(
                emotion=emotion,
                confidence=0.8,
                all_scores={label: 0.1 for label in detector.EMOTION_LABELS},
                timestamp=datetime.now(),
                audio_duration=1.0
            )
            detector._add_to_history(result)

        dominant = detector.get_dominant_emotion(window=5)
        assert dominant == 'angry'

    @patch('omega_emotion_advanced.DEPENDENCIES_AVAILABLE', True)
    @patch('omega_emotion_advanced.torch')
    @patch('omega_emotion_advanced.AutoModelForAudioClassification')
    @patch('omega_emotion_advanced.AutoFeatureExtractor')
    def test_statistics(
        self,
        mock_extractor_class,
        mock_model_class,
        mock_torch
    ):
        """Test statistics generation"""
        from omega_emotion_advanced import AdvancedEmotionDetector, EmotionResult

        mock_torch.cuda.is_available.return_value = False

        model = Mock()
        model.to = Mock(return_value=model)
        model.eval = Mock()
        mock_model_class.from_pretrained.return_value = model

        extractor = Mock()
        mock_extractor_class.from_pretrained.return_value = extractor

        detector = AdvancedEmotionDetector()

        # Add varied emotions
        emotions = ['happy', 'happy', 'sad', 'angry', 'happy']
        for emotion in emotions:
            result = EmotionResult(
                emotion=emotion,
                confidence=0.8,
                all_scores={label: 0.1 for label in detector.EMOTION_LABELS},
                timestamp=datetime.now(),
                audio_duration=1.0
            )
            detector._add_to_history(result)

        stats = detector.get_stats()

        assert stats['total_detections'] == 5
        assert stats['emotion_counts']['happy'] == 3
        assert stats['emotion_counts']['sad'] == 1
        assert stats['most_common'] == 'happy'
        assert stats['average_confidence'] == 0.8

    def test_fallback_when_unavailable(self):
        """Test fallback behavior when dependencies unavailable"""
        with patch('omega_emotion_advanced.DEPENDENCIES_AVAILABLE', False):
            from omega_emotion_advanced import AdvancedEmotionDetector

            detector = AdvancedEmotionDetector()

            assert detector.available == False

            # Should return neutral fallback
            result = detector.detect_from_audio(np.random.randn(16000))
            assert result.emotion == 'neutral'
            assert result.confidence == 0.0

    @patch('omega_emotion_advanced.DEPENDENCIES_AVAILABLE', True)
    @patch('omega_emotion_advanced.torch')
    @patch('omega_emotion_advanced.AutoModelForAudioClassification')
    @patch('omega_emotion_advanced.AutoFeatureExtractor')
    def test_save_history(
        self,
        mock_extractor_class,
        mock_model_class,
        mock_torch,
        tmp_path
    ):
        """Test saving emotion history to file"""
        from omega_emotion_advanced import AdvancedEmotionDetector, EmotionResult

        mock_torch.cuda.is_available.return_value = False

        model = Mock()
        model.to = Mock(return_value=model)
        model.eval = Mock()
        mock_model_class.from_pretrained.return_value = model

        extractor = Mock()
        mock_extractor_class.from_pretrained.return_value = extractor

        detector = AdvancedEmotionDetector()

        # Add some results
        for emotion in ['happy', 'sad']:
            result = EmotionResult(
                emotion=emotion,
                confidence=0.8,
                all_scores={label: 0.1 for label in detector.EMOTION_LABELS},
                timestamp=datetime.now(),
                audio_duration=1.0
            )
            detector._add_to_history(result)

        # Save history
        output_file = tmp_path / "emotion_history.json"
        detector.save_history(str(output_file))

        assert output_file.exists()

        # Verify content
        import json
        with open(output_file) as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]['emotion'] == 'happy'
        assert data[1]['emotion'] == 'sad'


class TestGlobalInstance:
    """Test global instance management"""

    def test_get_emotion_detector_singleton(self):
        """Test that get_emotion_detector returns singleton"""
        from omega_emotion_advanced import get_emotion_detector

        detector1 = get_emotion_detector()
        detector2 = get_emotion_detector()

        assert detector1 is detector2


class TestConvenienceFunctions:
    """Test convenience wrapper functions"""

    @patch('omega_emotion_advanced.get_emotion_detector')
    def test_detect_emotion_from_file(self, mock_get_detector):
        """Test convenience function for file detection"""
        from omega_emotion_advanced import detect_emotion_from_file, EmotionResult

        mock_detector = Mock()
        mock_result = EmotionResult(
            emotion='happy',
            confidence=0.9,
            all_scores={},
            timestamp=datetime.now(),
            audio_duration=1.0
        )
        mock_detector.detect_from_file.return_value = mock_result
        mock_get_detector.return_value = mock_detector

        result = detect_emotion_from_file("test.wav")

        assert result.emotion == 'happy'
        mock_detector.detect_from_file.assert_called_once_with("test.wav")

    @patch('omega_emotion_advanced.get_emotion_detector')
    def test_detect_emotion_from_audio(self, mock_get_detector):
        """Test convenience function for audio array detection"""
        from omega_emotion_advanced import detect_emotion_from_audio, EmotionResult

        mock_detector = Mock()
        mock_result = EmotionResult(
            emotion='sad',
            confidence=0.85,
            all_scores={},
            timestamp=datetime.now(),
            audio_duration=1.0
        )
        mock_detector.detect_from_audio.return_value = mock_result
        mock_get_detector.return_value = mock_detector

        audio = np.random.randn(16000)
        result = detect_emotion_from_audio(audio)

        assert result.emotion == 'sad'
        mock_detector.detect_from_audio.assert_called_once()

    @patch('omega_emotion_advanced.get_emotion_detector')
    def test_enhance_basic_emotion(self, mock_get_detector):
        """Test enhancing basic emotion with advanced detection"""
        from omega_emotion_advanced import enhance_basic_emotion, EmotionResult

        mock_detector = Mock()
        mock_detector.available = True
        mock_result = EmotionResult(
            emotion='angry',
            confidence=0.9,
            all_scores={},
            timestamp=datetime.now(),
            audio_duration=1.0
        )
        mock_detector.detect_from_file.return_value = mock_result
        mock_get_detector.return_value = mock_detector

        # Should use advanced detection (high confidence)
        result = enhance_basic_emotion('neutral', 'audio.wav')
        assert result == 'angry'

        # Should fallback to basic if low confidence
        mock_result.confidence = 0.3
        result = enhance_basic_emotion('neutral', 'audio.wav')
        assert result == 'neutral'

        # Should fallback if no audio path
        result = enhance_basic_emotion('happy', None)
        assert result == 'happy'
