# -*- coding: utf-8 -*-
# AGENT CHATBOT SYSTEM - Unified Agent + Prompt + Lock-On Tracking
# Combines: agent_forge (prompts), agent_anonymous (execution), conversational lock-on

import os
import json
import sys
import io
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict

# Import our systems
from agent_forge import forge_system_prompt, generate_agent_prompt, AGENT_TEMPLATES
from agent_anonymous import Agent, AgentConfig

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


@dataclass
class ConversationVector:
    """Represents conversation intent/tracking state."""
    intent: str
    context: str
    goal_active: bool
    goal_text: Optional[str] = None
    last_update: str = None
    
    def __post_init__(self):
        if self.last_update is None:
            self.last_update = str(datetime.now())


class ConversationalLockOn:
    """
    Missile-grade conversational tracking system.
    Maintains conversation vectors, detects drift, recalibrates naturally.
    """
    
    def __init__(self, deviation_threshold: float = 0.20):
        """
        Initialize lock-on system.
        
        Args:
            deviation_threshold: Percentage change before recalibration (default 20%)
        """
        self.deviation_threshold = deviation_threshold
        self.current_vector: Optional[ConversationVector] = None
        self.history: List[ConversationVector] = []
        self.goal_lock: bool = False
        self.goal_text: Optional[str] = None
    
    def detect_goal_explicit(self, user_message: str) -> bool:
        """
        Detect if user explicitly sets a goal.
        
        Goal triggers: "let's finish this", "remember my plan", "track this goal",
        "help me complete", "finish this task", etc.
        """
        goal_keywords = [
            "let's finish", "remember my plan", "track this goal",
            "help me complete", "finish this task", "complete this",
            "work on this goal", "achieve this", "accomplish this",
            "focus on", "lock onto", "target this"
        ]
        
        user_lower = user_message.lower()
        for keyword in goal_keywords:
            if keyword in user_lower:
                # Extract goal text if present
                if "goal" in user_lower or "plan" in user_lower or "task" in user_lower:
                    # Try to extract what comes after keyword
                    idx = user_lower.find(keyword)
                    if idx != -1:
                        after = user_message[idx:].strip()
                        if len(after) > len(keyword) + 10:  # Has actual goal text
                            self.goal_text = after
                return True
        return False
    
    def compute_delta(self, new_intent: str) -> float:
        """
        Compute deviation percentage from current vector.
        Simple word overlap calculation (can be enhanced with embeddings).
        """
        if self.current_vector is None:
            return 1.0  # 100% change = new conversation
        
        old_words = set(self.current_vector.intent.lower().split())
        new_words = set(new_intent.lower().split())
        
        if len(old_words) == 0:
            return 1.0
        
        intersection = len(old_words & new_words)
        union = len(old_words | new_words)
        
        if union == 0:
            return 1.0
        
        similarity = intersection / union
        delta = 1.0 - similarity
        
        return delta
    
    def update_vector(self, user_message: str) -> Tuple[bool, Optional[str]]:
        """
        Update conversation vector and detect if recalibration needed.
        
        Returns:
            Tuple of (recalibration_needed, recalibration_message)
        """
        # Check for explicit goal setting
        goal_detected = self.detect_goal_explicit(user_message)
        
        if goal_detected:
            self.goal_lock = True
            if not self.goal_text:
                # Extract goal from message context
                self.goal_text = user_message
        
        # Compute intent (simplified - extract key nouns/verbs)
        intent = self._extract_intent(user_message)
        
        # Compute delta
        delta = self.compute_delta(intent)
        
        # Create new vector
        new_vector = ConversationVector(
            intent=intent,
            context=user_message[:100],  # First 100 chars for context
            goal_active=self.goal_lock,
            goal_text=self.goal_text if self.goal_lock else None
        )
        
        recalibration_needed = False
        recalibration_msg = None
        
        # Check if recalibration needed
        if delta > self.deviation_threshold and self.goal_lock:
            recalibration_needed = True
            goal_ref = self.goal_text or "your original goal"
            
            # Natural recalibration phrases
            recalibration_options = [
                f"Still tracking {goal_ref} here—should we pivot or finish that first?",
                f"Right where we left off: {goal_ref}. Want to continue or switch tracks?",
                f"Locked onto {goal_ref}. This new direction—is it related or should I hold the original target?",
                f"Back on your trail: {goal_ref}. Still on this, or adapting?"
            ]
            
            # Simple rotation (could be smarter)
            recalibration_msg = recalibration_options[len(self.history) % len(recalibration_options)]
        
        # Update current vector
        self.current_vector = new_vector
        self.history.append(new_vector)
        
        # Keep history manageable
        if len(self.history) > 50:
            self.history = self.history[-50:]
        
        return recalibration_needed, recalibration_msg
    
    def _extract_intent(self, message: str) -> str:
        """
        Extract key intent from message (simplified).
        In production, use NLP/embeddings for better extraction.
        """
        # Remove stopwords, get key terms
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
        words = message.lower().split()
        key_words = [w for w in words if w not in stopwords and len(w) > 2]
        return ' '.join(key_words[:10])  # Top 10 key words
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current lock-on state for logging/debugging."""
        if self.current_vector is None:
            return {"status": "no_target", "goal_lock": False}
        
        return {
            "status": "locked_on" if self.goal_lock else "conversational",
            "goal_lock": self.goal_lock,
            "goal_text": self.goal_text,
            "current_intent": self.current_vector.intent,
            "context": self.current_vector.context
        }


class AgentChatbot:
    """
    Unified chatbot that combines:
    - Battle-tested system prompts (from agent_forge)
    - Anonymous agent execution (from agent_anonymous)
    - Conversational lock-on tracking
    - Self-improvement via skill logs
    """
    
    def __init__(
        self,
        agent_template: str = "elara",
        creator_name: str = "Anonymous",
        config: Optional[AgentConfig] = None
    ):
        """
        Initialize chatbot.
        
        Args:
            agent_template: Template name from AGENT_TEMPLATES
            creator_name: Creator name for sign-offs
            config: AgentConfig for execution tasks
        """
        self.agent_template = agent_template
        self.creator_name = creator_name
        
        # Generate system prompt
        self.system_prompt = generate_agent_prompt(agent_template, creator_name)
        
        # Initialize anonymous agent for task execution
        self.agent = Agent("chatbot assistant", config or AgentConfig())
        
        # Initialize lock-on system
        self.lock_on = ConversationalLockOn()
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        
        # Skill improvement tracking
        self.improvement_log = Path(self.agent.config.skills_dir) / f"{self.agent.name}_chatbot.json"
        self._init_improvement_log()
    
    def _init_improvement_log(self):
        """Initialize improvement log for self-learning."""
        if not self.improvement_log.exists():
            improvement_data = {
                "created": str(datetime.now()),
                "template": self.agent_template,
                "total_interactions": 0,
                "successful_responses": 0,
                "failed_responses": 0,
                "improvement_notes": [],
                "lock_on_stats": {
                    "recalibrations": 0,
                    "goal_locks": 0
                }
            }
            with open(self.improvement_log, 'w', encoding='utf-8') as f:
                json.dump(improvement_data, f, indent=2)
    
    def _log_interaction(self, user_input: str, response: str, success: bool, recalibrated: bool = False):
        """Log interaction for self-improvement."""
        # Load existing data
        if self.improvement_log.exists():
            with open(self.improvement_log, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                "created": str(datetime.now()),
                "template": self.agent_template,
                "total_interactions": 0,
                "successful_responses": 0,
                "failed_responses": 0,
                "improvement_notes": [],
                "lock_on_stats": {
                    "recalibrations": 0,
                    "goal_locks": 0
                }
            }
        
        data['total_interactions'] += 1
        
        if success:
            data['successful_responses'] += 1
        else:
            data['failed_responses'] += 1
        
        if recalibrated:
            data['lock_on_stats']['recalibrations'] += 1
        
        if self.lock_on.goal_lock:
            data['lock_on_stats']['goal_locks'] = data['lock_on_stats'].get('goal_locks', 0) + 1
        
        # Add improvement note
        note = {
            "timestamp": str(datetime.now()),
            "user_input": user_input[:200],
            "response_length": len(response),
            "success": success,
            "recalibrated": recalibrated,
            "lock_state": self.lock_on.get_current_state()
        }
        data['improvement_notes'].append(note)
        
        # Keep last 100 notes
        if len(data['improvement_notes']) > 100:
            data['improvement_notes'] = data['improvement_notes'][-100:]
        
        # Write back
        with open(self.improvement_log, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def chat(self, user_message: str) -> str:
        """
        Main chat function with lock-on tracking.
        
        Args:
            user_message: User's message
            
        Returns:
            Bot response
        """
        # Update lock-on system
        recalibrate, recalibration_msg = self.lock_on.update_vector(user_message)
        
        # Build response context
        context_parts = []
        
        # Add recalibration if needed
        if recalibrate and recalibration_msg:
            context_parts.append(f"[Lock-On Recalibration: {recalibration_msg}]")
        
        # Add goal context if locked
        if self.lock_on.goal_lock and self.lock_on.goal_text:
            context_parts.append(f"[Active Goal: {self.lock_on.goal_text}]")
        
        # Build full context
        context = "\n".join(context_parts) if context_parts else ""
        
        # Store in history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": str(datetime.now()),
            "lock_state": self.lock_on.get_current_state()
        })
        
        # Generate response (simplified - in production, call LLM API)
        # For now, return a template-based response
        response = self._generate_response(user_message, context)
        
        # Store response
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": str(datetime.now())
        })
        
        # Log for improvement
        self._log_interaction(user_message, response, success=True, recalibrated=recalibrate)
        
        return response
    
    def _generate_response(self, user_message: str, context: str) -> str:
        """
        Generate response (placeholder - integrate with actual LLM).
        
        In production, this would:
        1. Call LLM API (OpenAI, Anthropic, local model, etc.)
        2. Include system_prompt + conversation_history + context
        3. Return LLM response
        """
        # Placeholder response showing system is working
        template_name = AGENT_TEMPLATES.get(self.agent_template, {}).get('agent_name', 'Assistant')
        
        response_parts = []
        
        if context:
            response_parts.append(context)
        
        # Simple template response (replace with actual LLM call)
        response_parts.append(f"[{template_name}] I understand: {user_message[:100]}")
        
        if self.lock_on.goal_lock:
            response_parts.append(f"Locked onto goal: {self.lock_on.goal_text or 'your objective'}")
        
        response_parts.append(f"\n— {self.creator_name}, conversation tracked, response generated")
        
        return "\n".join(response_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chatbot statistics."""
        improvement_data = {}
        if self.improvement_log.exists():
            with open(self.improvement_log, 'r', encoding='utf-8') as f:
                improvement_data = json.load(f)
        
        total = improvement_data.get('total_interactions', 0)
        successful = improvement_data.get('successful_responses', 0)
        
        return {
            "agent_name": self.agent.name,
            "template": self.agent_template,
            "total_interactions": total,
            "success_rate": (successful / max(total, 1) * 100) if total > 0 else 0,
            "lock_on_state": self.lock_on.get_current_state(),
            "conversation_length": len(self.conversation_history)
        }


