"""
Unified Agent Framework
=======================
Base framework for all Omega agents across departments

All agents share the same core architecture and capabilities,
differentiated only by their department-specific knowledge and tools.

Core Philosophy:
- Same foundation, different specialization
- Unified communication protocol
- Shared memory and context
- Department-specific tools and knowledge
- Consistent behavior and response patterns

Like building on a steep parcel of land - the foundation must be identical
and solid, but each structure (department) has its own unique purpose.
"""

import os
import sys
import json
import time
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum

# Core Omega imports
try:
    from omega_admin_privileges import get_omega_admin
    from omega_credentials import get_credentials
    from omega_api_keys import get_api_key_manager
except ImportError:
    print("Warning: Core Omega modules not available")

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class AgentDepartment(Enum):
    """Agent department classifications"""
    CORE = "core"                      # Core system agent
    DEVELOPMENT = "development"        # Code and development
    OPERATIONS = "operations"          # System operations and DevOps
    SECURITY = "security"              # Security and access control
    DATA = "data"                      # Data analysis and management
    COMMUNICATION = "communication"    # Email, messaging, notifications
    AUTOMATION = "automation"          # Workflow automation
    MONITORING = "monitoring"          # System monitoring and health
    DOCUMENTATION = "documentation"    # Documentation and knowledge
    SUPPORT = "support"                # User support and assistance
    RESEARCH = "research"              # Research and exploration
    CREATIVE = "creative"              # Creative tasks and generation

class AgentCapability(Enum):
    """Standard agent capabilities"""
    # Communication
    TEXT_GENERATION = "text_generation"
    CONVERSATION = "conversation"
    EMAIL = "email"
    MESSAGING = "messaging"

    # System Control
    FILE_OPERATIONS = "file_operations"
    SYSTEM_COMMANDS = "system_commands"
    DESKTOP_AUTOMATION = "desktop_automation"
    BROWSER_AUTOMATION = "browser_automation"

    # Data & Analysis
    DATA_ANALYSIS = "data_analysis"
    CODE_EXECUTION = "code_execution"
    DATABASE_ACCESS = "database_access"

    # Monitoring & Logging
    SYSTEM_MONITORING = "system_monitoring"
    LOG_ANALYSIS = "log_analysis"
    METRICS_COLLECTION = "metrics_collection"

    # AI & ML
    LLM_ACCESS = "llm_access"
    VOICE_SYNTHESIS = "voice_synthesis"
    IMAGE_GENERATION = "image_generation"


@dataclass
class AgentMessage:
    """Structured inter-agent message."""
    sender: str
    recipient: str
    content: str
    timestamp: str
    metadata: Dict[str, Any]


class GatekeeperBrainAccess:
    """Shared knowledge accessor for Omega and all agents."""

    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.sources = [
            self.repo_root / "omega_memory_core.json",
            self.repo_root / "OMEGA_KNOWLEDGE_BASE.json",
            self.repo_root / "omega_memory.json",
            self.repo_root / "omega_autonomous_memory.json",
            self.repo_root / "backups/memory/knowledge_base_20260123_155929.json",
            self.repo_root / "Archived/gatekeeper_brain.json",
        ]

    def available_sources(self) -> List[str]:
        return [str(p) for p in self.sources if p.exists()]

    def _read_json(self, path: Path) -> Optional[Any]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        q = (query or "").strip().lower()
        if not q:
            return []

        hits: List[Dict[str, Any]] = []
        for source in self.sources:
            if not source.exists():
                continue
            data = self._read_json(source)
            if data is None:
                continue

            blob = json.dumps(data, ensure_ascii=False)[:2_000_000]
            lowered_blob = blob.lower()
            idx = lowered_blob.find(q)
            if idx != -1:
                start = max(0, idx - 120)
                end = min(len(lowered_blob), idx + 280)
                excerpt = blob[start:end]
                score = min(1.0, max(0.1, lowered_blob.count(q) / 10.0))
                hits.append({
                    "source": str(source),
                    "match": excerpt,
                    "score": round(score, 3),
                })
            if len(hits) >= limit:
                break
        return sorted(hits, key=lambda x: x.get("score", 0), reverse=True)[:limit]


