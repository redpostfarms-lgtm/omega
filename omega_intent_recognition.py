#!/usr/bin/env python3
"""
Omega Intent Recognition
========================
Intent classification system to categorize user requests.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import numpy as np

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("[Intent Recognition] sentence-transformers not available. Install with: pip install sentence-transformers")

# Try to import scikit-learn
try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.linear_model import LogisticRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("[Intent Recognition] scikit-learn not available. Install with: pip install scikit-learn")

class IntentRecognizer:
    """Intent recognition system using embeddings"""
    
    def __init__(self, intent_file: Optional[Path] = None):
        self.base_dir = Path(__file__).parent.absolute()
        self.intent_file = intent_file or (self.base_dir / "intent_classes.json")
        self.embeddings_model = None
        self.intent_classes = {}
        self.intent_embeddings = {}
        self.classifier = None
        self.training_data = []
        
        # Initialize embeddings model
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("[Intent Recognition] Embeddings model initialized")
            except Exception as e:
                print(f"[Intent Recognition] Embeddings initialization failed: {e}")
        
        # Load intent classes
        self.load_intent_classes()
        
        # Train classifier if data available
        if self.intent_embeddings:
            self._train_classifier()
    
    def load_intent_classes(self):
        """Load intent class definitions"""
        if not self.intent_file.exists():
            # Create default intent classes
            self.intent_classes = {
                "query": {
                    "description": "Ask a question or request information",
                    "examples": ["what is", "tell me about", "explain", "how does"]
                },
                "command": {
                    "description": "Give a command or instruction",
                    "examples": ["do this", "run", "execute", "start", "stop"]
                },
                "greeting": {
                    "description": "Greeting or salutation",
                    "examples": ["hello", "hi", "hey", "good morning", "good evening"]
                },
                "farewell": {
                    "description": "Farewell or goodbye",
                    "examples": ["goodbye", "bye", "see you", "later", "farewell"]
                },
                "clarification": {
                    "description": "Request clarification or repeat",
                    "examples": ["what did you say", "repeat", "clarify", "what do you mean"]
                },
                "affirmation": {
                    "description": "Agree or confirm",
                    "examples": ["yes", "okay", "sure", "correct", "that's right"]
                },
                "negation": {
                    "description": "Disagree or deny",
                    "examples": ["no", "not", "wrong", "incorrect", "that's not right"]
                }
            }
            self.save_intent_classes()
        else:
            try:
                with open(self.intent_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.intent_classes = data.get("intents", {})
            except Exception as e:
                print(f"[Intent Recognition] Error loading intent classes: {e}")
                self.intent_classes = {}
        
        # Generate embeddings for intent classes
        if self.embeddings_model and self.intent_classes:
            self._generate_intent_embeddings()
    
    def save_intent_classes(self):
        """Save intent class definitions"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "intents": self.intent_classes
        }
        
        try:
            with open(self.intent_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Intent Recognition] Error saving intent classes: {e}")
    
    def _generate_intent_embeddings(self):
        """Generate embeddings for intent classes"""
        if not self.embeddings_model:
            return
        
        for intent_name, intent_data in self.intent_classes.items():
            # Use description and examples for embedding
            text = intent_data.get("description", "")
            examples = intent_data.get("examples", [])
            combined_text = f"{text} {' '.join(examples)}"
            
            try:
                embedding = self.embeddings_model.encode(combined_text)
                self.intent_embeddings[intent_name] = embedding
            except Exception as e:
                print(f"[Intent Recognition] Error generating embedding for {intent_name}: {e}")
    
    def _train_classifier(self):
        """Train intent classifier"""
        if not SKLEARN_AVAILABLE or not self.intent_embeddings:
            return
        
        # For now, use similarity-based classification
        # Could be enhanced with a trained classifier
        pass
    
    def recognize_intent(self, text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Recognize intent from text.
        
        Formula: intent = argmax(cosine_similarity(embedding(query), intent_embeddings))
        
        Args:
            text: Input text
            top_k: Number of top intents to return
            
        Returns:
            List of (intent_name, similarity_score) tuples
        """
        if not self.embeddings_model or not self.intent_embeddings:
            # Fallback: simple keyword matching
            return self._keyword_based_intent(text, top_k)
        
        try:
            # Generate embedding for input text
            query_embedding = self.embeddings_model.encode([text])
            
            # Calculate similarity to each intent
            similarities = {}
            for intent_name, intent_embedding in self.intent_embeddings.items():
                if SKLEARN_AVAILABLE:
                    similarity = cosine_similarity(query_embedding, [intent_embedding])[0][0]
                else:
                    # Manual cosine similarity
                    similarity = np.dot(query_embedding[0], intent_embedding) / (
                        np.linalg.norm(query_embedding[0]) * np.linalg.norm(intent_embedding)
                    )
                similarities[intent_name] = float(similarity)
            
            # Sort by similarity
            sorted_intents = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
            return sorted_intents[:top_k]
        except Exception as e:
            print(f"[Intent Recognition] Error recognizing intent: {e}")
            return self._keyword_based_intent(text, top_k)
    
    def _keyword_based_intent(self, text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Fallback keyword-based intent recognition"""
        text_lower = text.lower()
        scores = {}
        
        for intent_name, intent_data in self.intent_classes.items():
            examples = intent_data.get("examples", [])
            score = sum(1 for example in examples if example.lower() in text_lower)
            if score > 0:
                scores[intent_name] = score / len(examples) if examples else 0.0
        
        if not scores:
            return [("query", 0.5)]  # Default intent
        
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_intents[:top_k]

# Global intent recognizer instance
_intent_recognizer = None

def get_intent_recognizer() -> IntentRecognizer:
    """Get global intent recognizer instance"""
    global _intent_recognizer
    if _intent_recognizer is None:
        _intent_recognizer = IntentRecognizer()
    return _intent_recognizer

def recognize_intent(text: str, top_k: int = 3) -> List[Tuple[str, float]]:
    """Recognize intent from text"""
    return get_intent_recognizer().recognize_intent(text, top_k)

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" " * 25 + "OMEGA INTENT RECOGNITION")
    print("=" * 80)
    print()
    
    recognizer = IntentRecognizer()
    print("[OK] Intent recognition system initialized")
    print(f"  - Intent classes: {len(recognizer.intent_classes)}")
    print(f"  - Embeddings available: {EMBEDDINGS_AVAILABLE}")
    print(f"  - scikit-learn available: {SKLEARN_AVAILABLE}")
    print()
    print("Usage:")
    print("  from omega_intent_recognition import recognize_intent")
    print("  intents = recognize_intent('What is the weather?')")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
