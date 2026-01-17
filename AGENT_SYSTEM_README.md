# Omega Agent Learning System

## Overview

Omega now has a **multi-agent learning system** that helps process the learning curve and improve continuously. The system consists of specialized agents that work together to analyze conversations, voice patterns, and language quality.

## Agent Council

The Agent Council consists of 5 specialized learning agents:

1. **Voice Pattern Analyst** (`voice_analyst`)
   - Expertise: Voice, audio, spectral analysis
   - Analyzes voice patterns and characteristics

2. **Language Quality Expert** (`language_expert`)
   - Expertise: Language, vocabulary, coherence
   - Analyzes language quality and coherence

3. **Conversation Flow Coach** (`conversation_coach`)
   - Expertise: Conversation, engagement, flow
   - Analyzes conversation flow and engagement

4. **Improvement Strategist** (`improvement_strategist`)
   - Expertise: Improvement, optimization, strategy
   - Generates improvement recommendations

5. **Learning Coordinator** (`learning_coordinator`)
   - Expertise: Coordination, integration, synthesis
   - Synthesizes findings from all agents

## How It Works

### Agent States

- **Hibernating**: Agent is inactive, waiting to be woken
- **Active**: Agent is awake and ready to process tasks
- **Processing**: Agent is currently working on a task
- **Learning**: Agent has processed and learned from data

### Learning Process

1. **Wake Agents**: Agents are woken from hibernation when Omega starts
2. **Queue Tasks**: Conversation data is queued for agent processing
3. **Parallel Processing**: Multiple agents process tasks simultaneously
4. **Communication**: Agents communicate findings with each other
5. **Synthesis**: Learning Coordinator synthesizes all findings
6. **Recommendations**: Prioritized recommendations are generated based on agent consensus

### Integration with Omega

The agent system is integrated into `hands_free_omega_optimized.py`:

- Agents wake automatically when Omega starts
- Every conversation turn is sent to agents for learning
- Agents process in the background (non-blocking)
- Agent insights are displayed during improvement cycles
- Recommendations are prioritized by agent agreement

## Usage

### Wake Agents Manually

```bash
python omega_agent_council.py
```text

Or use the batch script:
```bash
WAKE_AGENTS.bat
```text

### View Agent Status

```python
from omega_agent_council import agent_council

status = agent_council.get_agent_status()
print(f"Active agents: {status['active_agents']}/{status['total_agents']}")
```text

### Process Learning Tasks

```python
from omega_learning_swarm import learning_swarm

conversation_data = {
    'audio_file': 'conversation.wav',
    'emotion': 'neutral',
    'user_text': 'Hello',
    'omega_response': 'Hi there!',
    'history': [],
    'turn_count': 1
}

insight = await learning_swarm.process_conversation_learning(conversation_data)
```text

## Files

- `omega_agent_council.py`: Core agent council and individual agent classes
- `omega_learning_swarm.py`: Swarm intelligence coordinator
- `omega_agents/`: Directory for agent state and communication files
  - `agent_states.json`: Persistent agent states
  - `learning_queue.json`: Queued learning tasks
  - `agent_messages.json`: Inter-agent communication log

## Agent Communication

Agents communicate with each other through the Learning Coordinator:

1. Each agent processes its specialized task
2. Agents send findings to the Learning Coordinator
3. Coordinator synthesizes and prioritizes recommendations
4. Consensus is calculated based on agent agreement

## Future Enhancements

- Agent specializations can be extended
- More sophisticated consensus algorithms
- Real-time learning from user feedback
- Agent-to-agent direct communication
- Dynamic agent spawning based on workload
