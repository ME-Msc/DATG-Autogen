import os
from collections import OrderedDict, defaultdict
from copy import deepcopy
from typing import List, Tuple

import matplotlib.pyplot as plt
import networkx as nx

from dynamic_taskgraph.task import AlphaTask, OmegaTask, Task


class TaskGraphNode:
    """Class representing a node in the TaskGraph."""

    def __init__(self, task: Task | AlphaTask | OmegaTask):
        self.task: Task = task
        self.out_edges: set[str] = set()  # Nodes this node points to
        self.in_edges: set[str] = set()  # Nodes pointing to this node

    def __repr__(self) -> str:
        return f"TaskGraphNode(name={self.task.name}, out_edges={list(self.out_edges)}, in_edges={list(self.in_edges)})"


class TaskGraph:
    """Directed acyclic graph (DAG) implementation with comprehensive edge storage."""

    def __init__(self):
        self.graph: OrderedDict[str, TaskGraphNode] = OrderedDict()
        self.node_count = 0

    def reset_graph(self) -> None:
        """Restore the graph to an empty state."""
        self.__init__()

    def add_node(self, task: Task) -> None:
        """Add a node if it does not exist yet."""
        if task.name is None:
            raise ValueError("Task name cannot be None")
        if task.name in self.graph:
            raise KeyError(f"Node {task.name} already exists")
        self.graph[task.name] = TaskGraphNode(task)
        self.node_count += 1

    def delete_node(self, task: Task) -> None:
        """Delete a node and all edges referencing it."""
        if task.name not in self.graph:
            raise KeyError(f"Node {task.name} does not exist")

        node_to_delete = self.graph[task.name]
        # Remove edges to this node
        for predecessor in node_to_delete.in_edges:
            self.graph[predecessor].out_edges.remove(task.name)
        # Remove edges from this node
        for successor in node_to_delete.out_edges:
            self.graph[successor].in_edges.remove(task.name)
        # Remove the node itself
        del self.graph[task.name]
        self.node_count -= 1

    def add_edge(self, from_task: Task, to_task: Task) -> None:
        """Add an edge (dependency) between the specified nodes."""
        if from_task.name not in self.graph:
            raise KeyError(f"Node {from_task.name} do not exist in the graph")
        if to_task.name not in self.graph:
            raise KeyError(f"Node {to_task.name} do not exist in the graph")

        # Check for cycles by temporarily adding the edge
        test_graph = deepcopy(self.graph)
        test_graph[from_task.name].out_edges.add(to_task.name)
        test_graph[to_task.name].in_edges.add(from_task.name)
        is_valid, _ = self.validate()
        if is_valid:
            self.graph[from_task.name].out_edges.add(to_task.name)
            self.graph[to_task.name].in_edges.add(from_task.name)
        else:
            raise Exception("Adding this edge would create a cycle")

    def delete_edge(self, from_task: Task, to_task: Task) -> None:
        """Delete an edge from the graph."""
        if (
            to_task.name
            not in self.graph.get(from_task.name, TaskGraphNode(from_task)).out_edges
        ):
            raise KeyError(
                f"Edge from {from_task.name} to {to_task.name} does not exist"
            )
        self.graph[from_task.name].out_edges.remove(to_task.name)
        self.graph[to_task.name].in_edges.remove(from_task.name)

    def topological_sort(self) -> List[str]:
        """Returns a topological ordering of the DAG.
        Raises an error if this is not possible (graph is not valid).
        """
        in_degree = defaultdict(int)
        for node in self.graph.values():
            for successor_name in node.out_edges:
                in_degree[successor_name] += 1

        ready = [
            node.task.name
            for node in self.graph.values()
            if in_degree[node.task.name] == 0
        ]
        result = []

        while ready:
            task_name = ready.pop()
            result.append(task_name)
            for successor_name in self.graph[task_name].out_edges:
                in_degree[successor_name] -= 1
                if in_degree[successor_name] == 0:
                    ready.append(successor_name)

        if len(result) == len(self.graph):
            return result
        else:
            raise ValueError("Graph is not acyclic")

    def validate(self) -> Tuple[bool, str]:
        """Validate if the graph is a valid DAG."""
        try:
            self.topological_sort()
        except ValueError:
            return False, "Graph is not acyclic"
        return True, "Valid DAG"

    def all_downstreams(self, task: Task) -> List[str]:
        """Return all nodes downstream of the given node in topological order."""
        if task.name not in self.graph:
            raise KeyError(f"Node {task.name} does not exist")
        nodes_seen_names = set()
        nodes_to_visit_names = [task.name]

        while nodes_to_visit_names:
            current_task_name = nodes_to_visit_names.pop()
            if current_task_name not in nodes_seen_names:
                nodes_seen_names.add(current_task_name)
                nodes_to_visit_names.extend(self.graph[current_task_name].out_edges)

        return [
            node_name
            for node_name in self.topological_sort()
            if node_name in nodes_seen_names
        ]

    def visualize(self, filename: str = "figures/TaskGraph.png") -> None:
        """Visualize the graph using matplotlib and networkx."""
        G = nx.DiGraph()

        labels = {node_name: node.task.name for node_name, node in self.graph.items()}

        for node_name, node in self.graph.items():
            for successor_name in node.out_edges:
                G.add_edge(node_name, successor_name)

        # Use graphviz_layout for left-to-right directed graph layout
        pos = nx.nx_pydot.graphviz_layout(G, prog="dot")
        plt.figure(figsize=(10, 6))

        # Draw nodes with custom size and shape
        for node_name, (x, y) in pos.items():
            label = labels[node_name]
            plt.text(
                x,
                y,
                label,
                ha="center",
                va="center",
                bbox=dict(
                    boxstyle="round,pad=0.3", edgecolor="black", facecolor="skyblue"
                ),
            )

        nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=20)

        # Check if the directory exists, if not, create it
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        plt.savefig(filename)  # Save the visualization as a file
        plt.close()

    def __repr__(self) -> str:
        return f"TaskGraph({list(self.graph.values())})"

    async def run(self, max_rounds: int = 2) -> None:
        input_dict: OrderedDict[str, str] = OrderedDict()  # task_name: task_input
        for i in range(max_rounds):
            waiting_list: List[str] = self.topological_sort()
            if self.node_count == 2:  # initial first_task
                self.visualize(filename=f"figures/TaskGraph_{i}.png")

                alpha_task_name = waiting_list[0]
                alpha_task: AlphaTask = self.graph[alpha_task_name].task

                omega_task_name = waiting_list[-1]
                omega_task: OmegaTask = self.graph[omega_task_name].task
                alpha_task_output, first_task_name, _ = await alpha_task.start()

                input_dict[omega_task_name] = alpha_task_output

                first_task = Task(name=first_task_name)
                self.add_node(task=first_task)
                self.add_edge(from_task=alpha_task, to_task=first_task)
                self.add_edge(from_task=first_task, to_task=omega_task)
                self.delete_edge(from_task=alpha_task, to_task=omega_task)
                input_dict[first_task_name] = alpha_task_output
            else:  # alpha_task -> first_task -> ...... -> omega_task
                for current_task_name in waiting_list:
                    current_task = self.graph[current_task_name].task
                    if isinstance(current_task, AlphaTask):
                        continue
                    try:
                        current_task_input = input_dict[current_task_name]
                    except KeyError:
                        raise KeyError(f"Task {current_task_name} has no input.")

                    current_task_output, _, _ = await current_task.start(
                        task_input=current_task_input
                    )
                    for successor_task_name in self.graph[current_task_name].out_edges:
                        input_dict[successor_task_name] = current_task_output
                print(f"TaskGraph round {i} execution completed.")
                self.visualize(filename=f"TaskGraph_{i}.png")
