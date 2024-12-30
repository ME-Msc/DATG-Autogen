import re

def get_json(content):
    # 解析content
    decomposition_mode_pattern = r"\*\*Decomposition Mode\*\*: (\w+)"
    sub_task_pattern = r"- \*\*Sub-task (\d+)\*\*:\n\s+- \*\*Description\*\*: (.+)\n\s+- \*\*Name\*\*: (.+)"

    decomposition_mode = re.search(decomposition_mode_pattern, content).group(1)
    sub_tasks = re.findall(sub_task_pattern, content)

    sub_tasks_list = []
    for sub_task in sub_tasks: 
        sub_task_dict = {
            "sub_task_number": int(sub_task[0]),
            "description": sub_task[1],
            "name": sub_task[2]
        }
        sub_tasks_list.append(sub_task_dict)
    result = {
        "decomposition_mode": decomposition_mode,
        "sub_tasks": sub_tasks_list
    }
    
    return result
