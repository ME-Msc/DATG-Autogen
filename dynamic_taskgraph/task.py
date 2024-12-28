import asyncio
from typing import List, Optional, Tuple

from autogen_core import (
    AgentId,
    AgentProxy,
    DefaultTopicId,
    SingleThreadedAgentRuntime,
)
from autogen_core.models import UserMessage
from autogen_core.tools import BaseToolWithState
from autogen_magentic_one.agents.orchestrator import RoundRobinOrchestrator
from autogen_magentic_one.messages import BroadcastMessage
from autogen_magentic_one.utils import create_completion_client_from_env
from pydantic import (
    BaseModel,
    Field,
)

from dynamic_taskgraph.agent.actor import Actor
from dynamic_taskgraph.agent.allocator import Allocator
from dynamic_taskgraph.prompts.task_prompts import ALPHA_TASK_SYSTEM_MESSAGES


class AlphaTask(BaseModel):  # | GenesisTask
    """Virtual Task for processing input of Task Graph."""

    name: str = "alpha_task"
    description: str = "Virtual Task for processing input of Task Graph."
    task_output: Optional[Tuple[str, str | None]] = Field(
        description="tuple(user input, summary of user input as default task name)",
        default=None,
    )  # TODO: unify the type of task_output for all tasks

    async def start(self) -> Tuple[str, str]:
        try:
            user_input = await asyncio.to_thread(input, "User input ('exit' to quit): ")
            user_input = user_input.strip()
            if user_input == "exit":
                raise asyncio.CancelledError()
            client = create_completion_client_from_env()
            default_taskname = await client.create(
                messages=ALPHA_TASK_SYSTEM_MESSAGES
                + [UserMessage(content=user_input, source="UserProxy")]
            )
            assert isinstance(default_taskname.content, str)
            self.task_output = user_input, default_taskname.content
            return self.task_output
        except asyncio.CancelledError:
            print("Task has been cancelled.")


class OmegaTask(BaseModel):
    """Virtual Task for processing output of Task Graph."""

    name: str = "omega_task"
    description: str = "Virtual Task for processing output of Task Graph."
    task_output: Optional[str] = Field(description="task graph output", default=None)

    async def start(self, task_input: str) -> Tuple[str, str | None]:
        self.task_output = task_input
        print(
            f"{self.name} task completed. Its output is: {self.task_output}. It is the final task."
        )
        return self.task_output, None


class Task(BaseModel):
    """Task class representing a task node."""

    class Config:
        arbitrary_types_allowed = True

    name: str = Field(default=None)
    description: str = Field(default=None)
    task_input: str = Field(default=None)  # TODO: List[str] for parallel tasks
    task_output: Optional[str] = Field(default=None)
    allocator: Allocator = Field(default=None)
    actor: Actor = Field(default=None)
    tools: Optional[List[BaseToolWithState]] = Field(
        description="Tools the task is limited to use.",
        default_factory=list,
    )
    task_graph_context: Optional[List["Task"]] = Field(
        description="",
        default_factory=list,
    )

    async def start(self, task_input: str) -> str:
        runtime = SingleThreadedAgentRuntime()
        client = create_completion_client_from_env()

        # actor
        await Actor.register(
            runtime=runtime,
            type="Actor",
            factory=lambda: Actor(model_client=client),
        )
        actor_id = AgentId(type="Actor", key="default")
        actor_proxy = AgentProxy(actor_id, runtime)
        self.actor = await runtime._get_agent(actor_id)

        # allocator
        await Allocator.register(
            runtime=runtime,
            type="Allocator",
            factory=lambda: Allocator(model_client=client),
        )
        allocator_id = AgentId(type="Allocator", key="default")
        allocator_proxy = AgentProxy(allocator_id, runtime)
        self.allocator = await runtime._get_agent(allocator_id)

        await RoundRobinOrchestrator.register(
            runtime=runtime,
            type="orchestrator",
            factory=lambda: RoundRobinOrchestrator(
                agents=[actor_proxy, allocator_proxy], max_rounds=2
            ),
        )

        runtime.start()

        self.task_input = task_input
        await runtime.publish_message(
            BroadcastMessage(
                content=UserMessage(content=self.task_input, source="UserProxy")
            ),
            topic_id=DefaultTopicId(),
        )
        await runtime.stop_when_idle()
        self.task_output = (
            self.actor.get_final_result(),
            self.allocator.get_final_result(),
        )
        print(f"{self.name} task completed.")
        return self.task_output
