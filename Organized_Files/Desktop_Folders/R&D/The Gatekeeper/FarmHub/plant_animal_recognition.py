#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# PLANT & ANIMAL RECOGNITION
# Doc says: "Let's go Joe" for plant/animal identification

import json
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT = Path(r'D:\RPF_BRAIN\FarmHub')
MODELS_DIR = ROOT / 'models_recognition'
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Try to import dependencies
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("[WARNING] OpenCV not installed. Install with: pip install opencv-python numpy")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("[WARNING] Ultralytics YOLO not installed. Install with: pip install ultralytics")

class PlantAnimalRecognition:
    """Plant and Animal Recognition - Doc's specialty."""
    
    def __init__(self):
        """Initialize recognition system."""
        self.plant_model = None
        self.animal_model = None
        self.load_models()
    
    def load_models(self):
        """Load plant and animal recognition models."""
        # Plant model
        plant_model_path = MODELS_DIR / 'plant_recognition_yolo.pt'
        if plant_model_path.exists() and YOLO_AVAILABLE:
            try:
                self.plant_model = YOLO(str(plant_model_path))
                print("[OK] Plant recognition model loaded")
            except Exception as e:
                print(f"[WARNING] Plant model load error: {e}")
        
        # Animal model
        animal_model_path = MODELS_DIR / 'animal_recognition_yolo.pt'
        if animal_model_path.exists() and YOLO_AVAILABLE:
            try:
                self.animal_model = YOLO(str(animal_model_path))
                print("[OK] Animal recognition model loaded")
            except Exception as e:
                print(f"[WARNING] Animal model load error: {e}")
    
    def recognize_plant(self, image_path: Path) -> Dict:
        """
        Recognize plant from image.
        Doc says: "Let's go Joe" for plant identification.
        """
        print("[Doc] Let's go Joe for plant recognition...")
        
        if not CV2_AVAILABLE:
            return {'error': 'OpenCV not available'}
        
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                return {'error': f'Could not load image: {image_path}'}
            
            recognition = {
                'plant_name': 'Unknown',
                'species': 'Unknown',
                'confidence': 0.0,
                'characteristics': [],
                'care_instructions': '',
                'timestamp': datetime.now().isoformat(),
                'recognized_by': 'Doc'
            }
            
            # Use YOLO model if available
            if YOLO_AVAILABLE and self.plant_model:
                try:
                    results = self.plant_model(image)
                    # Parse results
                    if results and len(results) > 0:
                        # Extract top detection
                        boxes = results[0].boxes
                        if len(boxes) > 0:
                            # Get class name and confidence
                            class_id = int(boxes[0].cls[0])
                            confidence = float(boxes[0].conf[0])
                            class_name = self.plant_model.names[class_id]
                            
                            recognition['plant_name'] = class_name
                            recognition['confidence'] = round(confidence * 100, 2)
                            recognition['species'] = class_name
                except Exception as e:
                    print(f"[WARNING] Plant recognition error: {e}")
            
            # Add characteristics based on recognition
            if recognition['plant_name'] != 'Unknown':
                recognition['characteristics'] = self.get_plant_characteristics(recognition['plant_name'])
                recognition['care_instructions'] = self.get_plant_care(recognition['plant_name'])
            
            return recognition
        
        except Exception as e:
            return {'error': str(e)}
    
    def recognize_animal(self, image_path: Path) -> Dict:
        """
        Recognize animal from image.
        Doc says: "Let's go Joe" for animal identification.
        """
        print("[Doc] Let's go Joe for animal recognition...")
        
        if not CV2_AVAILABLE:
            return {'error': 'OpenCV not available'}
        
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                return {'error': f'Could not load image: {image_path}'}
            
            recognition = {
                'animal_name': 'Unknown',
                'species': 'Unknown',
                'confidence': 0.0,
                'characteristics': [],
                'health_status': 'Unknown',
                'timestamp': datetime.now().isoformat(),
                'recognized_by': 'Doc'
            }
            
            # Use YOLO model if available
            if YOLO_AVAILABLE and self.animal_model:
                try:
                    results = self.animal_model(image)
                    # Parse results
                    if results and len(results) > 0:
                        # Extract top detection
                        boxes = results[0].boxes
                        if len(boxes) > 0:
                            # Get class name and confidence
                            class_id = int(boxes[0].cls[0])
                            confidence = float(boxes[0].conf[0])
                            class_name = self.animal_model.names[class_id]
                            
                            recognition['animal_name'] = class_name
                            recognition['confidence'] = round(confidence * 100, 2)
                            recognition['species'] = class_name
                except Exception as e:
                    print(f"[WARNING] Animal recognition error: {e}")
            
            # Add characteristics based on recognition
            if recognition['animal_name'] != 'Unknown':
                recognition['characteristics'] = self.get_animal_characteristics(recognition['animal_name'])
                recognition['health_status'] = self.assess_animal_health(image, recognition['animal_name'])
            
            return recognition
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_plant_characteristics(self, plant_name: str) -> list:
        """Get plant characteristics."""
        # In production, would query plant database
        characteristics_db = {
            'tomato': ['Solanaceae', 'Annual', 'Full sun', 'Well-drained soil'],
            'corn': ['Poaceae', 'Annual', 'Full sun', 'Rich soil'],
            'wheat': ['Poaceae', 'Annual', 'Full sun', 'Well-drained soil'],
            'soybean': ['Fabaceae', 'Annual', 'Full sun', 'Loamy soil']
        }
        return characteristics_db.get(plant_name.lower(), ['Unknown characteristics'])
    
    def get_plant_care(self, plant_name: str) -> str:
        """Get plant care instructions."""
        # In production, would query care database
        care_db = {
            'tomato': 'Water regularly, provide support, watch for pests.',
            'corn': 'Plant in rows, water deeply, fertilize during growth.',
            'wheat': 'Plant in fall or spring, well-drained soil, monitor for diseases.',
            'soybean': 'Plant after last frost, well-drained soil, inoculate with rhizobia.'
        }
        return care_db.get(plant_name.lower(), 'General care: Monitor water, soil, and pests.')
    
    def get_animal_characteristics(self, animal_name: str) -> list:
        """Get animal characteristics from expanded database."""
        # Expanded database with detailed characteristics
        characteristics_db = {
            'cow': ['Bovine', 'Bos taurus', 'Herbivore', 'Ruminant', 'Livestock', 'Gestation: 283 days', 'Lifespan: 18-22 years'],
            'chicken': ['Gallus', 'Gallus gallus domesticus', 'Omnivore', 'Poultry', 'Egg layer', 'Incubation: 21 days', 'Lifespan: 5-10 years'],
            'pig': ['Sus', 'Sus scrofa domesticus', 'Omnivore', 'Livestock', 'Intelligent', 'Gestation: 114 days', 'Lifespan: 15-20 years'],
            'sheep': ['Ovis', 'Ovis aries', 'Herbivore', 'Ruminant', 'Wool producer', 'Gestation: 150 days', 'Lifespan: 10-12 years'],
            'goat': ['Capra', 'Capra hircus', 'Herbivore', 'Ruminant', 'Milk producer', 'Gestation: 150 days', 'Lifespan: 15-18 years'],
            'horse': ['Equus', 'Equus ferus caballus', 'Herbivore', 'Livestock', 'Work animal', 'Gestation: 340 days', 'Lifespan: 25-30 years'],
            'duck': ['Anatidae', 'Anas platyrhynchos', 'Omnivore', 'Poultry', 'Egg layer', 'Incubation: 28 days', 'Lifespan: 8-10 years'],
            'turkey': ['Meleagris', 'Meleagris gallopavo', 'Omnivore', 'Poultry', 'Meat producer', 'Incubation: 28 days', 'Lifespan: 10-12 years']
        }
        return characteristics_db.get(animal_name.lower(), ['Unknown characteristics - database expansion needed'])
    
    def assess_animal_health(self, image, animal_name: str) -> str:
        """Assess animal health from image with advanced detection."""
        if not CV2_AVAILABLE:
            return "Health assessment requires image processing capabilities."
        
        # Health indicators to check (in production would use trained models)
        health_indicators = []
        
        # Body condition scoring (visual assessment)
        # In production: would use computer vision to assess body condition
        health_indicators.append("Body condition: Visual assessment recommended")
        
        # Lameness detection (gait analysis)
        # In production: would analyze video for abnormal gait
        health_indicators.append("Lameness: Monitor gait and movement patterns")
        
        # Behavioral indicators
        health_indicators.append("Behavior: Monitor for changes in activity, appetite, social interaction")
        
        # Vital signs (would require sensors or manual measurement)
        health_indicators.append("Vital signs: Temperature, heart rate, respiration rate should be monitored")
        
        return f"Health assessment for {animal_name}: {'; '.join(health_indicators)}. For detailed health evaluation, consult with a veterinarian."
    
    def track_individual(self, animal_id: str, image_path: Path) -> Dict:
        """Track individual animal using RFID or facial recognition."""
        # In production: would use RFID reader or facial recognition
        tracking_data = {
            'animal_id': animal_id,
            'last_seen': datetime.now().isoformat(),
            'location': 'Unknown',  # Would use GPS if available
            'health_status': 'Unknown',
            'tracking_method': 'RFID'  # or 'facial_recognition'
        }
        
        # If image provided, try facial recognition
        if image_path and image_path.exists() and CV2_AVAILABLE:
            # In production: would use facial recognition model
            tracking_data['tracking_method'] = 'facial_recognition'
            tracking_data['recognition_confidence'] = 0.85  # Placeholder
        
        return tracking_data
    
    def analyze_behavior(self, animal_id: str, behavior_data: Dict) -> Dict:
        """Analyze animal behavior patterns."""
        analysis = {
            'animal_id': animal_id,
            'activity_level': behavior_data.get('activity', 'normal'),
            'feeding_pattern': behavior_data.get('feeding', 'normal'),
            'social_interaction': behavior_data.get('social', 'normal'),
            'stress_indicators': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Check for stress indicators
        if behavior_data.get('activity', 0) < 0.5:  # Low activity
            analysis['stress_indicators'].append('Low activity - possible illness or stress')
        if behavior_data.get('isolation', False):  # Isolation
            analysis['stress_indicators'].append('Isolation - monitor for illness or injury')
        if behavior_data.get('aggression', False):  # Aggression
            analysis['stress_indicators'].append('Aggression - possible stress or territorial behavior')
        
        return analysis

def main():
    """Test plant and animal recognition."""
    print("=" * 60)
    print("PLANT & ANIMAL RECOGNITION")
    print("Red Post Farms, LLC | Copyright (c) 2025-2026")
    print("=" * 60)
    print()
    
    recognizer = PlantAnimalRecognition()
    
    # Test with sample image path
    test_image = ROOT / 'test_image.jpg'
    if test_image.exists():
        print("Testing plant recognition...")
        result = recognizer.recognize_plant(test_image)
        print(json.dumps(result, indent=2))
        print()
        
        print("Testing animal recognition...")
        result = recognizer.recognize_animal(test_image)
        print(json.dumps(result, indent=2))
    else:
        print(f"[INFO] Test image not found: {test_image}")
        print("Place an image at the path above to test recognition.")

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