class AgentCommunicationBus:
    """Inter-agent communication bus with optional LangChain routing."""

    def __init__(self):
        self.history: List[AgentMessage] = []
        self.channels: Dict[str, List[AgentMessage]] = {}
        self.llm = None
        if LANGCHAIN_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                self.llm = ChatOpenAI(
                    model=os.getenv("AGENT_ROUTER_MODEL", "gpt-4.1-mini"),
                    temperature=0.2,
                )
            except Exception:
                self.llm = None

    def send(self, sender: str, recipient: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> AgentMessage:
        message = AgentMessage(
            sender=sender,
            recipient=recipient,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {},
        )
        self.history.append(message)
        return message

    def broadcast(self, sender: str, channel: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> AgentMessage:
        """Broadcast a message to a shared channel (town hall/community)."""
        message = AgentMessage(
            sender=sender,
            recipient=f"channel:{channel}",
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {},
        )
        self.history.append(message)
        self.channels.setdefault(channel, []).append(message)
        return message

    def get_channel_history(self, channel: str, limit: int = 100) -> List[AgentMessage]:
        return self.channels.get(channel, [])[-limit:]

    def suggest_capability(self, request: str, capabilities: List[str]) -> Optional[str]:
        """Select best capability via LangChain, fallback to keyword matching."""
        if self.llm:
            try:
                prompt = (
                    "Choose exactly one capability from this list for the request.\n"
                    f"Capabilities: {capabilities}\n"
                    f"Request: {request}\n"
                    "Return only the capability token."
                )
                response = self.llm.invoke([
                    SystemMessage(content="You are an Omega agent router."),
                    HumanMessage(content=prompt),
                ])
                choice = str(response.content).strip()
                if choice in capabilities:
                    return choice
            except Exception:
                pass

        lowered = request.lower()
        keyword_map = {
            "email": AgentCapability.EMAIL.value,
            "message": AgentCapability.MESSAGING.value,
            "chat": AgentCapability.CONVERSATION.value,
            "code": AgentCapability.CODE_EXECUTION.value,
            "test": AgentCapability.CODE_EXECUTION.value,
            "file": AgentCapability.FILE_OPERATIONS.value,
            "monitor": AgentCapability.SYSTEM_MONITORING.value,
            "log": AgentCapability.LOG_ANALYSIS.value,
        }
        for key, cap in keyword_map.items():
            if key in lowered and cap in capabilities:
                return cap
        return capabilities[0] if capabilities else None

class UnifiedAgent(ABC):
    """
    Base class for all Omega agents

    Every agent inherits this foundation and extends it with
    department-specific capabilities.

    Think of this as the foundation laid on the steep parcel -
    solid, consistent, and supporting everything built on top.
    """

    def __init__(
        self,
        agent_id: str,
        department: AgentDepartment,
        name: str,
        description: str,
        capabilities: List[AgentCapability] = None
    ):
        """
        Initialize a unified agent

        Args:
            agent_id: Unique identifier for this agent
            department: Department this agent belongs to
            name: Human-readable name
            description: What this agent does
            capabilities: List of capabilities this agent has
        """
        self.agent_id = agent_id
        self.department = department
        self.name = name
        self.description = description
        self.capabilities = capabilities or []

        # Core state
        self.active = False
        self.created_at = datetime.now()
        self.last_active = None
        self.task_count = 0

        # Admin privileges
        self.admin = None
        try:
            self.admin = get_omega_admin()
        except:
            pass

        # Memory and context
        self.memory = {}
        self.context = {}
        self.conversation_history = []

        # Configuration
        self.config = self._load_config()
        self.identity = self._load_identity_profile()

        # Metrics
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_runtime": 0.0,
            "errors": []
        }

        # Initialize agent-specific components
        self.brain = GatekeeperBrainAccess()
        self._initialize()

    def _load_config(self) -> Dict:
        """Load agent configuration"""
        config_file = Path(__file__).parent / f"config/agents/{self.agent_id}.json"

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                pass

        # Default config
        return {
            "enabled": True,
            "log_level": "INFO",
            "max_concurrent_tasks": 5,
            "timeout": 300,
            "retry_attempts": 3
        }

    def _load_identity_profile(self) -> Dict[str, Any]:
        """Load per-agent identity (voice/personality/specialization)."""
        profile_file = Path(__file__).parent / f"config/agents/profiles/{self.agent_id}.json"
        if profile_file.exists():
            try:
                with open(profile_file, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                    if isinstance(profile, dict):
                        return profile
            except Exception:
                pass

        return {
            "agent_id": self.agent_id,
            "display_name": self.name,
            "voice": {
                "profile": "default",
                "sample_file": None,
                "style": "neutral",
            },
            "personality": {
                "tone": "focused",
                "traits": ["pragmatic", "direct"],
                "communication_style": "concise",
            },
            "specialization": self.department.value,
        }

    @abstractmethod
    def _initialize(self):
        """Initialize agent-specific components (must be implemented by subclass)"""
        pass

    @abstractmethod
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task (must be implemented by subclass)

        Args:
            task: Task dictionary with:
                - type: Task type
                - data: Task data
                - priority: Task priority (1-10)
                - metadata: Additional metadata

        Returns:
            Result dictionary with:
                - success: Boolean
                - result: Task result
                - error: Error message if failed
                - metrics: Task metrics
        """
        pass

    def activate(self):
        """Activate the agent"""
        self.active = True
        self.last_active = datetime.now()
        self._log("INFO", f"Agent {self.name} activated")

    def deactivate(self):
        """Deactivate the agent"""
        self.active = False
        self._log("INFO", f"Agent {self.name} deactivated")

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with error handling and metrics

        This method wraps process_task with common functionality
        """
        if not self.active:
            return {
                "success": False,
                "error": "Agent is not active",
                "agent_id": self.agent_id
            }

        start_time = time.time()
        self.task_count += 1
        self.last_active = datetime.now()

        try:
            self._log("INFO", f"Processing task: {task.get('type', 'unknown')}")

            # Process the task (subclass implementation)
            result = self.process_task(task)

            # Track metrics
            elapsed = time.time() - start_time
            self.metrics["total_runtime"] += elapsed

            if result.get("success", False):
                self.metrics["tasks_completed"] += 1
            else:
                self.metrics["tasks_failed"] += 1

            result["elapsed_time"] = elapsed
            result["agent_id"] = self.agent_id
            result["agent_name"] = self.name

            self._log("INFO", f"Task completed in {elapsed:.2f}s")

            return result

        except Exception as e:
            elapsed = time.time() - start_time
            self.metrics["tasks_failed"] += 1
            self.metrics["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "task": task
            })

            self._log("ERROR", f"Task failed: {e}")

            return {
                "success": False,
                "error": str(e),
                "elapsed_time": elapsed,
                "agent_id": self.agent_id,
                "agent_name": self.name
            }

    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities

    def add_to_memory(self, key: str, value: Any):
        """Add information to agent memory"""
        self.memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }

    def recall_from_memory(self, key: str) -> Optional[Any]:
        """Recall information from agent memory"""
        if key in self.memory:
            return self.memory[key]["value"]
        return None

    def add_to_context(self, key: str, value: Any):
        """Add information to current context"""
        self.context[key] = value

    def clear_context(self):
        """Clear current context"""
        self.context = {}

    def add_to_conversation(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_conversation_history(self, limit: int = None) -> List[Dict]:
        """Get conversation history"""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history

    def _log(self, level: str, message: str):
        """Log a message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] [{self.name}] {message}")

        # Also write to log file
        log_file = Path(__file__).parent / f"logs/agents/{self.agent_id}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "department": self.department.value,
            "description": self.description,
            "active": self.active,
            "capabilities": [cap.value for cap in self.capabilities],
            "tasks_completed": self.metrics["tasks_completed"],
            "tasks_failed": self.metrics["tasks_failed"],
            "task_count": self.task_count,
            "uptime": (datetime.now() - self.created_at).total_seconds(),
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "config": self.config
        }

    def get_identity(self) -> Dict[str, Any]:
        return self.identity

    def query_shared_brain(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.brain.search(query, limit=limit)

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        return {
            "agent_id": self.agent_id,
            "metrics": self.metrics,
            "uptime": (datetime.now() - self.created_at).total_seconds(),
            "tasks_per_minute": self.task_count / max(1, (datetime.now() - self.created_at).total_seconds() / 60),
            "success_rate": self.metrics["tasks_completed"] / max(1, self.task_count),
            "average_task_time": self.metrics["total_runtime"] / max(1, self.task_count)
        }

    def __repr__(self) -> str:
        """String representation"""
        return f"<{self.__class__.__name__} '{self.name}' ({self.department.value})>"


class AgentRegistry:
    """
    Central registry for all agents

    Manages agent lifecycle, communication, and coordination
    """

    def __init__(self):
        """Initialize agent registry"""
        self.agents: Dict[str, UnifiedAgent] = {}
        self.departments: Dict[AgentDepartment, List[str]] = {}
        self.bus = AgentCommunicationBus()
        self.community_log_file = Path(__file__).parent / "logs/agents/town_hall.log"

    def register_agent(self, agent: UnifiedAgent):
        """Register an agent"""
        self.agents[agent.agent_id] = agent

        # Add to department
        if agent.department not in self.departments:
            self.departments[agent.department] = []
        self.departments[agent.department].append(agent.agent_id)

        print(f"✅ Registered agent: {agent.name} ({agent.department.value})")

    def get_agent(self, agent_id: str) -> Optional[UnifiedAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    def get_agents_by_department(self, department: AgentDepartment) -> List[UnifiedAgent]:
        """Get all agents in a department"""
        agent_ids = self.departments.get(department, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]

    def get_agents_by_capability(self, capability: AgentCapability) -> List[UnifiedAgent]:
        """Get all agents with a specific capability"""
        return [agent for agent in self.agents.values() if agent.has_capability(capability)]

    def activate_all(self):
        """Activate all agents"""
        for agent in self.agents.values():
            agent.activate()

    def deactivate_all(self):
        """Deactivate all agents"""
        for agent in self.agents.values():
            agent.deactivate()

    def get_system_status(self) -> Dict:
        """Get status of all agents"""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "departments": {dept.value: len(agents) for dept, agents in self.departments.items()},
            "agents": [agent.get_status() for agent in self.agents.values()],
            "messages": len(self.bus.history),
            "langchain_routing": LANGCHAIN_AVAILABLE and self.bus.llm is not None,
        }

    def route_task(self, request: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Route a free-text request to the best active agent and execute."""
        active_agents = [a for a in self.agents.values() if a.active]
        if not active_agents:
            return {"success": False, "error": "No active agents"}

        all_caps = sorted({cap.value for a in active_agents for cap in a.capabilities})
        selected_cap = self.bus.suggest_capability(request, all_caps)
        if not selected_cap:
            return {"success": False, "error": "No suitable capability found"}

        target = next(
            (a for a in active_agents if any(cap.value == selected_cap for cap in a.capabilities)),
            None,
        )
        if not target:
            return {"success": False, "error": f"No agent with capability {selected_cap}"}

        task = {
            "type": payload.get("type", "compose_message") if payload else "compose_message",
            "data": {
                "request": request,
                **(payload or {}),
            },
            "priority": payload.get("priority", 5) if payload else 5,
            "metadata": {"routed_capability": selected_cap},
        }
        self.bus.send("omega", target.agent_id, request, {"capability": selected_cap})
        result = target.execute_task(task)
        self.bus.send(target.agent_id, "omega", json.dumps(result)[:2000], {"result": True})
        return {
            "success": True,
            "target_agent": target.agent_id,
            "capability": selected_cap,
            "result": result,
        }

    def get_message_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        return [asdict(m) for m in self.bus.history[-limit:]]

    def town_hall_post(self, sender: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Post to shared community/town-hall channel."""
        msg = self.bus.broadcast(sender, "town_hall", content, metadata)
        self.community_log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.community_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(msg), ensure_ascii=False) + "\n")
        return asdict(msg)

    def town_hall_feed(self, limit: int = 100) -> List[Dict[str, Any]]:
        return [asdict(m) for m in self.bus.get_channel_history("town_hall", limit=limit)]

    def omega_query_brain(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Allow Omega (or orchestrator) to access the same shared brain layer."""
        brain = GatekeeperBrainAccess()
        return brain.search(query, limit=limit)

    def export_agent_bundle(self, agent_id: str, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Export an agent as an independent removable bundle for external systems.
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return {"success": False, "error": f"Unknown agent_id: {agent_id}"}

        root = Path(__file__).parent
        out_root = output_dir or (root / "dist/agent-bundles")
        bundle_dir = out_root / agent_id
        bundle_dir.mkdir(parents=True, exist_ok=True)

        module_map = {
            "development_agent": root / "agents/development_agent.py",
            "communication_agent": root / "agents/communication_agent.py",
            "creative_agent": root / "agents/creative_agent.py",
            "harriet_agent": root / "agents/harriet_agent.py",
            "bob_agent": root / "agents/bob_agent.py",
        }
        files_to_copy = [
            root / "unified_agent_framework.py",
            module_map.get(agent_id),
            root / f"config/agents/profiles/{agent_id}.json",
        ]

        copied = []
        for src in files_to_copy:
            if src is not None and src.exists():
                dst = bundle_dir / src.name
                shutil.copy2(src, dst)
                copied.append(str(dst))

        manifest = {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "department": agent.department.value,
            "identity": agent.get_identity(),
            "capabilities": [cap.value for cap in agent.capabilities],
            "brain_sources": agent.brain.available_sources(),
            "exported_at": datetime.now().isoformat(),
            "files": copied,
        }
        manifest_path = bundle_dir / "bundle_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return {
            "success": True,
            "bundle_dir": str(bundle_dir),
            "manifest": str(manifest_path),
        }


# Singleton registry
_agent_registry = None

def get_agent_registry() -> AgentRegistry:
    """Get singleton agent registry"""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry


if __name__ == "__main__":
    print("="*70)
    print("UNIFIED AGENT FRAMEWORK")
    print("="*70)
    print()
    print("This is the foundation for all Omega agents.")
    print("Each department agent extends this base framework.")
    print()
    print("Available Departments:")
    for dept in AgentDepartment:
        print(f"  - {dept.value}")
    print()
    print("Available Capabilities:")
    for cap in AgentCapability:
        print(f"  - {cap.value}")
