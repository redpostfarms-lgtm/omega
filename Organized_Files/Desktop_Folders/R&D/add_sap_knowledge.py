"""
Add SAP Knowledge to Knowledge Base
Structured knowledge entry from Facebook Reel about Free SAP Courses

Red Post Farms, LLC - 2026
"""

import json
import sys
from pathlib import Path

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
GATE = BRAIN_DIR / "The Gatekeeper"
ARCHIVED = BRAIN_DIR / "Archived"

# SAP Knowledge Entry
sap_knowledge = {
    'path': 'reference/sap_career_development',
    'text': '''SAP (System Applications and Products in Data Processing)
A leading Enterprise Resource Planning (ERP) software used by top organizations for optimizing business operations, analytics, finance, HR, supply chain, and data analytics.

BENEFITS OF LEARNING SAP:
- High Earning Potential: SAP-certified professionals are among the highest-paid in tech and business
- Diverse Applications: Applicable in sectors like finance, HR, supply chain, and data analytics
- Career Growth: Opens doors to roles in IT, finance, supply chain management, and more
- Certifications: Validate expertise and stand out in job markets
- Industry Demand: Essential for large-scale enterprises worldwide

RESUME BOOST:
- Demonstrates commitment to enterprise solutions and modern technologies
- Validates skills with official SAP credentials

COURSE FEATURES:
- Certification: Earn a certificate upon completion
- Flexible Learning: Self-paced, suitable for all levels
- Practical Knowledge: Includes hands-on labs and real-world scenarios

APPLICATION FOR RED POST FARMS:
- Useful for learning SAP tools for inventory management
- Supply chain optimization
- Financial tracking and reporting
- HR management systems

Source: Facebook Reel - Free SAP Courses (tricky_world23)
Tags: SAP, ERP, career, IT, education, certification, business, inventory, supply-chain, finance, HR''',
    'tags': ['SAP', 'ERP', 'career', 'IT', 'education', 'certification', 'business', 'inventory', 'supply-chain', 'finance', 'HR', 'resume', 'skill-development', 'enterprise'],
    'category': 'career_development',
    'source': 'Facebook Reel - tricky_world23',
    'date_added': '2026-01-04'
}

# Try to add to WorldMemory system
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from WorldMemory import WorldMemory
    
    wm = WorldMemory()
    
    # Add SAP knowledge as a fact
    sap_text = f"SAP Career Development Knowledge: {sap_knowledge['text'][:500]}..."
    success = wm.add_fact(sap_text)
    
    if success:
        print("OK SAP knowledge added to WorldMemory")
    else:
        print("FAILED to add to WorldMemory, using local storage")
except ImportError:
    print("WorldMemory not available, using local storage")

# Add to brain_prime knowledge base
brain_file = ARCHIVED / "gatekeeper_brain.json"
if brain_file.exists():
    try:
        with open(brain_file, 'r', encoding='utf-8') as f:
            brain = json.load(f)
        
        # Add SAP knowledge to docs
        if 'knowledge' not in brain:
            brain['knowledge'] = []
        
        # Check if already exists
        existing = [d for d in brain['knowledge'] if 'sap_career_development' in d.get('path', '')]
        if not existing:
            brain['knowledge'].append(sap_knowledge)
            print("OK SAP knowledge added to brain_prime knowledge base")
        else:
            print("INFO SAP knowledge already exists in brain_prime")
        
        # Save updated brain
        with open(brain_file, 'w', encoding='utf-8') as f:
            json.dump(brain, f, indent=2, ensure_ascii=False)
        
    except Exception as e:
        print(f"FAILED to update brain_prime: {e}")
else:
    print("INFO brain_prime.json not found, creating new entry")
    brain = {
        'knowledge': [sap_knowledge],
        'templates': {},
        'voice': 'The doors of knowledge opens.',
        'role': "Knowledge base with SAP career development information"
    }
    brain_file.parent.mkdir(parents=True, exist_ok=True)
    with open(brain_file, 'w', encoding='utf-8') as f:
        json.dump(brain, f, indent=2, ensure_ascii=False)
    print("OK Created new brain_prime.json with SAP knowledge")

# Try to use knowledge_tags system if available
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from knowledge_tags import KnowledgeTags
    
    kt = KnowledgeTags()
    
    # Add tags for SAP knowledge
    doc_id = 'sap_career_development'
    tags = ['SAP', 'ERP', 'career', 'IT', 'education', 'certification', 'business', 'inventory', 'supply-chain', 'finance', 'HR']
    
    kt.add_tags(doc_id, tags)
    print(f"OK Tags added via knowledge_tags system: {', '.join(tags)}")
    
except ImportError:
    print("INFO knowledge_tags module not available, tags stored in document")

# Save standalone SAP knowledge file
sap_file = ARCHIVED / "knowledge" / "sap_career_development.json"
sap_file.parent.mkdir(parents=True, exist_ok=True)

with open(sap_file, 'w', encoding='utf-8') as f:
    json.dump(sap_knowledge, f, indent=2, ensure_ascii=False)

print(f"OK SAP knowledge saved to: {sap_file}")
print("\n" + "="*80)
print("SAP KNOWLEDGE ADDED TO KNOWLEDGE BASE")
print("="*80)
print(f"\nDocument ID: {sap_knowledge['path']}")
print(f"Tags: {', '.join(sap_knowledge['tags'])}")
print(f"Category: {sap_knowledge['category']}")
print(f"Source: {sap_knowledge['source']}")
print("\n" + "="*80)
print("Knowledge is now searchable via:")
print("  - WorldMemory query system")
print("  - brain_prime knowledge base")
print("  - knowledge_tags system")
print("  - Standalone JSON file")
print("="*80)

