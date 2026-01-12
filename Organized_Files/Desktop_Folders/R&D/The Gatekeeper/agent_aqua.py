#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# AGENT AQUA - Water & Purification Specialist
# Handles water sensors, purification, insect & plant recognition

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

class AgentAqua:
    """
    Agent Aqua - Water & Purification Specialist
    Personality: Water engineer. Precision-focused. Monitors all water sensors.
    Handles purification, insect recognition, and plant recognition.
    """
    
    def __init__(self):
        """Initialize Agent Aqua."""
        self.persona = "Water engineer and purification specialist. Precision-focused. Monitors all water sensors (pH, TDS, EC, ORPC, flow, pressure). Expert in water purification systems. Handles insect recognition for pest detection and plant recognition for crop monitoring. Says 'Let's go Joe' for insect and plant identification."
        self.memory_file = AGENT_MEMORY_DIR / 'Aqua_memory.json'
        self.memory = self.load_memory()
        
        # Water sensors (from FarmHub sensor list)
        self.water_sensors = [
            'ph_water',
            'tds_water',
            'ec_water',
            'orpc_water',
            'flow_in_main',
            'flow_out_irrigation',
            'flow_tap',
            'flow_drain',
            'pressure_water_tank',
            'temp_water_reservoir'
        ]
        
        # Recognition models
        self.insect_model = None
        self.plant_model = None
        
        # Water logs
        self.water_logs_dir = FARMHUB / 'water_logs'
        self.water_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Purification system state
        self.purification_state = {
            'active': False,
            'mode': 'auto',
            'filter_status': 'unknown',
            'last_maintenance': None
        }
    
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
    
    def get_water_sensor_data(self) -> Dict:
        """Get current water sensor data from FarmHub."""
        water_data = {
            'timestamp': datetime.now().isoformat(),
            'sensors': {},
            'status': 'unknown',
            'analyzed_by': 'Aqua'
        }
        
        try:
            # Try to read from sensor log
            sensor_log = FARMHUB / 'sensor_log.csv'
            if sensor_log.exists():
                import csv
                with open(sensor_log, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    if rows:
                        latest = rows[-1]
                        for sensor in self.water_sensors:
                            if sensor in latest:
                                value = latest[sensor]
                                if value:
                                    water_data['sensors'][sensor] = float(value)
        except Exception as e:
            print(f"[WARNING] Error reading water sensor data: {e}")
        
        # Assess water quality
        water_data['status'] = self.assess_water_quality(water_data['sensors'])
        
        return water_data
    
    def assess_water_quality(self, sensors: Dict) -> str:
        """Assess water quality from sensor data."""
        ph = sensors.get('ph_water', 7.0)
        tds = sensors.get('tds_water', 0)
        ec = sensors.get('ec_water', 0)
        orpc = sensors.get('orpc_water', 0)
        
        issues = []
        
        # pH check (optimal: 6.5-7.5)
        if ph < 6.5:
            issues.append('pH too low (acidic)')
        elif ph > 7.5:
            issues.append('pH too high (alkaline)')
        
        # TDS check (optimal: <500 ppm for drinking, <1000 for irrigation)
        if tds > 1000:
            issues.append('TDS too high')
        
        # EC check (optimal: 0.5-2.0 dS/m for most crops)
        if ec > 2.0:
            issues.append('EC too high (salinity)')
        
        # ORPC check (oxidation-reduction potential, optimal: 200-400 mV)
        if orpc < 200:
            issues.append('ORPC too low (reducing conditions)')
        elif orpc > 400:
            issues.append('ORPC too high (oxidizing conditions)')
        
        if issues:
            return f"WARNING: {', '.join(issues)}"
        else:
            return "GOOD - All parameters within optimal range"
    
    def recommend_purification(self, water_data: Dict) -> Dict:
        """Recommend purification actions based on water quality."""
        recommendations = {
            'purification_needed': False,
            'methods': [],
            'priority': 'low',
            'timestamp': datetime.now().isoformat()
        }
        
        sensors = water_data.get('sensors', {})
        status = water_data.get('status', '')
        
        if 'WARNING' in status:
            recommendations['purification_needed'] = True
            recommendations['priority'] = 'high'
            
            # Recommend specific purification methods
            ph = sensors.get('ph_water', 7.0)
            tds = sensors.get('tds_water', 0)
            ec = sensors.get('ec_water', 0)
            
            if ph < 6.5 or ph > 7.5:
                recommendations['methods'].append('pH adjustment (add lime for low pH, acid for high pH)')
            
            if tds > 1000:
                recommendations['methods'].append('Reverse osmosis or distillation for TDS reduction')
            
            if ec > 2.0:
                recommendations['methods'].append('Desalination or dilution for EC reduction')
            
            # General filtration
            recommendations['methods'].append('Activated carbon filtration')
            recommendations['methods'].append('Sediment filtration')
        
        return recommendations
    
    def control_purification_system(self, action: str, mode: str = 'auto') -> Dict:
        """Control water purification system."""
        result = {
            'action': action,
            'mode': mode,
            'status': 'unknown',
            'timestamp': datetime.now().isoformat()
        }
        
        if action == 'start':
            self.purification_state['active'] = True
            self.purification_state['mode'] = mode
            result['status'] = 'Purification system started'
        elif action == 'stop':
            self.purification_state['active'] = False
            result['status'] = 'Purification system stopped'
        elif action == 'status':
            result['status'] = 'Active' if self.purification_state['active'] else 'Inactive'
            result['mode'] = self.purification_state['mode']
        
        # Log action
        self.add_memory({
            'type': 'purification_control',
            'data': result
        })
        
        return result
    
    def recognize_insect(self, image_path: Path) -> Dict:
        """
        Insect recognition for pest detection.
        Aqua says: "Let's go Joe" for insect identification.
        """
        print("[Aqua] Let's go Joe for insect recognition...")
        
        if not CV2_AVAILABLE:
            return {'error': 'OpenCV not available'}
        
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                return {'error': f'Could not load image: {image_path}'}
            
            recognition = {
                'insect_name': 'Unknown',
                'species': 'Unknown',
                'confidence': 0.0,
                'is_pest': False,
                'threat_level': 'unknown',
                'treatment': '',
                'timestamp': datetime.now().isoformat(),
                'recognized_by': 'Aqua'
            }
            
            # Use YOLO model if available
            if YOLO_AVAILABLE and self.insect_model:
                try:
                    results = self.insect_model(image)
                    # Parse results
                    if results and len(results) > 0:
                        boxes = results[0].boxes
                        if len(boxes) > 0:
                            class_id = int(boxes[0].cls[0])
                            confidence = float(boxes[0].conf[0])
                            class_name = self.insect_model.names[class_id]
                            
                            recognition['insect_name'] = class_name
                            recognition['confidence'] = round(confidence * 100, 2)
                            recognition['species'] = class_name
                            
                            # Determine if pest
                            recognition['is_pest'] = self.is_pest_insect(class_name)
                            if recognition['is_pest']:
                                recognition['threat_level'] = self.assess_pest_threat(class_name)
                                recognition['treatment'] = self.get_pest_treatment(class_name)
                except Exception as e:
                    print(f"[WARNING] Insect recognition error: {e}")
            
            # Add to memory
            self.add_memory({
                'type': 'insect_recognition',
                'image': str(image_path),
                'result': recognition
            })
            
            return recognition
        
        except Exception as e:
            return {'error': str(e)}
    
    def recognize_plant(self, image_path: Path) -> Dict:
        """
        Plant recognition for crop monitoring.
        Aqua says: "Let's go Joe" for plant identification.
        """
        print("[Aqua] Let's go Joe for plant recognition...")
        
        try:
            # Use plant_animal_recognition module
            sys.path.insert(0, str(GATE))
            from FarmHub.plant_animal_recognition import PlantAnimalRecognition
            
            recognizer = PlantAnimalRecognition()
            recognition = recognizer.recognize_plant(image_path)
            
            # Add water-specific analysis
            recognition['water_needs'] = self.assess_plant_water_needs(recognition.get('plant_name', 'Unknown'))
            recognition['irrigation_recommendation'] = self.get_irrigation_recommendation(recognition)
            
            # Add to memory
            self.add_memory({
                'type': 'plant_recognition',
                'image': str(image_path),
                'result': recognition
            })
            
            return recognition
        
        except Exception as e:
            return {'error': str(e)}
    
    def is_pest_insect(self, insect_name: str) -> bool:
        """Determine if insect is a pest."""
        pest_insects = [
            'aphid', 'spider mite', 'thrip', 'whitefly', 'mealybug',
            'scale', 'leaf miner', 'caterpillar', 'beetle', 'moth',
            'grasshopper', 'locust', 'stink bug', 'leafhopper'
        ]
        return any(pest in insect_name.lower() for pest in pest_insects)
    
    def assess_pest_threat(self, insect_name: str) -> str:
        """Assess pest threat level."""
        high_threat = ['aphid', 'spider mite', 'thrip', 'whitefly', 'locust']
        medium_threat = ['mealybug', 'scale', 'leaf miner', 'beetle']
        
        insect_lower = insect_name.lower()
        if any(threat in insect_lower for threat in high_threat):
            return 'high'
        elif any(threat in insect_lower for threat in medium_threat):
            return 'medium'
        else:
            return 'low'
    
    def get_pest_treatment(self, insect_name: str) -> str:
        """Get pest treatment recommendation."""
        treatments = {
            'aphid': 'Apply neem oil or insecticidal soap. Introduce ladybugs.',
            'spider mite': 'Increase humidity. Apply miticide. Remove affected leaves.',
            'thrip': 'Apply spinosad or neem oil. Use blue sticky traps.',
            'whitefly': 'Apply insecticidal soap. Use yellow sticky traps. Introduce parasitic wasps.',
            'mealybug': 'Apply rubbing alcohol or neem oil. Remove manually if possible.',
            'scale': 'Apply horticultural oil. Remove manually with soft brush.',
            'leaf miner': 'Remove affected leaves. Apply spinosad. Use row covers.',
            'beetle': 'Hand pick. Apply neem oil or pyrethrin.',
            'locust': 'Immediate action required. Contact agricultural extension. Use approved pesticides.'
        }
        
        insect_lower = insect_name.lower()
        for pest, treatment in treatments.items():
            if pest in insect_lower:
                return treatment
        
        return 'Monitor closely. Apply general insecticide if population increases.'
    
    def assess_plant_water_needs(self, plant_name: str) -> str:
        """Assess plant water needs."""
        water_needs_db = {
            'tomato': 'High - 1-2 inches per week',
            'corn': 'High - 1-1.5 inches per week',
            'wheat': 'Moderate - 0.75-1 inch per week',
            'soybean': 'Moderate - 0.75-1 inch per week',
            'lettuce': 'High - Keep soil consistently moist',
            'pepper': 'Moderate - 1 inch per week',
            'cucumber': 'High - 1-2 inches per week'
        }
        return water_needs_db.get(plant_name.lower(), 'Moderate - Monitor soil moisture')
    
    def get_irrigation_recommendation(self, plant_recognition: Dict) -> Dict:
        """Get irrigation recommendation based on plant recognition."""
        plant_name = plant_recognition.get('plant_name', 'Unknown')
        water_needs = self.assess_plant_water_needs(plant_name)
        
        # Get current water sensor data
        water_data = self.get_water_sensor_data()
        flow_irrigation = water_data.get('sensors', {}).get('flow_out_irrigation', 0)
        
        recommendation = {
            'plant': plant_name,
            'water_needs': water_needs,
            'current_flow': flow_irrigation,
            'recommendation': 'Monitor',
            'action': 'No change needed'
        }
        
        # Determine recommendation based on water needs and current flow
        if 'High' in water_needs and flow_irrigation < 10:
            recommendation['recommendation'] = 'Increase irrigation'
            recommendation['action'] = 'Increase flow to 15-20 L/min'
        elif 'Moderate' in water_needs and flow_irrigation > 15:
            recommendation['recommendation'] = 'Reduce irrigation'
            recommendation['action'] = 'Reduce flow to 8-12 L/min'
        
        return recommendation
    
    def get_response(self, problem: str, context: Dict = None) -> str:
        """Get Aqua's response to a problem."""
        problem_lower = problem.lower()
        
        # Water-related queries
        if any(word in problem_lower for word in ['water', 'purification', 'ph', 'tds', 'ec', 'flow', 'irrigation']):
            water_data = self.get_water_sensor_data()
            recommendations = self.recommend_purification(water_data)
            
            response = f"Water quality: {water_data['status']}. "
            if recommendations['purification_needed']:
                response += f"Purification needed: {', '.join(recommendations['methods'])}. "
            response += "Monitoring all water sensors. VOTE: yes - Water systems operational."
            return f"Aqua: {response}"
        
        # Insect recognition
        elif 'insect' in problem_lower or 'pest' in problem_lower or 'recognize insect' in problem_lower:
            response = "Let's go Joe for insect recognition. Ready to analyze insect images for pest detection. Monitoring for threats."
            return f"Aqua: {response} VOTE: yes - Insect recognition system ready."
        
        # Plant recognition
        elif 'plant' in problem_lower or 'recognize plant' in problem_lower or 'crop' in problem_lower:
            response = "Let's go Joe for plant recognition. Ready to analyze plant images for crop monitoring. Assessing water needs."
            return f"Aqua: {response} VOTE: yes - Plant recognition system ready."
        
        # General response
        else:
            response = "Monitoring water sensors. Analyzing water quality. Purification systems ready."
            return f"Aqua: {response} VOTE: abstain - Outside primary water scope, but monitoring active."

def main():
    """Test Agent Aqua."""
    print("=" * 60)
    print("AGENT AQUA - Water & Purification Specialist")
    print("Red Post Farms, LLC | Copyright (c) 2025-2026")
    print("=" * 60)
    print()
    
    aqua = AgentAqua()
    
    # Test water sensor data
    water_data = aqua.get_water_sensor_data()
    print("Water sensor data:")
    print(json.dumps(water_data, indent=2))
    print()
    
    # Test responses
    print("Test responses:")
    print(aqua.get_response("What's the water quality?"))
    print()
    print(aqua.get_response("Recognize this insect"))
    print()
    print(aqua.get_response("Recognize this plant"))
    print()

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

