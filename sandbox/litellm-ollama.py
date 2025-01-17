"""
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3:instruct
pip install 'litellm[proxy]'
litellm --model ollama/llama3:instruct

This will run the proxy server and it will be available at 'http://0.0.0.0:4000/'.
"""

import asyncio
from dataclasses import dataclass

from autogen_core import (
    AgentId,
    DefaultTopicId,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    default_subscription,
    message_handler,
)
from autogen_core.components.model_context import BufferedChatCompletionContext
from autogen_core.models import (
    AssistantMessage,
    ChatCompletionClient,
    SystemMessage,
    UserMessage,
)
from autogen_ext.models.openai import OpenAIChatCompletionClient

def get_model_client() -> OpenAIChatCompletionClient:  # type: ignore
    "Mimic OpenAI API using Local LLM Server."
    return OpenAIChatCompletionClient(
        model="gpt-4o",  # Need to use one of the OpenAI models as a placeholder for now.
        api_key="NotRequiredSinceWeAreLocal",
        base_url="http://0.0.0.0:4000",
    )

@dataclass
class Message:
    content: str

@default_subscription
class Assistant(RoutedAgent):
    def __init__(self, name: str, model_client: ChatCompletionClient) -> None:
        super().__init__("An assistant agent.")
        self._model_client = model_client
        self.name = name
        self.count = 0
        self._system_messages = [
            SystemMessage(
                content=f"Your name is {name} and you are a part of a duo of comedians."
                "You laugh when you find the joke funny, else reply 'I need to go now'.",
            )
        ]
        self._model_context = BufferedChatCompletionContext(buffer_size=5)

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> None:
        self.count += 1
        await self._model_context.add_message(UserMessage(content=message.content, source="user"))
        result = await self._model_client.create(self._system_messages + await self._model_context.get_messages())

        print(f"\n{self.name}: {message.content}")

        if "I need to go".lower() in message.content.lower() or self.count > 2:
            return

        await self._model_context.add_message(AssistantMessage(content=result.content, source="assistant"))  # type: ignore
        await self.publish_message(Message(content=result.content), DefaultTopicId())  # type: ignore

async def main():
    runtime = SingleThreadedAgentRuntime()

    cathy = await Assistant.register(
        runtime,
        "cathy",
        lambda: Assistant(name="Cathy", model_client=get_model_client()),
    )

    joe = await Assistant.register(
        runtime,
        "joe",
        lambda: Assistant(name="Joe", model_client=get_model_client()),
    )

    runtime.start()
    await runtime.send_message(
        Message("Joe, tell me a joke."),
        recipient=AgentId(joe, "default"),
        sender=AgentId(cathy, "default"),
    )
    await runtime.stop_when_idle()

if __name__ == '__main__':
    asyncio.run(main())