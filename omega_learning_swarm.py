import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from omega_agent_council import agent_council, wake_agents_and_process

try:
    from improvement_cycle_manager import ImprovementCycleManager
    from language_improver import LanguageImprover
    from voice_security_system import voice_security
except ImportError:
    ImprovementCycleManager = None
    LanguageImprover = None
    voice_security = None

class LearningSwarm:
    """Swarm intelligence system for distributed learning across agents."""
    
    def __init__(self):
        self.cycle_manager = ImprovementCycleManager() if ImprovementCycleManager else None
        self.language_improver = LanguageImprover() if LanguageImprover else None
        self.agent_council = agent_council
        self.learning_cycles = []
        self.swarm_insights = []
    
    async def process_conversation_learning(self, conversation_data: Dict):
        """Process conversation through swarm of learning agents."""
        await wake_agents_and_process()
        
        self.agent_council.queue_learning_task('voice_analysis', {
            'audio_file': conversation_data.get('audio_file'),
            'emotion': conversation_data.get('emotion'),
        })
        
        self.agent_council.queue_learning_task('language_quality', {
            'conversation_history': conversation_data.get('history', []),
            'user_text': conversation_data.get('user_text'),
            'omega_response': conversation_data.get('omega_response'),
        })
        
        self.agent_council.queue_learning_task('conversation_flow', {
            'conversation_history': conversation_data.get('history', []),
            'turn_count': conversation_data.get('turn_count', 0),
        })
        
        self.agent_council.queue_learning_task('speech_recognition', {
            'user_text': conversation_data.get('user_text'),
            'audio_file': conversation_data.get('audio_file'),
            'recognition_success': conversation_data.get('user_text') is not None and len(conversation_data.get('user_text', '')) > 0
        })
        
        results = await self.agent_council.process_learning_queue()
        
        swarm_insight = self._synthesize_swarm_intelligence(results)
        self.swarm_insights.append(swarm_insight)
        
        return swarm_insight
    
    def _synthesize_swarm_intelligence(self, agent_results: List[Dict]) -> Dict:
        """Synthesize findings from all agents into actionable improvements."""
        if not agent_results:
            return {}
        
        all_insights = []
        all_recommendations = []
        
        for result in agent_results:
            all_insights.extend(result.get('insights', []))
            all_recommendations.extend(result.get('recommendations', []))
        
        prioritized = self._prioritize_recommendations(all_recommendations)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'contributing_agents': len(agent_results),
            'insights': all_insights[:10],  # Top 10 insights
            'prioritized_recommendations': prioritized,
            'swarm_consensus': self._calculate_consensus(all_recommendations)
        }
    
    def _prioritize_recommendations(self, recommendations: List[str]) -> List[Dict]:
        """Prioritize recommendations based on frequency and agent consensus."""
        freq = {}
        for rec in recommendations:
            freq[rec] = freq.get(rec, 0) + 1
        
        prioritized = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'recommendation': rec, 'agent_agreement': count, 'priority': 'high' if count >= 2 else 'medium'}
            for rec, count in prioritized[:5]  # Top 5
        ]
    
    def _calculate_consensus(self, recommendations: List[str]) -> str:
        """Calculate swarm consensus on improvement direction."""
        if not recommendations:
            return "No consensus yet"
        
        if len(recommendations) >= 3:
            return "High consensus: Multiple agents agree on improvements"
        elif len(recommendations) >= 2:
            return "Moderate consensus: Some agents agree"
        else:
            return "Low consensus: Exploring different directions"
    
    async def continuous_learning_loop(self):
        """Continuous learning loop with agent swarm."""
        print("\n[LEARNING SWARM] Starting continuous learning loop...")
        print("[LEARNING SWARM] Agents active and ready to learn\n")
        
        status = self.agent_council.get_agent_status()
        print(f"[LEARNING SWARM] Active agents: {status['active_agents']}/{status['total_agents']}")
        
        return self.agent_council

learning_swarm = LearningSwarm()

if __name__ == "__main__":
    print("=" * 70)
    print("  OMEGA LEARNING SWARM")
    print("=" * 70)
    asyncio.run(learning_swarm.continuous_learning_loop())
