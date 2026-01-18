"""
Tests for Local LLM Integration
================================
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from omega_local_llm import (
    LocalLLM,
    OmegaBrainLLM,
    LLMConfig
)


class TestLocalLLM:
    """Test local LLM functionality"""

    @patch('omega_local_llm.ollama')
    def test_ollama_initialization(self, mock_ollama):
        """Test Ollama initialization"""
        mock_ollama.chat = Mock()

        config = LLMConfig(backend="ollama", model="llama3.2")
        llm = LocalLLM(config)

        assert llm.available == True
        assert llm.config.backend == "ollama"

    @patch('omega_local_llm.ollama')
    def test_text_generation(self, mock_ollama):
        """Test text generation"""
        mock_ollama.chat = Mock(return_value={
            'message': {'content': 'Generated response'}
        })

        config = LLMConfig(backend="ollama")
        llm = LocalLLM(config)

        response = llm.generate("Test prompt")

        assert response == 'Generated response'
        mock_ollama.chat.assert_called_once()

    @patch('omega_local_llm.ollama')
    def test_system_prompt(self, mock_ollama):
        """Test system prompt inclusion"""
        mock_ollama.chat = Mock(return_value={
            'message': {'content': 'Response'}
        })

        llm = LocalLLM(LLMConfig(backend="ollama"))
        llm.generate("User prompt", system_prompt="You are helpful")

        call_args = mock_ollama.chat.call_args
        messages = call_args[1]['messages']

        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'

    def test_llm_unavailable_fallback(self):
        """Test fallback when LLM unavailable"""
        config = LLMConfig(backend="invalid_backend")
        llm = LocalLLM(config)

        assert llm.available == False

        response = llm.generate("Test")
        assert "unavailable" in response.lower()


class TestOmegaBrainLLM:
    """Test Omega Brain LLM integration"""

    @patch('omega_local_llm.LocalLLM')
    def test_conversation_history(self, mock_llm_class):
        """Test conversation history tracking"""
        mock_llm = Mock()
        mock_llm.available = True
        mock_llm.generate = Mock(return_value="Response")
        mock_llm_class.return_value = mock_llm

        brain = OmegaBrainLLM()
        brain.llm = mock_llm

        brain.process_voice_input("First message", "neutral")
        brain.process_voice_input("Second message", "happy")

        assert len(brain.conversation_history) == 2
        assert brain.conversation_history[0]['user'] == "First message"
        assert brain.conversation_history[1]['emotion'] == "happy"

    @patch('omega_local_llm.LocalLLM')
    def test_emotion_aware_prompts(self, mock_llm_class):
        """Test emotion-aware system prompts"""
        mock_llm = Mock()
        mock_llm.available = True
        mock_llm.generate = Mock(return_value="Response")
        mock_llm_class.return_value = mock_llm

        brain = OmegaBrainLLM()
        brain.llm = mock_llm

        brain.process_voice_input("Test", "sad")

        # Check that generate was called with emotion-aware prompt
        call_args = mock_llm.generate.call_args
        system_prompt = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('system_prompt', '')

        assert 'sad' in system_prompt.lower() or 'empathy' in system_prompt.lower()

    @patch('omega_local_llm.LocalLLM')
    def test_history_limit(self, mock_llm_class):
        """Test conversation history limit"""
        mock_llm = Mock()
        mock_llm.available = True
        mock_llm.generate = Mock(return_value="Response")
        mock_llm_class.return_value = mock_llm

        brain = OmegaBrainLLM()
        brain.llm = mock_llm
        brain.max_history = 3

        # Add more messages than limit
        for i in range(5):
            brain.process_voice_input(f"Message {i}", "neutral")

        assert len(brain.conversation_history) == 3
        assert brain.conversation_history[0]['user'] == "Message 2"

    @patch('omega_local_llm.LocalLLM')
    def test_clear_history(self, mock_llm_class):
        """Test clearing conversation history"""
        mock_llm = Mock()
        mock_llm.available = True
        mock_llm.generate = Mock(return_value="Response")
        mock_llm_class.return_value = mock_llm

        brain = OmegaBrainLLM()
        brain.llm = mock_llm

        brain.process_voice_input("Test", "neutral")
        assert len(brain.conversation_history) == 1

        brain.clear_history()
        assert len(brain.conversation_history) == 0

    @pytest.mark.asyncio
    async def test_async_generation(self, mock_llm_client):
        """Test async LLM generation"""
        from omega_local_llm import omega_llm_response

        with patch('omega_local_llm.get_brain_llm') as mock_get_brain:
            mock_brain = Mock()
            mock_brain.process_voice_input = Mock(return_value="Async response")
            mock_get_brain.return_value = mock_brain

            response = await omega_llm_response("Test", "neutral")

            assert response == "Async response"
