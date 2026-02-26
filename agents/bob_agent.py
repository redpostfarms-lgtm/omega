"""
Bob Agent
=========
Engineering execution and implementation agent.
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


class BobAgent(UnifiedAgent):
    """Agent specialized in engineering implementation tasks."""

    def __init__(self):
        super().__init__(
            agent_id="bob_agent",
            department=AgentDepartment.DEVELOPMENT,
            name="Bob",
            description="Handles engineering implementation, code execution, and technical delivery tasks.",
            capabilities=[
                AgentCapability.TEXT_GENERATION,
                AgentCapability.CONVERSATION,
                AgentCapability.CODE_EXECUTION,
                AgentCapability.FILE_OPERATIONS,
                AgentCapability.LLM_ACCESS,
            ],
        )

    def _initialize(self):
        self._log("INFO", "Initializing Bob agent")

    def process_task(self, task: dict) -> dict:
        task_type = task.get("type", "")
        registry = get_agent_registry()
        registry.town_hall_post(
            self.agent_id,
            f"Bob accepted task '{task_type}'",
            {"department": self.department.value, "priority": task.get("priority", 5)},
        )

        if task_type in ("engineering_task", "code_review", "debug", "compose_message"):
            data = task.get("data", {})
            request = data.get("request", "") or data.get("purpose", "Resolve engineering task")
            return {
                "success": True,
                "result": {
                    "agent": self.name,
                    "request": request,
                    "response": "Prepared an engineering action plan with implementation and verification steps.",
                },
            }
        return {"success": False, "error": f"Unknown task type: {task_type}"}

