"""
Omega Context Summarization
============================
Context summarization for managing long conversations.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
import json
from datetime import datetime

try:
    from langchain.memory import ConversationSummaryMemory
    from langchain.llms.base import LLM
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("[Context Summarization] LangChain not available. Install with: pip install langchain")

class ContextSummarizer:
    """Context summarization for long conversations"""
    
    def __init__(self, max_turns: int = 10, summary_file: Optional[Path] = None):
        self.base_dir = Path(__file__).parent.absolute()
        self.max_turns = max_turns
        self.summary_file = summary_file or (self.base_dir / "conversation_summaries.json")
        self.memory = None
        
        if LANGCHAIN_AVAILABLE:
            try:
                self.memory = ConversationSummaryMemory(
                    llm=None,  # We'll use simple summarization for now
                    memory_key="chat_history",
                    return_messages=True,
                    max_token_limit=2000
                )
                print("[Context Summarization] LangChain memory initialized")
            except Exception as e:
                print(f"[Context Summarization] LangChain initialization failed: {e}")
    
    def summarize_context(self, conversation_turns: List[Dict[str, str]], 
                         max_length: int = 200) -> str:
        """
        Summarize conversation context.
        
        Args:
            conversation_turns: List of {"user": text, "assistant": text} dicts
            max_length: Maximum summary length in characters
            
        Returns:
            Summarized context string
        """
        if not conversation_turns:
            return ""
        
        if len(conversation_turns) <= 2:
            summary_parts = []
            for turn in conversation_turns:
                if turn.get("user"):
                    summary_parts.append(f"User: {turn['user']}")
                if turn.get("assistant"):
                    summary_parts.append(f"Assistant: {turn['assistant']}")
            return " ".join(summary_parts)
        
        summary_parts = []
        
        first_turn = conversation_turns[0]
        if first_turn.get("user"):
            summary_parts.append(f"User started: {first_turn['user'][:100]}")
        
        if len(conversation_turns) > 4:
            step = len(conversation_turns) // 3
            for i in range(step, len(conversation_turns) - step, step):
                turn = conversation_turns[i]
                if turn.get("user"):
                    summary_parts.append(f"User: {turn['user'][:50]}...")
        
        last_turn = conversation_turns[-1]
        if last_turn.get("user"):
            summary_parts.append(f"User recently: {last_turn['user'][:100]}")
        
        summary = " | ".join(summary_parts)
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    def truncate_context(self, conversation_turns: List[Dict[str, str]], 
                        max_turns: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Truncate conversation context to max_turns.
        
        Args:
            conversation_turns: List of conversation turns
            max_turns: Maximum number of turns (defaults to self.max_turns)
            
        Returns:
            Truncated conversation turns
        """
        max_turns = max_turns or self.max_turns
        
        if len(conversation_turns) <= max_turns:
            return conversation_turns
        
        truncated = [conversation_turns[0]] + conversation_turns[-(max_turns - 1):]
        return truncated
    
    def summarize_and_truncate(self, conversation_turns: List[Dict[str, str]]) -> tuple:
        """
        Summarize and truncate conversation context.
        
        Args:
            conversation_turns: List of conversation turns
            
        Returns:
            Tuple of (summary, truncated_turns)
        """
        if len(conversation_turns) <= self.max_turns:
            return "", conversation_turns
        
        older_turns = conversation_turns[:-self.max_turns]
        summary = self.summarize_context(older_turns)
        
        recent_turns = conversation_turns[-self.max_turns:]
        
        return summary, recent_turns

_context_summarizer = None

def get_context_summarizer(max_turns: int = 10) -> ContextSummarizer:
    """Get global context summarizer instance"""
    global _context_summarizer
    if _context_summarizer is None:
        _context_summarizer = ContextSummarizer(max_turns=max_turns)
    return _context_summarizer

def summarize_context(conversation_turns: List[Dict[str, str]], 
                     max_length: int = 200) -> str:
    """Summarize conversation context"""
    return get_context_summarizer().summarize_context(conversation_turns, max_length)

def truncate_context(conversation_turns: List[Dict[str, str]], 
                    max_turns: int = 10) -> List[Dict[str, str]]:
    """Truncate conversation context"""
    return get_context_summarizer().truncate_context(conversation_turns, max_turns)

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" " * 20 + "OMEGA CONTEXT SUMMARIZATION")
    print("=" * 80)
    print()
    
    summarizer = ContextSummarizer()
    print("[OK] Context summarization system initialized")
    print(f"  - Max turns: {summarizer.max_turns}")
    print(f"  - LangChain available: {LANGCHAIN_AVAILABLE}")
    print()
    print("Usage:")
    print("  from omega_context_summarization import summarize_context, truncate_context")
    print("  summary = summarize_context(conversation_turns)")
    print("  truncated = truncate_context(conversation_turns)")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