# Example usage and testing
if __name__ == '__main__':
    print("=" * 60)
    print("AGENT CHATBOT SYSTEM - Unified Agent + Lock-On")
    print("=" * 60)
    print()
    
    # Create chatbot with Elara template
    chatbot = AgentChatbot(
        agent_template="elara",
        creator_name="Wiley",
        config=AgentConfig(verbose=True)
    )
    
    print(f"🤖 Chatbot initialized: {chatbot.agent.name}")
    print(f"📋 Template: {chatbot.agent_template}")
    print(f"🎯 System prompt loaded: {len(chatbot.system_prompt)} characters")
    print()
    
    # Simulate conversation
    test_messages = [
        "Hey, I need help organizing my workspace",
        "Actually, can you help me book a flight instead?",
        "Wait, let's finish organizing first - remember my plan",
        "So organize the files into folders"
    ]
    
    print("Testing conversational lock-on...")
    print("-" * 60)
    
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        response = chatbot.chat(msg)
        print(f"🤖 Bot: {response[:200]}...")
        
        lock_state = chatbot.lock_on.get_current_state()
        if lock_state.get('goal_lock'):
            print(f"   🔒 Lock-On: ACTIVE - Goal: {lock_state.get('goal_text', 'N/A')}")
        else:
            print(f"   🔓 Lock-On: STEALTH MODE")
    
    print()
    print("-" * 60)
    print("\n📊 Statistics:")
    stats = chatbot.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print()
    print(f"✅ Chatbot ready. Improvement log: {chatbot.improvement_log}")

