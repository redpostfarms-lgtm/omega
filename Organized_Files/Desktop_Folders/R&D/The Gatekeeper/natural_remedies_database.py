#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# NATURAL REMEDIES DATABASE
# Comprehensive database of natural pest and disease remedies
# Integrated with pest detection system

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
REMEDIES_DIR = GATE / 'natural_remedies'
REMEDIES_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class NaturalRemedy:
    """Natural remedy for pest or disease."""
    name: str
    type: str  # 'pest' or 'disease'
    target: str  # pest/disease name
    recipe: Dict[str, Any]
    application: str
    frequency: str
    effectiveness: str
    safety: str
    prevention: bool = False

@dataclass
class BeneficialInsect:
    """Beneficial insect for pest control."""
    name: str
    scientific_name: str
    targets: List[str]
    release_rate: str
    best_time: str
    effectiveness: str

class NaturalRemediesDatabase:
    """Database of natural pest and disease remedies."""
    
    def __init__(self):
        """Initialize remedies database."""
        self.remedies_file = REMEDIES_DIR / 'natural_remedies.json'
        self.remedies = self._load_remedies()
        self.beneficial_insects = self._load_beneficial_insects()
    
    def _load_remedies(self) -> Dict[str, List[NaturalRemedy]]:
        """Load natural remedies database."""
        if self.remedies_file.exists():
            try:
                with open(self.remedies_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert back to NaturalRemedy objects
                    remedies = {}
                    for target, remedy_list in data.items():
                        remedies[target] = [NaturalRemedy(**r) for r in remedy_list]
                    return remedies
            except Exception as e:
                print(f"[WARNING] Could not load remedies: {e}")
        
        # Default comprehensive database
        return self._create_default_remedies()
    
    def _create_default_remedies(self) -> Dict[str, List[NaturalRemedy]]:
        """Create default natural remedies database."""
        remedies = {
            'aphids': [
                NaturalRemedy(
                    name="Neem Oil Spray",
                    type="pest",
                    target="aphids",
                    recipe={
                        "neem_oil": "2-3 tsp",
                        "liquid_soap": "1 tsp",
                        "water": "1 quart"
                    },
                    application="Spray every 3-5 days until controlled. Cover all leaf surfaces.",
                    frequency="Every 3-5 days",
                    effectiveness="90-95%",
                    safety="Safe for beneficial insects when used properly"
                ),
                NaturalRemedy(
                    name="Insecticidal Soap",
                    type="pest",
                    target="aphids",
                    recipe={
                        "liquid_soap": "1.5 tsp",
                        "water": "1 quart"
                    },
                    application="Spray directly on aphids. Rinse after 2 hours.",
                    frequency="Every 3-5 days",
                    effectiveness="85-90%",
                    safety="Rinse plants to prevent leaf burn"
                ),
                NaturalRemedy(
                    name="Beneficial Insects",
                    type="pest",
                    target="aphids",
                    recipe={
                        "ladybugs": "1,500-2,000 per acre",
                        "lacewings": "1,000-2,000 per acre"
                    },
                    application="Release early morning or evening. Provide water source.",
                    frequency="One-time or as needed",
                    effectiveness="80-90%",
                    safety="100% safe, natural predators",
                    prevention=True
                ),
                NaturalRemedy(
                    name="Garlic Spray",
                    type="pest",
                    target="aphids",
                    recipe={
                        "garlic": "4-5 cloves",
                        "water": "1 quart"
                    },
                    application="Spray every 3-4 days. Test on small area first.",
                    frequency="Every 3-4 days",
                    effectiveness="70-80%",
                    safety="Test on small area first"
                )
            ],
            'spider_mites': [
                NaturalRemedy(
                    name="Water Spray",
                    type="pest",
                    target="spider_mites",
                    recipe={
                        "water": "Strong stream"
                    },
                    application="Spray with strong stream of water daily for 3-5 days.",
                    frequency="Daily for 3-5 days",
                    effectiveness="80-85%",
                    safety="100% safe"
                ),
                NaturalRemedy(
                    name="Neem Oil",
                    type="pest",
                    target="spider_mites",
                    recipe={
                        "neem_oil": "2-3 tsp",
                        "liquid_soap": "1 tsp",
                        "water": "1 quart"
                    },
                    application="Spray every 5-7 days. Increase humidity.",
                    frequency="Every 5-7 days",
                    effectiveness="85-90%",
                    safety="Safe for beneficial insects"
                ),
                NaturalRemedy(
                    name="Predatory Mites",
                    type="pest",
                    target="spider_mites",
                    recipe={
                        "phytoseiulus_persimilis": "1,000-2,000 per acre"
                    },
                    application="Release early morning. Maintain humidity 50-60%.",
                    frequency="One-time or as needed",
                    effectiveness="85-95%",
                    safety="100% safe, natural predators",
                    prevention=True
                )
            ],
            'whiteflies': [
                NaturalRemedy(
                    name="Yellow Sticky Traps",
                    type="pest",
                    target="whiteflies",
                    recipe={
                        "yellow_sticky_cards": "1 per 50-100 sq ft"
                    },
                    application="Place traps near plants. Replace when full.",
                    frequency="Continuous",
                    effectiveness="70-80%",
                    safety="100% safe"
                ),
                NaturalRemedy(
                    name="Neem Oil",
                    type="pest",
                    target="whiteflies",
                    recipe={
                        "neem_oil": "2-3 tsp",
                        "liquid_soap": "1 tsp",
                        "water": "1 quart"
                    },
                    application="Spray every 5-7 days. Focus on undersides of leaves.",
                    frequency="Every 5-7 days",
                    effectiveness="85-90%",
                    safety="Safe for beneficial insects"
                ),
                NaturalRemedy(
                    name="Encarsia formosa",
                    type="pest",
                    target="whiteflies",
                    recipe={
                        "parasitic_wasps": "1,000-5,000 per acre"
                    },
                    application="Release early morning. Provide nectar sources.",
                    frequency="One-time or as needed",
                    effectiveness="80-95%",
                    safety="100% safe, natural predators",
                    prevention=True
                )
            ],
            'caterpillars': [
                NaturalRemedy(
                    name="Bacillus thuringiensis (Bt)",
                    type="pest",
                    target="caterpillars",
                    recipe={
                        "bt_kurstaki": "Follow label instructions"
                    },
                    application="Spray on leaves. Most effective on young caterpillars.",
                    frequency="Every 5-7 days or as needed",
                    effectiveness="90-95%",
                    safety="Safe for humans, pets, beneficial insects"
                ),
                NaturalRemedy(
                    name="Handpicking",
                    type="pest",
                    target="caterpillars",
                    recipe={},
                    application="Remove caterpillars by hand. Drop in soapy water.",
                    frequency="Daily during peak season",
                    effectiveness="80-90%",
                    safety="100% safe"
                ),
                NaturalRemedy(
                    name="Row Covers",
                    type="pest",
                    target="caterpillars",
                    recipe={
                        "fine_mesh": "Cover plants"
                    },
                    application="Install before egg-laying season. Remove for pollination.",
                    frequency="Season-long",
                    effectiveness="95%+",
                    safety="100% safe",
                    prevention=True
                )
            ],
            'powdery_mildew': [
                NaturalRemedy(
                    name="Baking Soda Spray",
                    type="disease",
                    target="powdery_mildew",
                    recipe={
                        "baking_soda": "1 tsp",
                        "liquid_soap": "1 tsp",
                        "water": "1 quart"
                    },
                    application="Spray every 7-10 days (preventive) or 3-5 days (active).",
                    frequency="Every 7-10 days (preventive)",
                    effectiveness="80-85%",
                    safety="Test on small area first"
                ),
                NaturalRemedy(
                    name="Milk Spray",
                    type="disease",
                    target="powdery_mildew",
                    recipe={
                        "milk": "1 part",
                        "water": "9 parts"
                    },
                    application="Spray every 7-10 days. Apply in morning.",
                    frequency="Every 7-10 days",
                    effectiveness="75-80%",
                    safety="100% safe"
                ),
                NaturalRemedy(
                    name="Neem Oil",
                    type="disease",
                    target="powdery_mildew",
                    recipe={
                        "neem_oil": "2-3 tsp",
                        "liquid_soap": "1 tsp",
                        "water": "1 quart"
                    },
                    application="Spray every 7-10 days.",
                    frequency="Every 7-10 days",
                    effectiveness="80-85%",
                    safety="Safe for beneficial insects"
                ),
                NaturalRemedy(
                    name="Proper Spacing",
                    type="disease",
                    target="powdery_mildew",
                    recipe={
                        "spacing": "18-24 inches between plants"
                    },
                    application="Plant with adequate spacing. Improves air circulation.",
                    frequency="At planting",
                    effectiveness="70-80%",
                    safety="100% safe",
                    prevention=True
                )
            ],
            'downy_mildew': [
                NaturalRemedy(
                    name="Copper Fungicide",
                    type="disease",
                    target="downy_mildew",
                    recipe={
                        "copper_sulfate": "Follow label instructions"
                    },
                    application="Spray every 7-14 days. Use protective equipment.",
                    frequency="Every 7-14 days",
                    effectiveness="85-90%",
                    safety="Use protective equipment, follow label"
                ),
                NaturalRemedy(
                    name="Baking Soda Spray",
                    type="disease",
                    target="downy_mildew",
                    recipe={
                        "baking_soda": "1 tsp",
                        "liquid_soap": "1 tsp",
                        "water": "1 quart"
                    },
                    application="Spray every 5-7 days.",
                    frequency="Every 5-7 days",
                    effectiveness="75-80%",
                    safety="Test on small area first"
                ),
                NaturalRemedy(
                    name="Remove Infected Leaves",
                    type="disease",
                    target="downy_mildew",
                    recipe={},
                    application="Prune and dispose of infected leaves immediately.",
                    frequency="As soon as detected",
                    effectiveness="90-95%",
                    safety="100% safe"
                )
            ],
            'rust': [
                NaturalRemedy(
                    name="Remove Infected Leaves",
                    type="disease",
                    target="rust",
                    recipe={},
                    application="Prune infected leaves immediately. Burn or bag.",
                    frequency="As soon as detected",
                    effectiveness="90-95%",
                    safety="100% safe"
                ),
                NaturalRemedy(
                    name="Neem Oil",
                    type="disease",
                    target="rust",
                    recipe={
                        "neem_oil": "2-3 tsp",
                        "liquid_soap": "1 tsp",
                        "water": "1 quart"
                    },
                    application="Spray every 7-10 days.",
                    frequency="Every 7-10 days",
                    effectiveness="80-85%",
                    safety="Safe for beneficial insects"
                ),
                NaturalRemedy(
                    name="Sulfur",
                    type="disease",
                    target="rust",
                    recipe={
                        "wettable_sulfur": "Follow label instructions"
                    },
                    application="Dust or spray. Don't use when temperature >85°F.",
                    frequency="Every 7-10 days",
                    effectiveness="85-90%",
                    safety="Don't use in hot weather"
                )
            ],
            'black_spot': [
                NaturalRemedy(
                    name="Baking Soda Spray",
                    type="disease",
                    target="black_spot",
                    recipe={
                        "baking_soda": "1 tsp",
                        "liquid_soap": "1 tsp",
                        "water": "1 quart"
                    },
                    application="Spray every 7-10 days.",
                    frequency="Every 7-10 days",
                    effectiveness="80-85%",
                    safety="Test on small area first"
                ),
                NaturalRemedy(
                    name="Remove Infected Leaves",
                    type="disease",
                    target="black_spot",
                    recipe={},
                    application="Prune and dispose immediately. Don't compost.",
                    frequency="As soon as detected",
                    effectiveness="90-95%",
                    safety="100% safe"
                ),
                NaturalRemedy(
                    name="Water at Base",
                    type="disease",
                    target="black_spot",
                    recipe={},
                    application="Water at base of plants. Avoid wetting leaves.",
                    frequency="Always",
                    effectiveness="70-80%",
                    safety="100% safe",
                    prevention=True
                )
            ]
        }
        
        # Save default database
        self._save_remedies(remedies)
        return remedies
    
    def _load_beneficial_insects(self) -> List[BeneficialInsect]:
        """Load beneficial insects database."""
        return [
            BeneficialInsect(
                name="Ladybugs",
                scientific_name="Coccinellidae",
                targets=["aphids", "scale", "mealybugs", "mites"],
                release_rate="1,500-2,000 per acre",
                best_time="Early morning or evening",
                effectiveness="80-90% reduction in aphids"
            ),
            BeneficialInsect(
                name="Lacewings",
                scientific_name="Chrysopidae",
                targets=["aphids", "thrips", "mites", "mealybugs", "whiteflies"],
                release_rate="1,000-2,000 per acre",
                best_time="Early morning or evening",
                effectiveness="70-85% reduction"
            ),
            BeneficialInsect(
                name="Trichogramma Wasps",
                scientific_name="Trichogrammatidae",
                targets=["caterpillar eggs", "moth eggs"],
                release_rate="5,000-10,000 per acre",
                best_time="Early morning",
                effectiveness="80-95% reduction"
            ),
            BeneficialInsect(
                name="Encarsia formosa",
                scientific_name="Encarsia formosa",
                targets=["whiteflies"],
                release_rate="1,000-5,000 per acre",
                best_time="Early morning",
                effectiveness="80-95% reduction"
            ),
            BeneficialInsect(
                name="Phytoseiulus persimilis",
                scientific_name="Phytoseiulus persimilis",
                targets=["spider mites"],
                release_rate="1,000-2,000 per acre",
                best_time="Early morning",
                effectiveness="85-95% reduction"
            ),
            BeneficialInsect(
                name="Minute Pirate Bug",
                scientific_name="Orius insidiosus",
                targets=["thrips", "mites", "aphids", "whiteflies"],
                release_rate="1,000-2,000 per acre",
                best_time="Early morning",
                effectiveness="80-90% reduction in thrips"
            )
        ]
    
    def _save_remedies(self, remedies: Dict[str, List[NaturalRemedy]]):
        """Save remedies to file."""
        try:
            data = {}
            for target, remedy_list in remedies.items():
                data[target] = [asdict(r) for r in remedy_list]
            
            with open(self.remedies_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[WARNING] Could not save remedies: {e}")
    
    def get_remedies(self, pest_or_disease: str) -> List[NaturalRemedy]:
        """Get remedies for specific pest or disease."""
        return self.remedies.get(pest_or_disease.lower(), [])
    
    def get_all_remedies(self) -> Dict[str, List[NaturalRemedy]]:
        """Get all remedies."""
        return self.remedies
    
    def get_beneficial_insects(self, target_pest: Optional[str] = None) -> List[BeneficialInsect]:
        """Get beneficial insects, optionally filtered by target pest."""
        if target_pest:
            return [bi for bi in self.beneficial_insects if target_pest.lower() in [t.lower() for t in bi.targets]]
        return self.beneficial_insects
    
    def search_remedies(self, query: str) -> List[NaturalRemedy]:
        """Search remedies by name or target."""
        query_lower = query.lower()
        results = []
        
        for target, remedy_list in self.remedies.items():
            if query_lower in target:
                results.extend(remedy_list)
            for remedy in remedy_list:
                if query_lower in remedy.name.lower():
                    results.append(remedy)
        
        return results

def main():
    """Test natural remedies database."""
    print("=" * 60)
    print("NATURAL REMEDIES DATABASE - TEST")
    print("=" * 60)
    
    db = NaturalRemediesDatabase()
    
    # Test getting remedies
    print("\n[1] Remedies for aphids:")
    aphid_remedies = db.get_remedies("aphids")
    for i, remedy in enumerate(aphid_remedies, 1):
        print(f"  {i}. {remedy.name} - {remedy.effectiveness}")
    
    # Test beneficial insects
    print("\n[2] Beneficial insects for aphids:")
    beneficial = db.get_beneficial_insects("aphids")
    for bi in beneficial:
        print(f"  - {bi.name} ({bi.scientific_name})")
        print(f"    Targets: {', '.join(bi.targets)}")
        print(f"    Release: {bi.release_rate}")
    
    # Test search
    print("\n[3] Search for 'neem':")
    neem_remedies = db.search_remedies("neem")
    for remedy in neem_remedies[:3]:
        print(f"  - {remedy.name} for {remedy.target}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)
