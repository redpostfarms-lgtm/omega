#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# AGENT DOC - Medical Organizer & Marker
# Plant and animal recognition specialist

import json
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
FARMHUB = BRAIN / 'FarmHub'
ARCHIVED = BRAIN / 'Archived'
AGENT_MEMORY_DIR = ARCHIVED / 'agents'

AGENT_MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# Try to import dependencies
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

class AgentDoc:
    """
    Agent Doc - Medical Organizer & Marker
    Personality: Calm, methodical, precise. ER-trained. Organizes medical data.
    Also handles plant and animal recognition.
    """
    
    def __init__(self):
        """Initialize Agent Doc."""
        self.persona = "ER-trained physician. Calm under pressure. Methodical organizer. Marks medical data precisely. Also expert in plant and animal recognition. Says 'Let's go Joe' for plant/animal identification."
        self.memory_file = AGENT_MEMORY_DIR / 'Doc_memory.json'
        self.memory = self.load_memory()
        
        # Medical models
        self.medical_models = {}
        
        # Plant/animal recognition models
        self.plant_model = None
        self.animal_model = None
        
        # Medical data organizer
        self.medical_logs_dir = FARMHUB / 'medical_logs'
        self.medical_logs_dir.mkdir(parents=True, exist_ok=True)
    
    def load_memory(self) -> List:
        """Load persistent memory."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_memory(self):
        """Save persistent memory."""
        # Keep last 50 entries
        if len(self.memory) > 50:
            self.memory = self.memory[-50:]
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def add_memory(self, entry: Dict):
        """Add entry to memory."""
        entry['timestamp'] = datetime.now().isoformat()
        self.memory.append(entry)
        self.save_memory()
    
    def organize_medical_data(self, data: Dict) -> Dict:
        """
        Organize and mark medical data.
        Doc's specialty: organizing medical information.
        """
        organized = {
            'timestamp': datetime.now().isoformat(),
            'vitals': {},
            'conditions': [],
            'alerts': [],
            'protocols': [],
            'marked_by': 'Doc'
        }
        
        # Organize vitals
        if 'vitals' in data:
            vitals = data['vitals']
            organized['vitals'] = {
                'hr': vitals.get('hr', 0),
                'spo2': vitals.get('spo2', 0),
                'rr': vitals.get('rr', 0),
                'temp': vitals.get('temp', 0.0),
                'status': self.assess_vitals(vitals)
            }
        
        # Organize conditions
        if 'conditions' in data:
            for condition in data['conditions']:
                organized['conditions'].append({
                    'type': condition.get('type', 'unknown'),
                    'severity': condition.get('severity', 'unknown'),
                    'protocol': self.get_protocol(condition.get('type', 'unknown'))
                })
        
        # Organize alerts
        if 'alerts' in data:
            organized['alerts'] = data['alerts']
        
        # Mark with Doc's assessment
        organized['doc_assessment'] = self.assess_situation(organized)
        
        # Save to medical logs
        log_file = self.medical_logs_dir / f"medical_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(organized, f, indent=2, ensure_ascii=False)
        
        # Add to memory
        self.add_memory({
            'type': 'medical_organization',
            'data': organized
        })
        
        return organized
    
    def assess_vitals(self, vitals: Dict) -> str:
        """Assess vital signs."""
        hr = vitals.get('hr', 0)
        spo2 = vitals.get('spo2', 0)
        rr = vitals.get('rr', 0)
        
        if hr > 180 or spo2 < 85 or rr > 30:
            return "CRITICAL"
        elif hr > 120 or spo2 < 92 or rr > 24:
            return "WARNING"
        else:
            return "NORMAL"
    
    def get_protocol(self, condition_type: str) -> str:
        """Get protocol for condition."""
        protocols = {
            'fall': 'Check for injury, assess consciousness, call 911 if unresponsive.',
            'bleeding': 'Apply direct pressure, elevate if possible, call 911 if severe.',
            'seizure': 'Clear area, do not restrain, time seizure, call 911 if >5 minutes.',
            'cardiac': 'Start CPR if unresponsive, call 911 immediately.',
            'respiratory': 'Check airway, breathing, circulation. Administer rescue breaths if needed.',
            'hypoxia': 'Administer oxygen if available. Call 911 if SpO2 < 85%.'
        }
        return protocols.get(condition_type.lower(), 'Monitor closely. Call 911 if condition worsens.')
    
    def assess_situation(self, organized: Dict) -> str:
        """Doc's assessment of the situation."""
        status = organized['vitals'].get('status', 'NORMAL')
        conditions = organized.get('conditions', [])
        alerts = organized.get('alerts', [])
        
        if status == 'CRITICAL' or any(c.get('severity') == 'high' for c in conditions):
            return "CRITICAL SITUATION. Immediate intervention required. 911 protocol activated."
        elif status == 'WARNING' or len(alerts) > 0:
            return "WARNING. Monitor closely. Prepare for potential intervention."
        else:
            return "Stable. Continue monitoring. No immediate action required."
    
    def recognize_plant(self, image_path: Path) -> Dict:
        """
        Plant recognition.
        Doc says: "Let's go Joe" for plant identification.
        """
        print("[Doc] Let's go Joe for plant recognition...")
        
        try:
            # Use plant_animal_recognition module
            sys.path.insert(0, str(GATE))
            from FarmHub.plant_animal_recognition import PlantAnimalRecognition
            
            recognizer = PlantAnimalRecognition()
            recognition = recognizer.recognize_plant(image_path)
            
            # Add to memory
            self.add_memory({
                'type': 'plant_recognition',
                'image': str(image_path),
                'result': recognition
            })
            
            return recognition
        
        except Exception as e:
            return {'error': str(e)}
    
    def recognize_animal(self, image_path: Path) -> Dict:
        """
        Animal recognition.
        Doc says: "Let's go Joe" for animal identification.
        """
        print("[Doc] Let's go Joe for animal recognition...")
        
        try:
            # Use plant_animal_recognition module
            sys.path.insert(0, str(GATE))
            from FarmHub.plant_animal_recognition import PlantAnimalRecognition
            
            recognizer = PlantAnimalRecognition()
            recognition = recognizer.recognize_animal(image_path)
            
            # Add to memory
            self.add_memory({
                'type': 'animal_recognition',
                'image': str(image_path),
                'result': recognition
            })
            
            return recognition
        
        except Exception as e:
            return {'error': str(e)}
    
    def handle_medical_query(self, query: str) -> str:
        """Handle medical query with Doc's personality."""
        query_lower = query.lower()
        
        # Doc's response style: calm, methodical, precise
        if 'vitals' in query_lower or 'status' in query_lower:
            return "Reviewing vitals. Organizing data. Marking critical values. Stand by for assessment."
        elif 'emergency' in query_lower or 'critical' in query_lower:
            return "Emergency protocol activated. Organizing response data. Marking priority actions. 911 protocol engaged."
        elif 'plant' in query_lower:
            return "Let's go Joe for plant recognition. Analyzing image. Organizing plant data. Marking characteristics."
        elif 'animal' in query_lower:
            return "Let's go Joe for animal recognition. Analyzing image. Organizing animal data. Marking health status."
        else:
            return "Organizing medical data. Marking relevant information. Assessment in progress."
    
    def get_response(self, problem: str, context: Dict = None) -> str:
        """Get Doc's response to a problem."""
        problem_lower = problem.lower()
        
        # Medical queries
        if any(word in problem_lower for word in ['medical', 'health', 'vitals', 'emergency', 'fall', 'bleeding', 'seizure']):
            response = self.handle_medical_query(problem)
            return f"Doc: {response} VOTE: yes - Medical data organized and marked."
        
        # Plant recognition
        elif 'plant' in problem_lower or 'recognize plant' in problem_lower:
            response = "Let's go Joe for plant recognition. Ready to analyze plant images. Organizing plant database."
            return f"Doc: {response} VOTE: yes - Plant recognition system ready."
        
        # Animal recognition
        elif 'animal' in problem_lower or 'recognize animal' in problem_lower:
            response = "Let's go Joe for animal recognition. Ready to analyze animal images. Organizing animal database."
            return f"Doc: {response} VOTE: yes - Animal recognition system ready."
        
        # General response
        else:
            response = "Organizing data. Marking relevant information. Methodical assessment in progress."
            return f"Doc: {response} VOTE: abstain - Outside primary medical scope, but data organized."

def main():
    """Test Agent Doc."""
    print("=" * 60)
    print("AGENT DOC - Medical Organizer & Marker")
    print("Red Post Farms, LLC | Copyright (c) 2025-2026")
    print("=" * 60)
    print()
    
    doc = AgentDoc()
    
    # Test medical organization
    test_data = {
        'vitals': {'hr': 88, 'spo2': 98, 'rr': 16},
        'conditions': [{'type': 'fall', 'severity': 'low'}],
        'alerts': []
    }
    
    organized = doc.organize_medical_data(test_data)
    print("Medical data organized:")
    print(json.dumps(organized, indent=2))
    print()
    
    # Test responses
    print("Test responses:")
    print(doc.get_response("What's the medical status?"))
    print()
    print(doc.get_response("Recognize this plant"))
    print()
    print(doc.get_response("Recognize this animal"))
    print()

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

