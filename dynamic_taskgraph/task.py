from typing import List, Optional

from autogen_core.tools import BaseToolWithState
from autogen_magentic_one.agents.base_agent import MagenticOneBaseAgent
from pydantic import (
    BaseModel,
    Field,
)


class Task(BaseModel):
    """Task class representing a task node."""

    name: str
    description: str
    actual_input: List[str]
    expected_output: str
    actual_output: str
    allocating_orchestrator_agent: MagenticOneBaseAgent
    # TODO execute_agent: MagenticOneBaseAgent
    tools: Optional[List[BaseToolWithState]] = Field(
        default_factory=list,
        description="Tools the task is limited to use.",
    )
    context: Optional[List["Task"]] = Field(
        description="Other tasks that will have their output used as context for this task.",
        default=None,
    )

    def start(actual_input: str) -> str:
        # TODO
        return "LLM response"
