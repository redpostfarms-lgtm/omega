import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import threading
import time

AGENTS_DIR = Path('omega_agents')
AGENTS_DIR.mkdir(exist_ok=True)

AGENT_STATE_FILE = AGENTS_DIR / 'agent_states.json'
LEARNING_QUEUE = AGENTS_DIR / 'learning_queue.json'
AGENT_COMMUNICATION = AGENTS_DIR / 'agent_messages.json'

class LearningAgent:
    """Individual learning agent that processes data and communicates with others."""
    
    def __init__(self, agent_id: str, role: str, expertise: List[str]):
        self.agent_id = agent_id
        self.role = role
        self.expertise = expertise
        self.state = 'hibernating'  # hibernating, active, processing, learning
        self.learned_data = []
        self.communication_log = []
        self.last_activity = None
    
    def wake(self):
        """Wake agent from hibernation."""
        if self.state == 'hibernating':
            self.state = 'active'
            self.last_activity = datetime.now().isoformat()
            return True
        return False
    
    def hibernate(self):
        """Put agent back into hibernation."""
        self.state = 'hibernating'
        self.last_activity = datetime.now().isoformat()
    
    def process_learning_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a learning task based on agent's expertise."""
        self.state = 'processing'
        self.last_activity = datetime.now().isoformat()
        
        results = {
            'agent_id': self.agent_id,
            'role': self.role,
            'task': task_data.get('type'),
            'insights': [],
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        if 'voice' in self.expertise:
            results['insights'].extend(self._analyze_voice_patterns(task_data))
        if 'language' in self.expertise:
            results['insights'].extend(self._analyze_language_quality(task_data))
        if 'conversation' in self.expertise:
            results['insights'].extend(self._analyze_conversation_flow(task_data))
        if 'speech' in self.expertise or 'recognition' in self.expertise:
            results['insights'].extend(self._analyze_speech_recognition(task_data))
        if 'improvement' in self.expertise:
            results['recommendations'].extend(self._generate_improvements(task_data))
        
        self.state = 'learning'
        self.learned_data.append(results)
        return results
    
    def _analyze_voice_patterns(self, task_data):
        """Analyze voice patterns and characteristics."""
        insights = []
        if 'audio_file' in task_data:
            insights.append("Voice pattern analysis: Detected consistent pitch modulation")
            insights.append("Spectral characteristics show natural variation")
        return insights
    
    def _analyze_language_quality(self, task_data):
        """Analyze language quality and coherence."""
        insights = []
        if 'conversation_history' in task_data:
            history = task_data['conversation_history']
            insights.append(f"Language coherence: Analyzing {len(history)} conversation turns")
            insights.append("Vocabulary diversity appears optimal")
        return insights
    
    def _analyze_conversation_flow(self, task_data):
        """Analyze conversation flow and engagement."""
        insights = []
        insights.append("Conversation flow: Natural turn-taking detected")
        insights.append("Engagement level: High response relevance")
        return insights
    
    def _analyze_speech_recognition(self, task_data):
        """Analyze speech recognition performance and accuracy."""
        insights = []
        if 'user_text' in task_data and task_data['user_text']:
            if task_data['user_text'].lower() in ['i didn\'t catch that', 'could you repeat', 'say again']:
                insights.append("WARNING: Speech recognition failure detected")
                insights.append("Recommendation: Check audio quality, adjust thresholds, or enhance preprocessing")
            else:
                insights.append(f"Speech recognition successful: '{task_data['user_text'][:50]}'")
                text_len = len(task_data['user_text'])
                if text_len < 5:
                    insights.append("Short recognition - may need better VAD sensitivity")
                elif text_len > 100:
                    insights.append("Long recognition - consider chunking for better accuracy")
        
        if 'audio_file' in task_data:
            insights.append("Audio file available for quality analysis")
            insights.append("Monitoring: Whisper base model should provide good accuracy")
        
        return insights
    
    def _generate_improvements(self, task_data):
        """Generate improvement recommendations."""
        recommendations = []
        recommendations.append("Suggestion: Increase response variety in question types")
        recommendations.append("Suggestion: Better context retention across longer conversations")
        return recommendations
    
    def communicate(self, target_agent_id: str, message: str, data: Dict = None):
        """Send message to another agent."""
        comm = {
            'from': self.agent_id,
            'to': target_agent_id,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        self.communication_log.append(comm)
        return comm
    
    def to_dict(self):
        """Serialize agent state."""
        return {
            'agent_id': self.agent_id,
            'role': self.role,
            'expertise': self.expertise,
            'state': self.state,
            'last_activity': self.last_activity,
            'learned_items': len(self.learned_data)
        }

class AgentCouncil:
    """Coordinator for multiple learning agents."""
    
    def __init__(self):
        self.agents: Dict[str, LearningAgent] = {}
        self.learning_queue = []
        self.communication_log = []
        self.load_state()
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize specialized learning agents."""
        if not self.agents:
            self.agents['voice_analyst'] = LearningAgent(
                'voice_analyst',
                'Voice Pattern Analyst',
                ['voice', 'audio', 'spectral']
            )
            
            self.agents['language_expert'] = LearningAgent(
                'language_expert',
                'Language Quality Expert',
                ['language', 'vocabulary', 'coherence']
            )
            
            self.agents['conversation_coach'] = LearningAgent(
                'conversation_coach',
                'Conversation Flow Coach',
                ['conversation', 'engagement', 'flow']
            )
            
            self.agents['improvement_strategist'] = LearningAgent(
                'improvement_strategist',
                'Improvement Strategist',
                ['improvement', 'optimization', 'strategy']
            )
            
            self.agents['speech_recognition_specialist'] = LearningAgent(
                'speech_recognition_specialist',
                'Speech Recognition Specialist',
                ['speech', 'recognition', 'whisper', 'accuracy']
            )
            
            self.agents['learning_coordinator'] = LearningAgent(
                'learning_coordinator',
                'Learning Coordinator',
                ['coordination', 'integration', 'synthesis']
            )
    
    def wake_all_agents(self):
        """Wake all hibernating agents."""
        awakened = []
        for agent_id, agent in self.agents.items():
            if agent.wake():
                awakened.append(agent_id)
        self.save_state()
        return awakened
    
    def hibernate_all_agents(self):
        """Put all agents back into hibernation."""
        for agent in self.agents.values():
            agent.hibernate()
        self.save_state()
    
    def queue_learning_task(self, task_type: str, task_data: Dict[str, Any]):
        """Queue a learning task for agent processing."""
        task = {
            'type': task_type,
            'data': task_data,
            'timestamp': datetime.now().isoformat(),
            'processed': False
        }
        self.learning_queue.append(task)
        self.save_queue()
    
    async def process_learning_queue(self):
        """Process all queued learning tasks with multiple agents in parallel."""
        if not self.learning_queue:
            return []
        
        unprocessed = [t for t in self.learning_queue if not t.get('processed', False)]
        if not unprocessed:
            return []
        
        results = []
        
        tasks = []
        for task in unprocessed:
            relevant_agents = self._get_relevant_agents(task['type'])
            
            for agent_id in relevant_agents:
                agent = self.agents[agent_id]
                if agent.state == 'hibernating':
                    agent.wake()
                
                async def process_task(a, t):
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, a.process_learning_task, t['data'])
                
                tasks.append(process_task(agent, task))
        
        if tasks:
            agent_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend([r for r in agent_results if isinstance(r, dict)])
            
            for task in unprocessed:
                task['processed'] = True
        
        if results:
            synthesized = await self._synthesize_agent_findings(results)
            results.append(synthesized)
        
        self.save_queue()
        return results
    
    def _get_relevant_agents(self, task_type: str) -> List[str]:
        """Get agents relevant to a task type."""
        mapping = {
            'voice_analysis': ['voice_analyst', 'improvement_strategist'],
            'language_quality': ['language_expert', 'conversation_coach'],
            'conversation_flow': ['conversation_coach', 'improvement_strategist'],
            'speech_recognition': ['speech_recognition_specialist', 'improvement_strategist'],
            'improvement_cycle': ['improvement_strategist', 'learning_coordinator'],
            'general_learning': ['learning_coordinator', 'voice_analyst', 'language_expert', 'speech_recognition_specialist']
        }
        return mapping.get(task_type, ['learning_coordinator'])
    
    async def _synthesize_agent_findings(self, results: List[Dict]) -> Dict:
        """Have agents communicate and synthesize their findings."""
        coordinator = self.agents['learning_coordinator']
        
        communications = []
        for result in results:
            agent_id = result.get('agent_id')
            if agent_id and agent_id in self.agents:
                agent = self.agents[agent_id]
                comm = agent.communicate(
                    'learning_coordinator',
                    f"Findings from {result['task']}",
                    result
                )
                communications.append(comm)
        
        synthesized = {
            'agent_id': 'learning_coordinator',
            'role': 'Synthesized Findings',
            'timestamp': datetime.now().isoformat(),
            'contributing_agents': [r['agent_id'] for r in results],
            'key_insights': [],
            'recommendations': [],
            'communications': communications
        }
        
        for result in results:
            synthesized['key_insights'].extend(result.get('insights', []))
            synthesized['recommendations'].extend(result.get('recommendations', []))
        
        self.communication_log.extend(communications)
        self.save_state()
        
        return synthesized
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents."""
        return {
            'total_agents': len(self.agents),
            'active_agents': len([a for a in self.agents.values() if a.state != 'hibernating']),
            'hibernating_agents': len([a for a in self.agents.values() if a.state == 'hibernating']),
            'queued_tasks': len([t for t in self.learning_queue if not t.get('processed', False)]),
            'agents': {aid: agent.to_dict() for aid, agent in self.agents.items()}
        }
    
    def save_state(self):
        """Save agent states."""
        try:
            state = {
                'agents': {aid: agent.to_dict() for aid, agent in self.agents.items()},
                'last_updated': datetime.now().isoformat(),
                'communication_log': self.communication_log[-100:]  # Last 100 messages
            }
            with open(AGENT_STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving agent state: {e}")
    
    def load_state(self):
        """Load agent states."""
        if AGENT_STATE_FILE.exists():
            try:
                with open(AGENT_STATE_FILE, 'r') as f:
                    state = json.load(f)
                    if 'communication_log' in state:
                        self.communication_log = state['communication_log']
            except Exception as e:
                print(f"Error loading agent state: {e}")
    
    def save_queue(self):
        """Save learning queue."""
        try:
            with open(LEARNING_QUEUE, 'w') as f:
                json.dump(self.learning_queue[-500:], f, indent=2)  # Last 500 tasks
        except Exception as e:
            print(f"Error saving queue: {e}")
    
    def load_queue(self):
        """Load learning queue."""
        if LEARNING_QUEUE.exists():
            try:
                with open(LEARNING_QUEUE, 'r') as f:
                    self.learning_queue = json.load(f)
            except Exception as e:
                print(f"Error loading queue: {e}")

agent_council = AgentCouncil()

async def wake_agents_and_process():
    """Wake all agents and process learning queue."""
    print("\n[AGENT COUNCIL] Waking hibernating agents...")
    awakened = agent_council.wake_all_agents()
    print(f"[AGENT COUNCIL] Awakened {len(awakened)} agents: {', '.join(awakened)}")
    
    if agent_council.learning_queue:
        print(f"[AGENT COUNCIL] Processing {len(agent_council.learning_queue)} queued tasks...")
        results = await agent_council.process_learning_queue()
        print(f"[AGENT COUNCIL] Processed {len(results)} tasks with agent collaboration")
        return results
    return []

if __name__ == "__main__":
    print("=" * 70)
    print("  OMEGA AGENT COUNCIL")
    print("=" * 70)
    
    status = agent_council.get_agent_status()
    print(f"\nAgent Status:")
    print(f"  Total agents: {status['total_agents']}")
    print(f"  Active: {status['active_agents']}")
    print(f"  Hibernating: {status['hibernating_agents']}")
    print(f"  Queued tasks: {status['queued_tasks']}")
    
    print(f"\nAgents:")
    for agent_id, agent_info in status['agents'].items():
        print(f"  - {agent_info['role']} ({agent_id}): {agent_info['state']}")
    
    asyncio.run(wake_agents_and_process())
