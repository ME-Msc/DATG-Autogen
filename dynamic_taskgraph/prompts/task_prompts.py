from autogen_core.models import SystemMessage

ALPHA_TASK_SYSTEM_MESSAGES = [
    SystemMessage(
        content="""
Your purpose is to process user input and generate a summary of the input as a task name.
You will receive the user input as follows:
{user_input}

Based on this input, summarize it with the fewest phrases, and I will regard it as a task name.
"""
    ),
]
