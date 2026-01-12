"""
Agent Streaming System
Enables real-time streaming output from agents.

Red Post Farms, LLC - 2026
"""

import sys
import time
from typing import Iterator, Optional, Callable

class AgentStreaming:
    def __init__(self):
        self.streaming_enabled = True
    
    def stream_response(self, generator: Iterator[str], callback: Optional[Callable[[str], None]] = None):
        """Stream agent response in real-time."""
        if not self.streaming_enabled:
            return ''.join(generator)
        
        result = []
        for chunk in generator:
            result.append(chunk)
            if callback:
                callback(chunk)
            else:
                sys.stdout.write(chunk)
                sys.stdout.flush()
        return ''.join(result)
    
    def enable_streaming(self, enabled: bool = True):
        """Enable or disable streaming."""
        self.streaming_enabled = enabled
    
    def stream_with_progress(self, generator: Iterator[str], total: Optional[int] = None):
        """Stream with progress indicator."""
        result = []
        count = 0
        for chunk in generator:
            result.append(chunk)
            count += len(chunk)
            if total:
                progress = (count / total) * 100
                sys.stdout.write(f"\rProgress: {progress:.1f}%")
                sys.stdout.flush()
            else:
                sys.stdout.write(chunk)
                sys.stdout.flush()
        if total:
            sys.stdout.write("\n")
        return ''.join(result)

def create_streaming_generator(text: str, chunk_size: int = 10) -> Iterator[str]:
    """Create a generator that yields text in chunks."""
    for i in range(0, len(text), chunk_size):
        yield text[i:i+chunk_size]
        time.sleep(0.01)  # Small delay for streaming effect

if __name__ == "__main__":
    streamer = AgentStreaming()
    test_text = "This is a test of the streaming system. " * 10
    print("Streaming test:")
    streamer.stream_response(create_streaming_generator(test_text))

