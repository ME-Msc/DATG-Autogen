import asyncio
import logging

from autogen_core import EVENT_LOGGER_NAME
from autogen_magentic_one.utils import LogHandler

from dynamic_taskgraph.task import AlphaTask, OmegaTask, Task
from dynamic_taskgraph.taskgraph import TaskGraph


async def main():
    task_graph = TaskGraph()
    alpha_task = AlphaTask()
    omega_task = OmegaTask()
    task_graph.add_node(task=alpha_task)
    task_graph.add_node(task=omega_task)
    task_graph.add_edge(from_task=alpha_task, to_task=omega_task)
    await task_graph.run(max_rounds=3)


def test_taskGraph():
    from dynamic_taskgraph.taskgraph import TaskGraph

    dag = TaskGraph()
    task_1 = Task(name="task_1")
    task_2 = Task(name="task_2")
    task_3 = Task(name="task_3")
    task_4 = Task(name="task_4")
    dag.add_node(task=task_1)
    dag.add_node(task=task_2)
    dag.add_node(task=task_3)
    dag.add_node(task=task_4)

    dag.add_edge(from_task=task_1, to_task=task_2)
    dag.add_edge(from_task=task_1, to_task=task_4)
    dag.add_edge(from_task=task_2, to_task=task_3)

    print("Topological Sort:", dag.topological_sort())
    print("All Downstreams of 'b':", dag.all_downstreams(task_2))
    print("Graph Representation:", dag)

    # Visualize the DAG
    dag.visualize()


if __name__ == "__main__":
    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_handler = LogHandler()
    logger.handlers = [log_handler]
    asyncio.run(main())
