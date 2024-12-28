from typing import List, Optional

from autogen_core import (
    AgentId,
    AgentProxy,
    SingleThreadedAgentRuntime,
)
from autogen_core.tools import BaseToolWithState
from autogen_magentic_one.agents.orchestrator import RoundRobinOrchestrator
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import (
    RequestReplyMessage,
)
from autogen_magentic_one.utils import create_completion_client_from_env
from pydantic import (
    BaseModel,
    Field,
)

from dynamic_taskgraph.agent.actor import Actor
from dynamic_taskgraph.agent.allocator import Allocator


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

    async def start(self) -> str:
        runtime = SingleThreadedAgentRuntime()
        client = create_completion_client_from_env()

        # user_input_agent
        await UserProxy.register(
            runtime=runtime,
            type="UserProxy",
            factory=lambda: UserProxy(
                description="The current user interacting with you."
            ),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), runtime)

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
        await runtime.send_message(RequestReplyMessage(), user_proxy.id)
        await runtime.stop_when_idle()
        self.task_output = self.allocator.get_final_result()
        print(f"{self.name} task completed.")
