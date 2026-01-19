"""
Omega LangChain Integration
============================
Integrates LangChain for better context management, memory, and chain of thought reasoning.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

try:
    from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
    from langchain.chains import ConversationChain
    from langchain.llms.base import LLM
    from langchain.schema import BaseMessage, HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("[LangChain] LangChain not available. Install with: pip install langchain")

class OmegaLangChainIntegration:
    """LangChain integration for Omega"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.memory = None
        self.chain = None
        self.initialized = False
        
    def initialize(self):
        """Initialize LangChain integration"""
        if not LANGCHAIN_AVAILABLE:
            print("[LangChain] LangChain not available, using simple memory fallback")
            return False
        
        try:
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Note: We'll use a simple prompt template since we don't have an LLM
            self.initialized = True
            print("[LangChain] LangChain integration initialized")
            return True
        except Exception as e:
            print(f"[LangChain] Initialization error: {e}")
            return False
    
    def add_to_memory(self, human_input: str, ai_output: str):
        """Add conversation turn to memory"""
        if not self.initialized or not self.memory:
            return
        
        try:
            self.memory.chat_memory.add_user_message(human_input)
            self.memory.chat_memory.add_ai_message(ai_output)
        except Exception as e:
            print(f"[LangChain] Error adding to memory: {e}")
    
    def get_conversation_context(self, max_turns: int = 5) -> List[Dict[str, str]]:
        """Get conversation context from memory"""
        if not self.initialized or not self.memory:
            return []
        
        try:
            messages = self.memory.chat_memory.messages
            context = []
            
            for i in range(max(0, len(messages) - max_turns * 2), len(messages), 2):
                if i + 1 < len(messages):
                    context.append({
                        "human": messages[i].content if hasattr(messages[i], 'content') else str(messages[i]),
                        "ai": messages[i+1].content if hasattr(messages[i+1], 'content') else str(messages[i+1])
                    })
            
            return context
        except Exception as e:
            print(f"[LangChain] Error getting context: {e}")
            return []
    
    def get_context_for_whisper(self, max_words: int = 100) -> Optional[str]:
        """Get conversation context formatted for Whisper initial_prompt"""
        context = self.get_conversation_context()
        if not context:
            return None
        
        context_text = []
        for turn in context:
            context_text.append(turn.get("human", ""))
            context_text.append(turn.get("ai", ""))
        
        full_text = ' '.join(context_text)
        words = full_text.split()
        
        if len(words) > max_words:
            words = words[-max_words:]
        
        return ' '.join(words)
    
    def clear_memory(self):
        """Clear conversation memory"""
        if self.memory:
            try:
                self.memory.clear()
                print("[LangChain] Memory cleared")
            except Exception as e:
                print(f"[LangChain] Error clearing memory: {e}")
    
    def save_memory(self, file_path: Path):
        """Save memory to file"""
        context = self.get_conversation_context(max_turns=100)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2)
    
    def load_memory(self, file_path: Path):
        """Load memory from file"""
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                context = json.load(f)
            
            for turn in context:
                self.add_to_memory(
                    turn.get("human", ""),
                    turn.get("ai", "")
                )
        except Exception as e:
            print(f"[LangChain] Error loading memory: {e}")

def get_langchain_integration() -> OmegaLangChainIntegration:
    """Get global LangChain integration instance"""
    if not hasattr(get_langchain_integration, '_instance'):
        get_langchain_integration._instance = OmegaLangChainIntegration()
        get_langchain_integration._instance.initialize()
    return get_langchain_integration._instance

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" " * 20 + "OMEGA LANGCHAIN INTEGRATION")
    print("=" * 80)
    print()
    
    integration = OmegaLangChainIntegration()
    if integration.initialize():
        print("[OK] LangChain integration initialized")
        print("  - Conversation memory enabled")
        print("  - Context management ready")
        print("  - Whisper context formatting ready")
    else:
        print("[INFO] LangChain not available, using fallback")
        print("  Install with: pip install langchain")
    
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
