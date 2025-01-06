import re


def content_to_dictionary(content):
    satisfaction_decision_pattern = r"\*\*Satisfaction Decision\*\*: (True|False)"
    reasoning_pattern = r"\*\*Reasoning\*\*: (.+)"
    decomposition_mode_pattern = r"\*\*Decomposition Mode\*\*: (\w+)"
    sub_task_pattern = r"- \*\*Sub-task (\d+)\*\*:\n\s+- \*\*Description\*\*: (.+)\n\s+- \*\*Name\*\*: (.+)"

    satisfaction_decision = re.search(satisfaction_decision_pattern, content).group(1)
    reasoning = re.search(reasoning_pattern, content).group(1)

    decomposition_mode = None
    sub_tasks_list = []
    if satisfaction_decision == "False":
        decomposition_mode = re.search(decomposition_mode_pattern, content).group(1)
        sub_tasks = re.findall(sub_task_pattern, content)
        for sub_task in sub_tasks:
            sub_task_dict = {
                "sub_task_number": int(sub_task[0]),
                "description": sub_task[1],
                "name": sub_task[2],
            }
            sub_tasks_list.append(sub_task_dict)

    result = {
        "satisfaction_decision": satisfaction_decision == "True",
        "reasoning": reasoning,
        "decomposition_mode": decomposition_mode,
        "sub_tasks": sub_tasks_list if satisfaction_decision == "False" else None,
    }

    return result
