"""
Omega Language Enhancer - Integrates Slang into Speech Patterns
===============================================================
Enhances Omega's language generation with context-aware slang usage.
"""

from omega_slang_processor_optimized import get_slang_processor, Context, Formality
from typing import Optional, List, Tuple
import random

class LanguageEnhancer:
    """Enhances language with appropriate slang usage"""
    
    def __init__(self):
        self.slang_processor = get_slang_processor()
        self.formality_level = Formality.NEUTRAL  # Default to neutral
        self.context = Context.CODING  # Default context
    
    def set_formality(self, level: Formality):
        """Set desired formality level"""
        self.formality_level = level
    
    def set_context(self, context: Context):
        """Set conversation context"""
        self.context = context
    
    def enhance_response(self, response: str, detected_slang: Optional[List[Tuple[str, dict]]] = None) -> str:
        """Enhance response with appropriate slang"""
        if detected_slang:
            slang_levels = [s[1].get('formality', 'NEUTRAL') for s in detected_slang]
            if slang_levels:
                pass  # Keep original response, slang is already appropriate
        
        if self.context == Context.CODING and self.formality_level >= Formality.INFORMAL:
            pass
        
        return response
    
    def detect_user_slang(self, user_text: str) -> List[Tuple[str, dict]]:
        """Detect slang in user's text"""
        return self.slang_processor.detect_slang(user_text)
    
    def adapt_formality(self, user_text: str) -> Formality:
        """Adapt formality based on user's language"""
        detected = self.detect_user_slang(user_text)
        
        if not detected:
            return self.formality_level  # Keep current
        
        slang_formalities = []
        for term, info in detected:
            formality_str = info.get('formality', 'NEUTRAL')
            try:
                slang_formalities.append(Formality[formality_str])
            except:
                pass
        
        if slang_formalities:
            avg_formality = sum(f.value for f in slang_formalities) / len(slang_formalities)
            formality_idx = int(avg_formality)
            return Formality(formality_idx)
        
        return self.formality_level
    
    def generate_slang_aware_response(self, base_response: str, user_text: str, 
                                     context: Optional[Context] = None) -> str:
        """Generate response with slang awareness"""
        detected_slang = self.detect_user_slang(user_text)
        
        if detected_slang:
            self.formality_level = self.adapt_formality(user_text)
            if context:
                self.context = context
        
        enhanced = self.enhance_response(base_response, detected_slang)
        
        return enhanced
    
    def is_informal_context(self, user_text: str) -> bool:
        """Check if user's text suggests informal context"""
        informal_indicators = ['lol', 'omg', 'dude', 'cool', 'awesome', 'yeah', 'yea', 
                              'gonna', 'wanna', 'gotta', 'ya', 'nah', 'nope']
        text_lower = user_text.lower()
        return any(indicator in text_lower for indicator in informal_indicators)
    
    def can_use_slang(self, response: str) -> bool:
        """Check if slang can be used in response"""
        
        if self.formality_level < Formality.INFORMAL:
            return False
        
        conversational_indicators = ['great', 'awesome', 'cool', 'interesting', 'nice', 'wonderful']
        response_lower = response.lower()
        is_conversational = any(indicator in response_lower for indicator in conversational_indicators)
        
        return is_conversational

_language_enhancer = None

def get_language_enhancer() -> LanguageEnhancer:
    """Get singleton language enhancer"""
    global _language_enhancer
    if _language_enhancer is None:
        _language_enhancer = LanguageEnhancer()
    return _language_enhancer
