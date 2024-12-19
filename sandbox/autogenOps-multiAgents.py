import os

import agentops
import dotenv
import IPython.display
import litellm
from agentops import track_agent

# Configurations
# config: API_KEY
dotenv.load_dotenv("../")
AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")

# config: logging
# logging.basicConfig(
#     level=logging.DEBUG
# )

# config: agentops
agentops.init(AGENTOPS_API_KEY, default_tags=["multi-agent"])


@track_agent(name="qa")
class QaAgent:
    def completion(self, prompt: str):
        response = litellm.completion(
            model="ollama/mistral",
            api_base="http://localhost:11434",
            stream=False,
            messages=[
                {
                    "role": "system",
                    "content": "You are a qa engineer and only output python code, no markdown tags.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content


@track_agent(name="engineer")
class EngineerAgent:
    def completion(self, prompt: str):
        response = litellm.completion(
            model="ollama/mistral",
            api_base="http://localhost:11434",
            stream=False,
            messages=[
                {
                    "role": "system",
                    "content": "You are a software engineer and only output python code, no markdown tags.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content


qa = QaAgent()
engineer = EngineerAgent()

generated_func = engineer.completion("python function to test prime number")

IPython.display.display(
    IPython.display.Markdown("```python\n" + generated_func + "\n```")
)

generated_test = qa.completion(
    "Write a python unit test that test the following function: \n " + generated_func
)

IPython.display.display(
    IPython.display.Markdown("```python\n" + generated_test + "\n```")
)
