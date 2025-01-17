from typing import List, Tuple

from autogen_core import CancellationToken, default_subscription
from autogen_core.models import ChatCompletionClient, SystemMessage
from autogen_magentic_one.agents.base_worker import BaseWorker
from autogen_magentic_one.messages import (
    UserContent,
)

from dynamic_taskgraph.prompts.allocator_prompts import (
    ALLOCATOR_DESCRIPTION,
    ALLOCATOR_SYSTEM_MESSAGES,
)
from dynamic_taskgraph.prompts.prompts_parser import content_to_dictionary


@default_subscription
class Allocator(BaseWorker):
    def __init__(
        self,
        model_client: ChatCompletionClient,
        description: str = ALLOCATOR_DESCRIPTION,
        system_messages: List[SystemMessage] = ALLOCATOR_SYSTEM_MESSAGES,
        request_terminate: bool = False,
    ) -> None:
        super().__init__(description)
        self._model_client = model_client
        self._system_messages = system_messages
        self._request_terminate = request_terminate

    async def _generate_reply(
        self, cancellation_token: CancellationToken
    ) -> Tuple[bool, UserContent]:
        """Respond to a reply request."""

        # Make an inference to the model.
        response = await self._model_client.create(
            self._system_messages + self._chat_history,
            cancellation_token=cancellation_token,
        )
        assert isinstance(response.content, str)
        if self._request_terminate:
            return "TERMINATE" in response.content, response.content
        else:
            return False, response.content

    def get_final_result(self):
        return self._chat_history[-1].content

    def get_subtask_result_dict(self):
        return content_to_dictionary(self._chat_history[-1].content)
