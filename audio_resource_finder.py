#!/usr/bin/env python3
# Audio Resource Finder - Finds and catalogs free audio resources for voice improvement
import requests
import json
from pathlib import Path
from datetime import datetime

AUDIO_RESOURCES_FILE = Path('audio_resources.json')

# Comprehensive list of free audio resources
FREE_AUDIO_RESOURCES = {
    'sound_effects': {
        'Freesound': {
            'url': 'https://freesound.org',
            'license': 'CC0/CC-BY',
            'description': 'Over 500,000+ sound effects, music samples, and recordings',
            'api': 'https://freesound.org/docs/api/',
            'search_url': 'https://freesound.org/apiv2/search/text/',
        },
        'Zapsplat': {
            'url': 'https://www.zapsplat.com',
            'license': 'Free with attribution',
            'description': 'Professional sound effects library',
            'categories': ['Human voices', 'Ambient sounds', 'Foley', 'Nature'],
        },
        'BBC Sound Effects': {
            'url': 'https://sound-effects.bbcrewind.co.uk',
            'license': 'RemArc License (non-commercial)',
            'description': '16,000+ BBC sound effects from archives',
        },
        'OpenGameArt': {
            'url': 'https://opengameart.org',
            'license': 'Various open licenses',
            'description': 'Free game assets including sound effects',
        },
        'Incompetech': {
            'url': 'https://incompetech.com/music/royalty-free',
            'license': 'Creative Commons',
            'description': 'Royalty-free music and sound effects',
        },
        'Mixkit': {
            'url': 'https://mixkit.co/free-sound-effects',
            'license': 'Free license',
            'description': 'Free sound effects for video production',
        },
    },
    'voice_samples': {
        'Common Voice (Mozilla)': {
            'url': 'https://commonvoice.mozilla.org',
            'license': 'CC0',
            'description': 'Massive open dataset of voice recordings in multiple languages',
            'download': 'https://commonvoice.mozilla.org/en/datasets',
            'size': 'Thousands of hours',
        },
        'LibriSpeech': {
            'url': 'https://www.openslr.org/12/',
            'license': 'CC BY 4.0',
            'description': '1000 hours of read English speech from audiobooks',
            'formats': ['16kHz, 16-bit'],
        },
        'VoxCeleb': {
            'url': 'https://www.robots.ox.ac.uk/~vgg/data/voxceleb/',
            'license': 'Research use',
            'description': 'Large-scale speaker recognition dataset',
        },
        'TED-LIUM': {
            'url': 'http://www.openslr.org/7/',
            'license': 'CC BY-NC-ND 3.0',
            'description': 'TED talks audio dataset',
        },
        'LJSpeech': {
            'url': 'https://keithito.com/LJ-Speech-Dataset/',
            'license': 'Public Domain',
            'description': '13,100 short audio clips of a single speaker',
            'duration': '~24 hours',
        },
        'CMU ARCTIC': {
            'url': 'http://festvox.org/cmu_arctic/',
            'license': 'Free',
            'description': 'Phonetically balanced US English voices',
        },
    },
    'music_background': {
        'Free Music Archive': {
            'url': 'https://freemusicarchive.org',
            'license': 'CC licenses',
            'description': 'High-quality, legal audio downloads',
        },
        'YouTube Audio Library': {
            'url': 'https://www.youtube.com/audiolibrary',
            'license': 'Free for YouTube videos',
            'description': 'Free music and sound effects',
        },
        'Purple Planet': {
            'url': 'https://www.purple-planet.com',
            'license': 'Free with attribution',
            'description': 'Background music tracks',
        },
    }
}

def search_freesound(query, api_key=None):
    """Search Freesound.org for audio samples."""
    # Note: Requires API key from https://freesound.org/apiv2/apply/
    if not api_key:
        print(f"\n[INFO] Freesound API requires registration at: https://freesound.org/apiv2/apply/")
        print(f"       Search manually at: https://freesound.org/search/?q={query}")
        return None
    
    try:
        url = "https://freesound.org/apiv2/search/text/"
        params = {
            'query': query,
            'token': api_key,
            'fields': 'id,name,url,previews,duration',
            'page_size': 20
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Freesound search error: {e}")
    return None

def save_resources_catalog():
    """Save the resources catalog to a JSON file."""
    catalog = {
        'last_updated': datetime.now().isoformat(),
        'resources': FREE_AUDIO_RESOURCES,
        'notes': {
            'freesound_api': 'Get API key at: https://freesound.org/apiv2/apply/',
            'common_voice': 'Best for multilingual voice training data',
            'librispeech': 'Best for English TTS training',
            'ljspeech': 'Single speaker, high quality, great for voice cloning',
        }
    }
    
    with open(AUDIO_RESOURCES_FILE, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"\n[Saved] Resources catalog: {AUDIO_RESOURCES_FILE}")

def print_resources_summary():
    """Print a summary of available resources."""
    print("\n" + "=" * 70)
    print("  FREE AUDIO RESOURCES FOR VOICE IMPROVEMENT")
    print("=" * 70)
    
    for category, resources in FREE_AUDIO_RESOURCES.items():
        print(f"\n{category.replace('_', ' ').upper()}:")
        print("-" * 70)
        for name, info in resources.items():
            print(f"\n  {name}")
            print(f"    URL: {info['url']}")
            print(f"    License: {info['license']}")
            print(f"    Description: {info['description']}")
            if 'download' in info:
                print(f"    Download: {info['download']}")

def get_recommended_for_voice_improvement():
    """Get recommended resources specifically for voice/TTS improvement."""
    recommendations = {
        'voice_cloning': [
            'LJSpeech - Single speaker, 24 hours, high quality',
            'Common Voice - Diverse voices, multiple languages',
            'CMU ARCTIC - Phonetically balanced, multiple speakers',
        ],
        'voice_characteristics': [
            'LibriSpeech - Natural speech patterns',
            'TED-LIUM - Conversational speech',
            'VoxCeleb - Speaker recognition data',
        ],
        'sound_effects': [
            'Freesound - Largest collection',
            'BBC Sound Effects - Professional quality',
            'Zapsplat - Well organized categories',
        ]
    }
    
    print("\n" + "=" * 70)
    print("  RECOMMENDED RESOURCES FOR VOICE IMPROVEMENT")
    print("=" * 70)
    
    for category, items in recommendations.items():
        print(f"\n{category.replace('_', ' ').upper()}:")
        for item in items:
            print(f"  • {item}")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  AUDIO RESOURCE FINDER")
    print("=" * 70)
    
    print_resources_summary()
    get_recommended_for_voice_improvement()
    save_resources_catalog()
    
    print("\n" + "=" * 70)
    print("  NEXT STEPS")
    print("=" * 70)
    print("\n1. Download voice samples from recommended resources")
    print("2. Use conversation_recorder.py to record your voice")
    print("3. Use voice_improvement_analyzer.py to analyze characteristics")
    print("4. Compare your voice with reference samples")
    print("5. Improve TTS voice quality based on analysis")
    print()
