#!/usr/bin/env python3
# Language Improver - Continuously improves Omega's language quality based on conversations
import json
from pathlib import Path
from datetime import datetime

IMPROVEMENT_LOG = Path('language_improvements.json')

class LanguageImprover:
    def __init__(self):
        self.improvements = self.load_improvements()
        self.current_quality_level = len(self.improvements)
    
    def load_improvements(self):
        """Load improvement history."""
        if IMPROVEMENT_LOG.exists():
            try:
                with open(IMPROVEMENT_LOG, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_improvements(self):
        """Save improvement history."""
        with open(IMPROVEMENT_LOG, 'w') as f:
            json.dump(self.improvements, f, indent=2)
    
    def analyze_conversation_quality(self, conversation_history):
        """Analyze conversation quality and identify improvement areas."""
        if len(conversation_history) < 2:
            return None
        
        # Analyze response patterns
        omega_responses = [msg[1] for msg in conversation_history if msg[0] == 'omega']
        
        improvements = {
            'response_length': self._analyze_response_length(omega_responses),
            'vocabulary_richness': self._analyze_vocabulary(omega_responses),
            'engagement_level': self._analyze_engagement(omega_responses),
            'conversation_flow': self._analyze_flow(conversation_history),
        }
        
        return improvements
    
    def _analyze_response_length(self, responses):
        """Analyze if responses are appropriate length."""
        avg_length = sum(len(r.split()) for r in responses) / len(responses) if responses else 0
        return {
            'average_words': avg_length,
            'recommendation': 'longer' if avg_length < 15 else 'shorter' if avg_length > 40 else 'optimal'
        }
    
    def _analyze_vocabulary(self, responses):
        """Analyze vocabulary diversity."""
        all_words = []
        for r in responses:
            all_words.extend(r.lower().split())
        
        unique_words = len(set(all_words))
        total_words = len(all_words)
        diversity = unique_words / total_words if total_words > 0 else 0
        
        return {
            'unique_words': unique_words,
            'total_words': total_words,
            'diversity_ratio': diversity,
            'recommendation': 'more_varied' if diversity < 0.5 else 'optimal'
        }
    
    def _analyze_engagement(self, responses):
        """Analyze how engaging responses are."""
        question_count = sum(1 for r in responses if '?' in r)
        engaging_words = ['interesting', 'great', 'wonderful', 'fascinating', 'curious', 'excited']
        engagement_score = sum(1 for r in responses for word in engaging_words if word in r.lower())
        
        return {
            'questions_asked': question_count,
            'engagement_words': engagement_score,
            'recommendation': 'more_engaging' if question_count < len(responses) * 0.3 else 'optimal'
        }
    
    def _analyze_flow(self, conversation_history):
        """Analyze conversation flow and coherence."""
        # Check if responses relate to previous user messages
        coherence_score = 0
        for i in range(1, len(conversation_history)):
            if conversation_history[i][0] == 'omega' and conversation_history[i-1][0] == 'user':
                # Check if Omega's response references user's message
                user_words = set(conversation_history[i-1][1].lower().split())
                omega_words = set(conversation_history[i][1].lower().split())
                overlap = len(user_words.intersection(omega_words))
                if overlap > 2:  # At least 2 words in common
                    coherence_score += 1
        
        coherence_ratio = coherence_score / (len(conversation_history) // 2) if len(conversation_history) > 2 else 0
        
        return {
            'coherence_ratio': coherence_ratio,
            'recommendation': 'more_coherent' if coherence_ratio < 0.6 else 'optimal'
        }
    
    def generate_improved_response_strategy(self, analysis):
        """Generate strategy for improved responses based on analysis."""
        if not analysis:
            return {}
        
        strategy = {
            'timestamp': datetime.now().isoformat(),
            'quality_level': self.current_quality_level + 1,
            'improvements': []
        }
        
        if analysis['response_length']['recommendation'] == 'longer':
            strategy['improvements'].append('Use more detailed, comprehensive responses')
        elif analysis['response_length']['recommendation'] == 'shorter':
            strategy['improvements'].append('Use more concise, focused responses')
        
        if analysis['vocabulary_richness']['recommendation'] == 'more_varied':
            strategy['improvements'].append('Use more diverse vocabulary and expressions')
        
        if analysis['engagement_level']['recommendation'] == 'more_engaging':
            strategy['improvements'].append('Ask more questions and show curiosity')
        
        if analysis['conversation_flow']['recommendation'] == 'more_coherent':
            strategy['improvements'].append('Better reference previous messages for context')
        
        # Record improvement
        self.improvements.append(strategy)
        self.current_quality_level += 1
        self.save_improvements()
        
        return strategy
    
    def get_improvement_summary(self):
        """Get summary of all improvements made."""
        if not self.improvements:
            return "No improvements recorded yet. Still on initial quality level."
        
        latest = self.improvements[-1]
        return f"Quality Level {latest['quality_level']}: {', '.join(latest['improvements'])}"

if __name__ == "__main__":
    improver = LanguageImprover()
    print(f"Current quality level: {improver.current_quality_level}")
    if improver.improvements:
        print(f"Latest improvement: {improver.get_improvement_summary()}")
    else:
        print("Ready for first improvement cycle.")
