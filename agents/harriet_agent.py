"""
Harriet Agent
=============
People-operations and communication support agent.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_agent_framework import (
    UnifiedAgent,
    AgentDepartment,
    AgentCapability,
    get_agent_registry,
)


class HarrietAgent(UnifiedAgent):
    """Agent specialized in people operations and support communication."""

    def __init__(self):
        super().__init__(
            agent_id="harriet_agent",
            department=AgentDepartment.SUPPORT,
            name="Harriet",
            description="Handles HR-style support workflows, policy communication, and team coordination tasks.",
            capabilities=[
                AgentCapability.TEXT_GENERATION,
                AgentCapability.CONVERSATION,
                AgentCapability.MESSAGING,
                AgentCapability.LLM_ACCESS,
            ],
        )

    def _initialize(self):
        self._log("INFO", "Initializing Harriet agent")

    def process_task(self, task: dict) -> dict:
        task_type = task.get("type", "")
        registry = get_agent_registry()
        registry.town_hall_post(
            self.agent_id,
            f"Harriet accepted task '{task_type}'",
            {"department": self.department.value, "priority": task.get("priority", 5)},
        )

        if task_type in ("hr_support", "policy_brief", "team_update", "compose_message"):
            data = task.get("data", {})
            request = data.get("request", "") or data.get("purpose", "Provide team support guidance")
            return {
                "success": True,
                "result": {
                    "agent": self.name,
                    "request": request,
                    "response": "Prepared a clear support-oriented response with policy-safe language and action steps.",
                },
            }
        return {"success": False, "error": f"Unknown task type: {task_type}"}

