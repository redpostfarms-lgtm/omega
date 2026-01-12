#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# PRECISION AGRICULTURE SYSTEM
# Crop yield prediction, field zone management, variable rate recommendations
# Integrates with IoT sensors, weather data, and drone NDVI

import json
import sys
import io
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
PRECISION_DIR = BRAIN / 'Archived' / 'precision_ag'
PRECISION_DIR.mkdir(parents=True, exist_ok=True)

class PrecisionAgriculture:
    """Precision agriculture system with yield prediction and zone management."""
    
    def __init__(self):
        """Initialize precision agriculture system."""
        self.fields = {}
        self.zones = {}
        self.yield_predictions = {}
        self.historical_data = self.load_historical_data()
    
    def load_historical_data(self) -> Dict:
        """Load historical crop data."""
        data_file = PRECISION_DIR / 'historical_yields.json'
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def register_field(self, field_id: str, name: str, area_acres: float, crop_type: str):
        """Register a field."""
        self.fields[field_id] = {
            'name': name,
            'area_acres': area_acres,
            'crop_type': crop_type,
            'zones': [],
            'registered_at': datetime.now().isoformat()
        }
        print(f"[OK] Field registered: {field_id} ({name}) - {area_acres} acres, {crop_type}")
    
    def create_zone(self, field_id: str, zone_id: str, area_acres: float, soil_type: str = 'loam'):
        """Create a management zone within a field."""
        if field_id not in self.fields:
            print(f"[ERROR] Field {field_id} not found")
            return False
        
        zone = {
            'field_id': field_id,
            'zone_id': zone_id,
            'area_acres': area_acres,
            'soil_type': soil_type,
            'ndvi_avg': 0.0,
            'soil_moisture_avg': 0.0,
            'yield_prediction': 0.0,
            'created_at': datetime.now().isoformat()
        }
        
        self.zones[zone_id] = zone
        self.fields[field_id]['zones'].append(zone_id)
        
        print(f"[OK] Zone created: {zone_id} in {field_id} - {area_acres} acres")
        return True
    
    def predict_yield(self, field_id: str, zone_id: Optional[str] = None) -> Dict:
        """
        Predict crop yield using multiple factors.
        
        Factors:
        - Historical yields
        - Current NDVI
        - Soil moisture
        - Weather forecast
        - Crop type
        - Field conditions
        """
        if field_id not in self.fields:
            return {'error': 'Field not found'}
        
        field = self.fields[field_id]
        crop_type = field['crop_type']
        
        # Get zone data if specified
        if zone_id and zone_id in self.zones:
            zone = self.zones[zone_id]
            ndvi = zone.get('ndvi_avg', 0.5)
            soil_moisture = zone.get('soil_moisture_avg', 50.0)
        else:
            # Use field averages
            ndvi = 0.5
            soil_moisture = 50.0
        
        # Base yield by crop type (bushels/acre)
        base_yields = {
            'corn': 180,
            'wheat': 60,
            'soybeans': 50,
            'tomatoes': 25,  # tons/acre
            'lettuce': 15,   # tons/acre
            'potatoes': 400  # cwt/acre
        }
        
        base_yield = base_yields.get(crop_type.lower(), 100)
        
        # Adjust based on NDVI (0.3-0.7 range)
        ndvi_factor = 0.5 + (ndvi - 0.3) * 1.25  # Scale 0.3-0.7 to 0.5-1.0
        ndvi_factor = max(0.3, min(1.2, ndvi_factor))
        
        # Adjust based on soil moisture (40-60% optimal)
        if 40 <= soil_moisture <= 60:
            moisture_factor = 1.0
        elif soil_moisture < 40:
            moisture_factor = 0.7 + (soil_moisture / 40) * 0.3
        else:
            moisture_factor = 1.0 - ((soil_moisture - 60) / 40) * 0.3
        
        # Historical adjustment
        historical_factor = 1.0
        if field_id in self.historical_data:
            hist_yields = self.historical_data[field_id]
            if hist_yields:
                avg_historical = sum(hist_yields) / len(hist_yields)
                historical_factor = avg_historical / base_yield
                historical_factor = max(0.7, min(1.3, historical_factor))
        
        # Calculate predicted yield
        predicted_yield = base_yield * ndvi_factor * moisture_factor * historical_factor
        
        # Confidence based on data quality
        confidence = 0.7
        if ndvi > 0 and soil_moisture > 0:
            confidence = 0.85
        if field_id in self.historical_data and len(self.historical_data[field_id]) >= 3:
            confidence = 0.95
        
        prediction = {
            'field_id': field_id,
            'zone_id': zone_id,
            'crop_type': crop_type,
            'predicted_yield': round(predicted_yield, 2),
            'base_yield': base_yield,
            'factors': {
                'ndvi_factor': round(ndvi_factor, 3),
                'moisture_factor': round(moisture_factor, 3),
                'historical_factor': round(historical_factor, 3)
            },
            'confidence': round(confidence, 2),
            'predicted_at': datetime.now().isoformat()
        }
        
        if zone_id:
            self.zones[zone_id]['yield_prediction'] = predicted_yield
        
        self.yield_predictions[f"{field_id}_{zone_id or 'field'}"] = prediction
        
        return prediction
    
    def get_variable_rate_recommendation(self, field_id: str, zone_id: str, input_type: str = 'fertilizer') -> Dict:
        """
        Get variable rate application recommendation.
        
        Args:
            field_id: Field identifier
            zone_id: Zone identifier
            input_type: 'fertilizer', 'water', 'pesticide', 'seeds'
        """
        if zone_id not in self.zones:
            return {'error': 'Zone not found'}
        
        zone = self.zones[zone_id]
        ndvi = zone.get('ndvi_avg', 0.5)
        soil_moisture = zone.get('soil_moisture_avg', 50.0)
        
        # Base rates (per acre)
        base_rates = {
            'fertilizer': 150,  # lbs/acre
            'water': 1.0,       # inches
            'pesticide': 1.0,   # oz/acre
            'seeds': 30000     # seeds/acre
        }
        
        base_rate = base_rates.get(input_type, 100)
        
        # Adjust based on NDVI (low NDVI = more input needed)
        if ndvi < 0.4:
            adjustment = 1.2  # 20% more
        elif ndvi < 0.5:
            adjustment = 1.1  # 10% more
        elif ndvi > 0.6:
            adjustment = 0.9  # 10% less
        else:
            adjustment = 1.0
        
        # Adjust based on soil moisture (for water/fertilizer)
        if input_type in ['water', 'fertilizer']:
            if soil_moisture < 40:
                adjustment *= 1.15
            elif soil_moisture > 60:
                adjustment *= 0.9
        
        recommended_rate = base_rate * adjustment
        
        return {
            'field_id': field_id,
            'zone_id': zone_id,
            'input_type': input_type,
            'recommended_rate': round(recommended_rate, 2),
            'base_rate': base_rate,
            'adjustment_factor': round(adjustment, 3),
            'reasoning': f"NDVI: {ndvi:.2f}, Soil Moisture: {soil_moisture:.1f}%",
            'recommended_at': datetime.now().isoformat()
        }
    
    def update_zone_data(self, zone_id: str, ndvi: Optional[float] = None, soil_moisture: Optional[float] = None):
        """Update zone data from sensors/drones."""
        if zone_id not in self.zones:
            return False
        
        if ndvi is not None:
            self.zones[zone_id]['ndvi_avg'] = ndvi
        if soil_moisture is not None:
            self.zones[zone_id]['soil_moisture_avg'] = soil_moisture
        
        # Recalculate yield prediction
        field_id = self.zones[zone_id]['field_id']
        self.predict_yield(field_id, zone_id)
        
        return True
    
    def generate_field_map(self, field_id: str) -> Dict:
        """Generate field map with zones and recommendations."""
        if field_id not in self.fields:
            return {'error': 'Field not found'}
        
        field = self.fields[field_id]
        zones_data = []
        
        for zone_id in field['zones']:
            if zone_id in self.zones:
                zone = self.zones[zone_id]
                zones_data.append({
                    'zone_id': zone_id,
                    'area_acres': zone['area_acres'],
                    'ndvi': zone.get('ndvi_avg', 0.0),
                    'soil_moisture': zone.get('soil_moisture_avg', 0.0),
                    'yield_prediction': zone.get('yield_prediction', 0.0)
                })
        
        return {
            'field_id': field_id,
            'field_name': field['name'],
            'total_acres': field['area_acres'],
            'crop_type': field['crop_type'],
            'zones': zones_data,
            'total_zones': len(zones_data),
            'generated_at': datetime.now().isoformat()
        }
    
    def save_data(self):
        """Save precision agriculture data."""
        data_file = PRECISION_DIR / 'precision_data.json'
        data = {
            'fields': self.fields,
            'zones': self.zones,
            'yield_predictions': self.yield_predictions,
            'updated_at': datetime.now().isoformat()
        }
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Precision Agriculture System')
    parser.add_argument('--register-field', nargs=4, metavar=('ID', 'NAME', 'ACRES', 'CROP'),
                       help='Register a field')
    parser.add_argument('--create-zone', nargs=4, metavar=('FIELD_ID', 'ZONE_ID', 'ACRES', 'SOIL'),
                       help='Create a zone')
    parser.add_argument('--predict-yield', nargs=2, metavar=('FIELD_ID', 'ZONE_ID'),
                       help='Predict yield for field/zone')
    parser.add_argument('--variable-rate', nargs=3, metavar=('FIELD_ID', 'ZONE_ID', 'INPUT_TYPE'),
                       help='Get variable rate recommendation')
    parser.add_argument('--field-map', help='Generate field map')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("PRECISION AGRICULTURE SYSTEM")
    print("Red Post Farms, LLC | Copyright (c) 2025-2026")
    print("=" * 60)
    print()
    print("The doors of knowledge opens.")
    print("Precision agriculture system initializing...\n")
    
    pa = PrecisionAgriculture()
    
    if args.register_field:
        field_id, name, acres, crop = args.register_field
        pa.register_field(field_id, name, float(acres), crop)
        pa.save_data()
    
    elif args.create_zone:
        field_id, zone_id, acres, soil = args.create_zone
        pa.create_zone(field_id, zone_id, float(acres), soil)
        pa.save_data()
    
    elif args.predict_yield:
        field_id, zone_id = args.predict_yield
        prediction = pa.predict_yield(field_id, zone_id if zone_id != 'None' else None)
        print(json.dumps(prediction, indent=2))
        pa.save_data()
    
    elif args.variable_rate:
        field_id, zone_id, input_type = args.variable_rate
        recommendation = pa.get_variable_rate_recommendation(field_id, zone_id, input_type)
        print(json.dumps(recommendation, indent=2))
    
    elif args.field_map:
        field_map = pa.generate_field_map(args.field_map)
        print(json.dumps(field_map, indent=2))
    
    else:
        print("Usage examples:")
        print("  --register-field field1 'Field A' 10 corn")
        print("  --create-zone field1 zone1 2.5 loam")
        print("  --predict-yield field1 zone1")
        print("  --variable-rate field1 zone1 fertilizer")
        print("  --field-map field1")

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

