"""
Pytest Configuration and Shared Fixtures
=========================================
Global fixtures for all tests
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_llm_client():
    """Mock LLM client (Ollama/LM Studio)"""
    mock = Mock()
    mock.chat = Mock(return_value={
        'message': {'content': 'Test response from LLM'}
    })
    mock.generate = Mock(return_value='Generated text')
    return mock


@pytest.fixture
def mock_claude_client():
    """Mock Claude API client"""
    mock = AsyncMock()
    mock.messages.create = AsyncMock(return_value=Mock(
        content=[Mock(text='Claude response')]
    ))
    return mock


@pytest.fixture
def mock_tts_model():
    """Mock TTS model"""
    mock = Mock()
    mock.tts_to_file = Mock()
    return mock


@pytest.fixture
def mock_speech_recognizer():
    """Mock speech recognition"""
    mock = Mock()
    mock.recognize_google = Mock(return_value="Test transcription")
    return mock


@pytest.fixture
def sample_audio_file(temp_dir):
    """Create sample audio file for testing"""
    import wave
    import numpy as np

    audio_path = temp_dir / "test_audio.wav"

    # Generate 1 second of silence
    sample_rate = 16000
    duration = 1.0
    samples = np.zeros(int(sample_rate * duration), dtype=np.int16)

    with wave.open(str(audio_path), 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())

    return audio_path


@pytest.fixture
def sample_json_data():
    """Sample JSON data for testing"""
    return {
        "test": "data",
        "nested": {
            "value": 123,
            "array": [1, 2, 3]
        },
        "timestamp": "2026-01-17T12:00:00"
    }


@pytest.fixture
def large_json_data():
    """Large JSON data for compression testing"""
    return {
        "large_array": [{"id": i, "data": "x" * 1000} for i in range(3000)]
    }


@pytest.fixture
def mock_prometheus_metrics():
    """Mock Prometheus metrics"""
    from unittest.mock import MagicMock

    mock_counter = MagicMock()
    mock_histogram = MagicMock()
    mock_gauge = MagicMock()

    return {
        'counter': mock_counter,
        'histogram': mock_histogram,
        'gauge': mock_gauge
    }


@pytest.fixture
def mock_file_integrity_checker():
    """Mock integrity checker"""
    mock = Mock()
    mock.register_file = Mock()
    mock.verify_file = Mock(return_value={'status': 'verified'})
    mock.verify_before_process = Mock(return_value=True)
    return mock


@pytest.fixture
def mock_notifier():
    """Mock notification system"""
    mock = Mock()
    mock.notify = Mock(return_value=True)
    mock.cleanup_started = Mock(return_value=True)
    mock.cleanup_completed = Mock(return_value=True)
    mock.disk_space_warning = Mock(return_value=True)
    return mock


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    # Reset any global state
    yield
    # Cleanup after test


@pytest.fixture
def mock_ollama_available():
    """Mock Ollama availability"""
    import sys
    from unittest.mock import MagicMock

    # Mock ollama module
    ollama_mock = MagicMock()
    ollama_mock.chat = MagicMock(return_value={
        'message': {'content': 'Test response'}
    })
    ollama_mock.list = MagicMock(return_value={
        'models': [{'name': 'llama3.2'}]
    })

    sys.modules['ollama'] = ollama_mock
    yield ollama_mock

    # Cleanup
    if 'ollama' in sys.modules:
        del sys.modules['ollama']


@pytest.fixture
def mock_system_metrics():
    """Mock system metrics (psutil)"""
    mock = Mock()
    mock.cpu_percent = Mock(return_value=45.5)
    mock.virtual_memory = Mock(return_value=Mock(
        percent=60.0,
        total=16000000000,
        available=6400000000
    ))
    mock.disk_usage = Mock(return_value=Mock(
        percent=75.0,
        total=500000000000,
        free=125000000000
    ))
    return mock


# Markers
def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "requires_gpu: marks tests that require GPU"
    )
    config.addinivalue_line(
        "markers", "requires_audio: marks tests that require audio devices"
    )
