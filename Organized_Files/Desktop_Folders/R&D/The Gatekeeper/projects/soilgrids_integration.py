#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# SOILGRIDS API INTEGRATION
# Free global soil property maps from ISRIC
# No auth required, unlimited access

import requests
import json
import sys
import io
from pathlib import Path
from typing import Dict, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
SOIL_DIR = BRAIN / 'Archived' / 'soil_data'
SOIL_DIR.mkdir(parents=True, exist_ok=True)

class SoilGridsAPI:
    """SoilGrids API integration - free global soil property maps."""
    
    def __init__(self):
        """Initialize SoilGrids API client."""
        self.base_url = "https://rest.isric.org/soilgrids/v2.0"
        
    def get_soil_properties(self, lat: float, lon: float, properties: list = None) -> Dict:
        """
        Get soil properties for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            properties: List of properties to fetch. Default: ['clay', 'silt', 'sand', 'phh2o', 'oc', 'bdod']
        
        Returns:
            Dictionary with soil properties
        """
        if properties is None:
            properties = ['clay', 'silt', 'sand', 'phh2o', 'oc', 'bdod']
        
        try:
            # SoilGrids API endpoint
            url = f"{self.base_url}/properties/query"
            params = {
                'lon': lon,
                'lat': lat,
                'properties': ','.join(properties),
                'depth': '0-5cm',  # Can also use '5-15cm', '15-30cm', etc.
                'value': 'mean'  # Can also use 'Q0.05', 'Q0.5', 'Q0.95'
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'location': {'lat': lat, 'lon': lon},
                    'properties': data.get('properties', {}),
                    'timestamp': data.get('timestamp', '')
                }
            else:
                return {
                    'success': False,
                    'error': f"API returned status {response.status_code}",
                    'response': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_soil_map(self, bbox: list, property_name: str = 'clay', depth: str = '0-5cm') -> Optional[Dict]:
        """
        Get soil map for a bounding box.
        
        Args:
            bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
            property_name: Soil property name (clay, silt, sand, phh2o, oc, bdod)
            depth: Soil depth (0-5cm, 5-15cm, 15-30cm, etc.)
        
        Returns:
            Dictionary with map data or None
        """
        try:
            url = f"{self.base_url}/properties/{property_name}/query"
            params = {
                'bbox': ','.join(map(str, bbox)),
                'depth': depth,
                'value': 'mean'
            }
            
            response = requests.get(url, params=params, timeout=60)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[SoilGrids Error] Status {response.status_code}: {response.text}")
                return None
        
        except Exception as e:
            print(f"[SoilGrids Error] {e}")
            return None
    
    def save_soil_data(self, location_name: str, data: Dict):
        """Save soil data to file."""
        file_path = SOIL_DIR / f"soil_{location_name}_{data.get('timestamp', 'unknown')}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Soil data saved to {file_path.name}")

def main():
    """Example usage."""
    print("=" * 60)
    print("SOILGRIDS API INTEGRATION")
    print("=" * 60)
    print()
    
    api = SoilGridsAPI()
    
    # Example: Get soil properties for a location
    print("Fetching soil properties for Red Post Farms (example)...")
    result = api.get_soil_properties(lat=40.123, lon=-75.456)
    
    if result['success']:
        print("  ✓ Soil properties retrieved:")
        for prop, value in result['properties'].items():
            print(f"    {prop}: {value}")
        api.save_soil_data('red_post_farms', result)
    else:
        print(f"  ✗ Error: {result.get('error', 'Unknown error')}")
    
    print()

if __name__ == '__main__':
    main()

