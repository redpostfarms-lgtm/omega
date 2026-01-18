
# Type stubs for TTS (Coqui Text-to-Speech)
# NOTE: TTS doesn't support Python 3.14 yet
# This stub file suppresses import errors in VS Code

from typing import Any, Optional, List, Dict

class TTS:
    def __init__(self, model_name: str = ..., **kwargs: Any) -> None: ...
    def to(self, device: str) -> 'TTS': ...
    def tts_to_file(
        self,
        text: str,
        speaker_wav: Optional[str] = ...,
        language: Optional[str] = ...,
        file_path: Optional[str] = ...,
        **kwargs: Any
    ) -> None: ...
    def tts(self, text: str, **kwargs: Any) -> Any: ...
