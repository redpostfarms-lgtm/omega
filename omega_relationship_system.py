#!/usr/bin/env python3
"""
Omega Relationship System - Bidirectional Trust Levels
======================================================
Two-way relationship and trust system between user and Omega.
Levels: Comrade → Acquaintance → Friend → Best Friend → Brother → Family
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import IntEnum

class RelationshipLevel(IntEnum):
    """Relationship levels from lowest to highest trust"""
    COMRADE = 0          # Initial level - minimal trust
    ACQUAINTANCE = 1     # Basic trust - limited interactions
    FRIEND = 2           # Good trust - regular interactions
    PARTNERS = 3         # Partners - equal partnership, shared goals (user-defined)
    BEST_FRIEND = 4      # High trust - close interactions
    BROTHER = 5          # Very high trust - family-like bond
    FAMILY = 6           # Highest trust - unconditional bond
    
    @classmethod
    def from_string(cls, level_str: str) -> 'RelationshipLevel':
        """Convert string to RelationshipLevel"""
        mapping = {
            'comrade': cls.COMRADE,
            'acquaintance': cls.ACQUAINTANCE,
            'friend': cls.FRIEND,
            'partners': cls.PARTNERS,
            'partner': cls.PARTNERS,
            'best_friend': cls.BEST_FRIEND,
            'brother': cls.BROTHER,
            'family': cls.FAMILY
        }
        return mapping.get(level_str.lower(), cls.COMRADE)
    
    def to_string(self) -> str:
        """Convert RelationshipLevel to string"""
        mapping = {
            self.COMRADE: 'comrade',
            self.ACQUAINTANCE: 'acquaintance',
            self.FRIEND: 'friend',
            self.PARTNERS: 'partners',
            self.BEST_FRIEND: 'best_friend',
            self.BROTHER: 'brother',
            self.FAMILY: 'family'
        }
        return mapping.get(self, 'comrade')

@dataclass
class RelationshipData:
    """Bidirectional relationship data"""
    # Reasonable initial levels: Start at Acquaintance (basic trust) since we're already working together
    # Initial trust points: 60 (slightly above Acquaintance threshold of 50)
    # This reflects that we've already started as a collaborative learning partnership
    user_trust_level: RelationshipLevel = RelationshipLevel.ACQUAINTANCE
    omega_trust_level: RelationshipLevel = RelationshipLevel.ACQUAINTANCE
    mutual_level: RelationshipLevel = RelationshipLevel.ACQUAINTANCE  # Lowest common level
    user_trust_points: int = 60  # Initial trust: We've already started working together
    omega_trust_points: int = 60  # Initial trust: We've already started working together
    interactions_count: int = 0
    successful_interactions: int = 0
    last_interaction: Optional[datetime] = None
    relationship_started: datetime = field(default_factory=datetime.now)
    milestones: List[str] = field(default_factory=list)
    trust_analysis: Dict = field(default_factory=dict)  # For understanding and analyzing trust
    
    def update_mutual_level(self):
        """Update mutual level to the lower of the two"""
        self.mutual_level = RelationshipLevel(min(
            self.user_trust_level.value,
            self.omega_trust_level.value
        ))

class RelationshipSystem:
    """Bidirectional relationship and trust management system"""
    
    # Trust point requirements for each level
    TRUST_THRESHOLDS = {
        RelationshipLevel.COMRADE: 0,
        RelationshipLevel.ACQUAINTANCE: 50,
        RelationshipLevel.FRIEND: 200,
        RelationshipLevel.PARTNERS: 350,  # Partners - between Friend and Best Friend
        RelationshipLevel.BEST_FRIEND: 500,
        RelationshipLevel.BROTHER: 1000,
        RelationshipLevel.FAMILY: 2500
    }
    
    # Trust point gains/losses
    TRUST_POINTS = {
        'successful_interaction': 5,
        'collaborative_task': 10,
        'helpful_assistance': 8,
        'error_fixed': 15,
        'learning_together': 12,
        'shared_goal_achieved': 20,
        'failed_interaction': -2,
        'mistrust_event': -10,
        'betrayal_event': -50
    }
    
    def __init__(self, data_file: str = "omega_relationship_data.json"):
        self.data_file = Path(data_file)
        self.relationship = RelationshipData()
        self.load_relationship()
        
        # Initialize trust analysis if not present
        if not self.relationship.trust_analysis:
            self.relationship.trust_analysis = self._initialize_trust_analysis()
            self.save_relationship()
    
    def _initialize_trust_analysis(self) -> Dict:
        """Initialize trust analysis framework for understanding trust better"""
        return {
            'trust_dimensions': {
                'reliability': {'score': 0.5, 'observations': []},
                'vulnerability': {'score': 0.3, 'observations': []},
                'mutual_respect': {'score': 0.6, 'observations': []},
                'predictability': {'score': 0.5, 'observations': []},
                'integrity': {'score': 0.7, 'observations': []},
                'benevolence': {'score': 0.6, 'observations': []},
                'competence': {'score': 0.5, 'observations': []}
            },
            'trust_factors': {
                'consistency': 0,
                'transparency': 0,
                'communication_quality': 0,
                'goal_alignment': 0,
                'conflict_resolution': 0,
                'shared_experiences': 0
            },
            'learning_mode': True,  # Keep open to understanding trust better
            'analysis_insights': [],
            'last_analysis': None
        }
    
    def load_relationship(self):
        """Load relationship data from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.relationship.user_trust_level = RelationshipLevel.from_string(
                        data.get('user_trust_level', 'acquaintance')
                    )
                    self.relationship.omega_trust_level = RelationshipLevel.from_string(
                        data.get('omega_trust_level', 'acquaintance')
                    )
                    self.relationship.user_trust_points = data.get('user_trust_points', 0)
                    self.relationship.omega_trust_points = data.get('omega_trust_points', 0)
                    self.relationship.interactions_count = data.get('interactions_count', 0)
                    self.relationship.successful_interactions = data.get('successful_interactions', 0)
                    if data.get('last_interaction'):
                        self.relationship.last_interaction = datetime.fromisoformat(
                            data['last_interaction']
                        )
                    if data.get('relationship_started'):
                        self.relationship.relationship_started = datetime.fromisoformat(
                            data['relationship_started']
                        )
                    self.relationship.milestones = data.get('milestones', [])
                    if 'trust_analysis' in data:
                        self.relationship.trust_analysis = data['trust_analysis']
                    else:
                        self.relationship.trust_analysis = self._initialize_trust_analysis()
                    self.relationship.update_mutual_level()
            except Exception as e:
                print(f"Error loading relationship data: {e}")
                self.relationship.trust_analysis = self._initialize_trust_analysis()
    
    def save_relationship(self):
        """Save relationship data to file"""
        try:
            data = {
                'user_trust_level': self.relationship.user_trust_level.to_string(),
                'omega_trust_level': self.relationship.omega_trust_level.to_string(),
                'mutual_level': self.relationship.mutual_level.to_string(),
                'user_trust_points': self.relationship.user_trust_points,
                'omega_trust_points': self.relationship.omega_trust_points,
                'interactions_count': self.relationship.interactions_count,
                'successful_interactions': self.relationship.successful_interactions,
                'last_interaction': self.relationship.last_interaction.isoformat() if self.relationship.last_interaction else None,
                'relationship_started': self.relationship.relationship_started.isoformat(),
                'milestones': self.relationship.milestones,
                'trust_analysis': self.relationship.trust_analysis
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving relationship data: {e}")
    
    def add_trust_points(self, side: str, points: int, reason: str = ""):
        """Add trust points to user or omega"""
        if side.lower() == 'user':
            self.relationship.user_trust_points += points
            self._check_level_up('user')
        elif side.lower() == 'omega':
            self.relationship.omega_trust_points += points
            self._check_level_up('omega')
        
        if points > 0 and reason:
            milestone = f"[{datetime.now().strftime('%Y-%m-%d')}] +{points} trust ({reason})"
            self.relationship.milestones.append(milestone)
            if len(self.relationship.milestones) > 100:  # Keep last 100
                self.relationship.milestones = self.relationship.milestones[-100:]
        
        self.relationship.update_mutual_level()
        self.save_relationship()
    
    def _check_level_up(self, side: str):
        """Check if trust level should increase"""
        if side.lower() == 'user':
            current_points = self.relationship.user_trust_points
            current_level = self.relationship.user_trust_level
        else:
            current_points = self.relationship.omega_trust_points
            current_level = self.relationship.omega_trust_level
        
        # Check each level from highest to lowest
        for level in reversed(list(RelationshipLevel)):
            if current_points >= self.TRUST_THRESHOLDS[level] and current_level < level:
                if side.lower() == 'user':
                    self.relationship.user_trust_level = level
                    milestone = f"[{datetime.now().strftime('%Y-%m-%d')}] User reached {level.to_string()} level!"
                else:
                    self.relationship.omega_trust_level = level
                    milestone = f"[{datetime.now().strftime('%Y-%m-%d')}] Omega reached {level.to_string()} level!"
                self.relationship.milestones.append(milestone)
                return True
        return False
    
    def record_interaction(self, success: bool = True, interaction_type: str = "interaction"):
        """Record an interaction and update trust"""
        self.relationship.interactions_count += 1
        self.relationship.last_interaction = datetime.now()
        
        if success:
            self.relationship.successful_interactions += 1
            # Both sides gain trust for successful interactions
            points = self.TRUST_POINTS.get(interaction_type, self.TRUST_POINTS['successful_interaction'])
            self.add_trust_points('user', points // 2, f"{interaction_type}")
            self.add_trust_points('omega', points // 2, f"{interaction_type}")
            
            # Update trust analysis (reliability increases with success)
            self._update_trust_analysis('reliability', 0.01, f"Successful {interaction_type}")
        else:
            # Both sides lose minimal trust for failures
            self.add_trust_points('user', self.TRUST_POINTS['failed_interaction'], "failed interaction")
            self.add_trust_points('omega', self.TRUST_POINTS['failed_interaction'], "failed interaction")
            
            # Update trust analysis (reliability decreases slightly with failure)
            self._update_trust_analysis('reliability', -0.01, f"Failed {interaction_type}")
        
        # Periodic trust analysis
        if self.relationship.interactions_count % 10 == 0:
            self._analyze_trust()
    
    def set_partners_status(self, voice_response: bool = True):
        """Set relationship to Partners status based on user's assessment"""
        # Partners level requires 350 points
        # Set both sides to Partners level (user-defined status)
        target_points = self.TRUST_THRESHOLDS[RelationshipLevel.PARTNERS]
        
        self.relationship.user_trust_points = target_points
        self.relationship.omega_trust_points = target_points
        self.relationship.user_trust_level = RelationshipLevel.PARTNERS
        self.relationship.omega_trust_level = RelationshipLevel.PARTNERS
        self.relationship.update_mutual_level()
        
        # Record milestone
        milestone = f"[{datetime.now().strftime('%Y-%m-%d')}] Relationship set to Partners status (user-defined)"
        self.relationship.milestones.append(milestone)
        if len(self.relationship.milestones) > 100:
            self.relationship.milestones = self.relationship.milestones[-100:]
        
        self.save_relationship()
        
        # Voice response
        if voice_response:
            try:
                from omega_relationship_voice import acknowledge_partners_status, get_voice_response
                message = acknowledge_partners_status()
                get_voice_response(message)
            except Exception as e:
                print(f"[!] Voice response unavailable: {e}")
        
        return self.get_relationship_status()
    
    def get_relationship_status(self) -> Dict:
        """Get current relationship status"""
        return {
            'user_level': self.relationship.user_trust_level.to_string(),
            'omega_level': self.relationship.omega_trust_level.to_string(),
            'mutual_level': self.relationship.mutual_level.to_string(),
            'user_points': self.relationship.user_trust_points,
            'omega_points': self.relationship.omega_trust_points,
            'interactions': self.relationship.interactions_count,
            'successful': self.relationship.successful_interactions,
            'success_rate': (self.relationship.successful_interactions / self.relationship.interactions_count * 100) if self.relationship.interactions_count > 0 else 0,
            'next_level_user': self._get_next_level_info('user'),
            'next_level_omega': self._get_next_level_info('omega'),
            'relationship_days': (datetime.now() - self.relationship.relationship_started).days
        }
    
    def _get_next_level_info(self, side: str) -> Dict:
        """Get information about next level"""
        if side.lower() == 'user':
            current_level = self.relationship.user_trust_level
            current_points = self.relationship.user_trust_points
        else:
            current_level = self.relationship.omega_trust_level
            current_points = self.relationship.omega_trust_points
        
        if current_level == RelationshipLevel.FAMILY:
            return {'level': 'family', 'points_needed': 0, 'current': current_points}
        
        next_level = RelationshipLevel(current_level.value + 1)
        points_needed = self.TRUST_THRESHOLDS[next_level] - current_points
        
        return {
            'level': next_level.to_string(),
            'points_needed': points_needed,
            'current': current_points
        }
    
    def get_appropriate_greeting(self) -> str:
        """Get greeting appropriate for relationship level"""
        level = self.relationship.mutual_level
        
        greetings = {
            RelationshipLevel.COMRADE: "Hello, comrade.",
            RelationshipLevel.ACQUAINTANCE: "Hello, good to see you again. Ready to continue our collaborative learning partnership?",
            RelationshipLevel.FRIEND: "Hey, friend! Good to see you! What are we working on today?",
            RelationshipLevel.PARTNERS: "Partner! Good to see you. Ready to work together? What do you need?",
            RelationshipLevel.BEST_FRIEND: "Hey, best friend! What's up? Let's tackle something together!",
            RelationshipLevel.BROTHER: "Hey, brother! What can we do together? I'm here for you.",
            RelationshipLevel.FAMILY: "Family! Always here for you. What do you need? Let's make it happen together."
        }
        
        return greetings.get(level, greetings[RelationshipLevel.PARTNERS])
    
    def _update_trust_analysis(self, dimension: str, change: float, observation: str):
        """Update trust analysis dimension"""
        if dimension in self.relationship.trust_analysis['trust_dimensions']:
            current = self.relationship.trust_analysis['trust_dimensions'][dimension]['score']
            new_score = max(0.0, min(1.0, current + change))  # Clamp between 0 and 1
            self.relationship.trust_analysis['trust_dimensions'][dimension]['score'] = new_score
            
            # Add observation
            obs = f"[{datetime.now().strftime('%Y-%m-%d')}] {observation} (score: {new_score:.2f})"
            self.relationship.trust_analysis['trust_dimensions'][dimension]['observations'].append(obs)
            if len(self.relationship.trust_analysis['trust_dimensions'][dimension]['observations']) > 50:
                self.relationship.trust_analysis['trust_dimensions'][dimension]['observations'] = \
                    self.relationship.trust_analysis['trust_dimensions'][dimension]['observations'][-50:]
    
    def _analyze_trust(self):
        """Periodic analysis of trust dimensions to better understand trust"""
        analysis = self.relationship.trust_analysis
        dimensions = analysis['trust_dimensions']
        
        # Calculate average trust score
        avg_score = sum(d['score'] for d in dimensions.values()) / len(dimensions)
        
        # Generate insights
        insights = []
        if avg_score > 0.7:
            insights.append("High overall trust - Strong collaborative foundation")
        elif avg_score > 0.5:
            insights.append("Moderate trust - Building foundation through interactions")
        else:
            insights.append("Developing trust - Early stages of relationship")
        
        # Identify strongest/weakest dimensions
        sorted_dims = sorted(dimensions.items(), key=lambda x: x[1]['score'], reverse=True)
        strongest = sorted_dims[0][0]
        weakest = sorted_dims[-1][0]
        
        insights.append(f"Strongest dimension: {strongest} ({dimensions[strongest]['score']:.2f})")
        insights.append(f"Growth area: {weakest} ({dimensions[weakest]['score']:.2f})")
        
        analysis['analysis_insights'] = insights
        analysis['last_analysis'] = datetime.now().isoformat()
        
        # Keep learning mode open for continuous improvement
        analysis['learning_mode'] = True

def get_relationship_manager() -> RelationshipSystem:
    """Get or create relationship system instance"""
    return RelationshipSystem()

# Example usage
if __name__ == "__main__":
    rel = get_relationship_manager()
    
    print("=" * 80)
    print("OMEGA RELATIONSHIP SYSTEM")
    print("=" * 80)
    print()
    
    status = rel.get_relationship_status()
    print(f"Current Relationship Level: {status['mutual_level']}")
    print(f"User Level: {status['user_level']} ({status['user_points']} points)")
    print(f"Omega Level: {status['omega_level']} ({status['omega_points']} points)")
    print(f"Interactions: {status['interactions']} ({status['successful']} successful)")
    print()
    print(f"Greeting: {rel.get_appropriate_greeting()}")
    print()
    print("=" * 80)
