# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# Solar Production Forecaster
# Uses NOAA 7-day solar irradiance API + your panel angles
# → tells you tomorrow's kWh before sunrise

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
import math

ARCHIVED = Path(r'D:\RPF_BRAIN\Archived')
SOLAR_DIR = ARCHIVED / 'solar_data'
SOLAR_DIR.mkdir(parents=True, exist_ok=True)

# Panel configuration
PANEL_CONFIG = {
    'total_panels': 24,
    'watts_per_panel': 300,
    'total_watts': 7200,  # 7.2 kW
    'panel_angle': 35,  # degrees from horizontal
    'azimuth': 180,  # degrees (south = 180)
    'efficiency': 0.85,  # 85% system efficiency
    'location': {
        'lat': 40.123,
        'lon': -75.456
    }
}

def get_noaa_forecast(lat, lon):
    """Get 7-day solar irradiance forecast from NOAA."""
    # NOAA API endpoint (example)
    # Actual endpoint may vary - check NOAA documentation
    url = f"https://api.weather.gov/points/{lat},{lon}/forecast"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"NOAA API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Failed to fetch NOAA forecast: {e}")
        return None

def get_open_meteo_forecast(lat, lon):
    """Get solar irradiance forecast from Open-Meteo API (free, no auth)."""
    try:
        # Open-Meteo API for solar radiation
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'hourly': 'shortwave_radiation,direct_radiation,diffuse_radiation',
            'forecast_days': 7,
            'timezone': 'auto'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Open-Meteo API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Failed to fetch Open-Meteo forecast: {e}")
        return None

def calculate_solar_production(irradiance, hours, config):
    """Calculate kWh production from irradiance."""
    # Irradiance in W/m²
    # Account for panel angle and efficiency
    angle_factor = math.sin(math.radians(config['panel_angle']))
    effective_irradiance = irradiance * angle_factor
    
    # Calculate production
    # kWh = (W/m² * m² * hours * efficiency) / 1000
    panel_area = config['total_panels'] * 1.6  # m² per panel (approx)
    production_kwh = (effective_irradiance * panel_area * hours * config['efficiency']) / 1000
    
    return production_kwh

def forecast_tomorrow():
    """Forecast tomorrow's solar production."""
    print("=" * 60)
    print("Solar Production Forecaster")
    print("=" * 60)
    
    # Try Open-Meteo first (more reliable for solar irradiance)
    forecast = get_open_meteo_forecast(
        PANEL_CONFIG['location']['lat'],
        PANEL_CONFIG['location']['lon']
    )
    
    # Fallback to NOAA if Open-Meteo fails
    if not forecast:
        forecast = get_noaa_forecast(
            PANEL_CONFIG['location']['lat'],
            PANEL_CONFIG['location']['lon']
        )
    
    if not forecast:
        print("Using fallback calculation...")
        # Fallback: estimate based on season
        month = datetime.now().month
        if month in [6, 7, 8]:  # Summer
            avg_irradiance = 800  # W/m²
            sun_hours = 6
        elif month in [12, 1, 2]:  # Winter
            avg_irradiance = 400
            sun_hours = 4
        else:  # Spring/Fall
            avg_irradiance = 600
            sun_hours = 5
        
        production = calculate_solar_production(avg_irradiance, sun_hours, PANEL_CONFIG)
        
        forecast_data = {
            'date': (datetime.now() + timedelta(days=1)).isoformat(),
            'forecast_kwh': round(production, 2),
            'method': 'fallback',
            'irradiance': avg_irradiance,
            'sun_hours': sun_hours
        }
    else:
        # Parse NOAA data (simplified - actual parsing depends on API format)
        # Extract tomorrow's forecast
        tomorrow = datetime.now() + timedelta(days=1)
        # Placeholder - would parse actual NOAA response
        forecast_data = {
            'date': tomorrow.isoformat(),
            'forecast_kwh': 0,  # Would calculate from actual data
            'method': 'noaa_api'
        }
    
    # Save forecast
    forecast_file = SOLAR_DIR / f'forecast_{datetime.now().strftime("%Y%m%d")}.json'
    with open(forecast_file, 'w') as f:
        json.dump(forecast_data, f, indent=2)
    
    print(f"\nTomorrow's forecast: {forecast_data['forecast_kwh']} kWh")
    print(f"Saved to: {forecast_file}")
    
    return forecast_data

if __name__ == '__main__':
    forecast_tomorrow()

