"""
Omega Named Entity Recognition and Slot Filling
================================================
NER and slot filling system for extracting structured information.
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json
from datetime import datetime

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("[NER] spaCy not available. Install with: pip install spacy")
    print("[NER] Then run: python -m spacy download en_core_web_sm")

class NERSystem:
    """Named Entity Recognition and Slot Filling system"""
    
    def __init__(self, slot_file: Optional[Path] = None):
        self.base_dir = Path(__file__).parent.absolute()
        self.slot_file = slot_file or (self.base_dir / "slot_definitions.json")
        self.nlp = None
        self.slot_definitions = {}
        
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("[NER] spaCy model loaded")
            except OSError:
                print("[NER] spaCy model not found. Run: python -m spacy download en_core_web_sm")
                SPACY_AVAILABLE = False
            except Exception as e:
                print(f"[NER] Error loading spaCy model: {e}")
        
        self.load_slot_definitions()
    
    def load_slot_definitions(self):
        """Load slot definitions"""
        if not self.slot_file.exists():
            self.slot_definitions = {
                "time": {
                    "description": "Time specification",
                    "patterns": [
                        r"\d{1,2}:\d{2}(?:\s*(?:AM|PM|am|pm))?",
                        r"\d{1,2}\s*(?:AM|PM|am|pm)",
                        r"(?:at|around|about)\s+\d{1,2}",
                        r"(?:morning|afternoon|evening|night)"
                    ],
                    "spacy_labels": ["TIME"]
                },
                "date": {
                    "description": "Date specification",
                    "patterns": [
                        r"\d{1,2}/\d{1,2}/\d{2,4}",
                        r"\d{1,2}-\d{1,2}-\d{2,4}",
                        r"(?:today|tomorrow|yesterday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)",
                        r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}"
                    ],
                    "spacy_labels": ["DATE"]
                },
                "person": {
                    "description": "Person name",
                    "patterns": [],
                    "spacy_labels": ["PERSON"]
                },
                "location": {
                    "description": "Location name",
                    "patterns": [],
                    "spacy_labels": ["GPE", "LOC"]
                },
                "number": {
                    "description": "Numeric value",
                    "patterns": [
                        r"\d+",
                        r"\d+\.\d+"
                    ],
                    "spacy_labels": ["CARDINAL", "ORDINAL", "QUANTITY", "MONEY"]
                },
                "organization": {
                    "description": "Organization name",
                    "patterns": [],
                    "spacy_labels": ["ORG"]
                }
            }
            self.save_slot_definitions()
        else:
            try:
                with open(self.slot_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.slot_definitions = data.get("slots", {})
            except Exception as e:
                print(f"[NER] Error loading slot definitions: {e}")
                self.slot_definitions = {}
    
    def save_slot_definitions(self):
        """Save slot definitions"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "slots": self.slot_definitions
        }
        
        try:
            with open(self.slot_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[NER] Error saving slot definitions: {e}")
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary mapping entity types to lists of entities
        """
        entities = {}
        
        if self.nlp:
            try:
                doc = self.nlp(text)
                for ent in doc.ents:
                    entity_type = ent.label_
                    entity_text = ent.text
                    entity_span = (ent.start_char, ent.end_char)
                    
                    slot_type = self._map_spacy_label(entity_type)
                    if slot_type:
                        if slot_type not in entities:
                            entities[slot_type] = []
                        entities[slot_type].append({
                            "text": entity_text,
                            "label": entity_type,
                            "span": entity_span,
                            "confidence": 1.0  # spaCy doesn't provide confidence
                        })
            except Exception as e:
                print(f"[NER] Error extracting entities with spaCy: {e}")
        
        if not entities:
            entities = self._regex_based_extraction(text)
        
        return entities
    
    def _map_spacy_label(self, label: str) -> Optional[str]:
        """Map spaCy label to our slot type"""
        for slot_type, slot_data in self.slot_definitions.items():
            spacy_labels = slot_data.get("spacy_labels", [])
            if label in spacy_labels:
                return slot_type
        return None
    
    def _regex_based_extraction(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Fallback regex-based entity extraction"""
        entities = {}
        
        for slot_type, slot_data in self.slot_definitions.items():
            patterns = slot_data.get("patterns", [])
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if slot_type not in entities:
                        entities[slot_type] = []
                    entities[slot_type].append({
                        "text": match.group(),
                        "label": slot_type,
                        "span": (match.start(), match.end()),
                        "confidence": 0.8  # Lower confidence for regex
                    })
        
        return entities
    
    def fill_slots(self, text: str, required_slots: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fill slots from text.
        
        Args:
            text: Input text
            required_slots: List of required slot types (optional)
            
        Returns:
            Dictionary mapping slot types to extracted values
        """
        entities = self.extract_entities(text)
        
        slots = {}
        for slot_type, entity_list in entities.items():
            if entity_list:
                slots[slot_type] = entity_list[0]["text"]
        
        if required_slots:
            for slot_type in required_slots:
                if slot_type not in slots:
                    slots[slot_type] = None
        
        return slots

_ner_system = None

def get_ner_system() -> NERSystem:
    """Get global NER system instance"""
    global _ner_system
    if _ner_system is None:
        _ner_system = NERSystem()
    return _ner_system

def extract_entities(text: str) -> Dict[str, List[Dict[str, Any]]]:
    """Extract named entities from text"""
    return get_ner_system().extract_entities(text)

def fill_slots(text: str, required_slots: Optional[List[str]] = None) -> Dict[str, Any]:
    """Fill slots from text"""
    return get_ner_system().fill_slots(text, required_slots)

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" " * 20 + "OMEGA NER AND SLOT FILLING")
    print("=" * 80)
    print()
    
    ner = NERSystem()
    print("[OK] NER and slot filling system initialized")
    print(f"  - Slot types: {len(ner.slot_definitions)}")
    print(f"  - spaCy available: {SPACY_AVAILABLE}")
    print()
    print("Usage:")
    print("  from omega_ner_system import extract_entities, fill_slots")
    print("  entities = extract_entities('Meet me at 3 PM tomorrow')")
    print("  slots = fill_slots('Meet me at 3 PM tomorrow')")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
