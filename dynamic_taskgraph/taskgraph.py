from collections import OrderedDict, defaultdict
from copy import deepcopy
from typing import List, Tuple

import matplotlib.pyplot as plt
import networkx as nx


class TaskGraphNode:
    """Class representing a node in the TaskGraph."""

    def __init__(self, name: str):
        self.name: str = name
        self.out_edges: set[str] = set()  # Nodes this node points to
        self.in_edges: set[str] = set()  # Nodes pointing to this node

    def __repr__(self) -> str:
        return f"TaskGraphNode(name={self.name}, out_edges={list(self.out_edges)}, in_edges={list(self.in_edges)})"


class TaskGraph:
    """Directed acyclic graph (DAG) implementation with comprehensive edge storage."""

    def __init__(self):
        self.reset_graph()

    def reset_graph(self) -> None:
        """Restore the graph to an empty state."""
        self.graph: OrderedDict[str, TaskGraphNode] = OrderedDict()

    def add_node(self, node_name: str) -> None:
        """Add a node if it does not exist yet."""
        if node_name in self.graph:
            raise KeyError(f"Node {node_name} already exists")
        self.graph[node_name] = TaskGraphNode(node_name)

    def delete_node(self, node_name: str) -> None:
        """Delete a node and all edges referencing it."""
        if node_name not in self.graph:
            raise KeyError(f"Node {node_name} does not exist")

        node_to_delete = self.graph[node_name]
        # Remove edges to this node
        for predecessor in node_to_delete.in_edges:
            self.graph[predecessor].out_edges.remove(node_name)
        # Remove edges from this node
        for successor in node_to_delete.out_edges:
            self.graph[successor].in_edges.remove(node_name)
        # Remove the node itself
        del self.graph[node_name]

    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add an edge (dependency) between the specified nodes."""
        if from_node not in self.graph or to_node not in self.graph:
            raise KeyError("One or more nodes do not exist in the graph")

        # Check for cycles by temporarily adding the edge
        test_graph = deepcopy(self.graph)
        test_graph[from_node].out_edges.add(to_node)
        test_graph[to_node].in_edges.add(from_node)
        is_valid, _ = self.validate()
        if is_valid:
            self.graph[from_node].out_edges.add(to_node)
            self.graph[to_node].in_edges.add(from_node)
        else:
            raise Exception("Adding this edge would create a cycle")

    def delete_edge(self, from_node: str, to_node: str) -> None:
        """Delete an edge from the graph."""
        if to_node not in self.graph.get(from_node, TaskGraphNode(from_node)).out_edges:
            raise KeyError(f"Edge from {from_node} to {to_node} does not exist")
        self.graph[from_node].out_edges.remove(to_node)
        self.graph[to_node].in_edges.remove(from_node)

    def topological_sort(self) -> List[str]:
        """Returns a topological ordering of the DAG.
        Raises an error if this is not possible (graph is not valid).
        """
        in_degree = defaultdict(int)
        for node in self.graph.values():
            for successor in node.out_edges:
                in_degree[successor] += 1

        ready = [node.name for node in self.graph.values() if in_degree[node.name] == 0]
        result = []

        while ready:
            node_name = ready.pop()
            result.append(node_name)
            for successor in self.graph[node_name].out_edges:
                in_degree[successor] -= 1
                if in_degree[successor] == 0:
                    ready.append(successor)

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

    def all_downstreams(self, node_name: str) -> List[str]:
        """Return all nodes downstream of the given node in topological order."""
        if node_name not in self.graph:
            raise KeyError(f"Node {node_name} does not exist")
        nodes_seen = set()
        nodes_to_visit = [node_name]

        while nodes_to_visit:
            current = nodes_to_visit.pop()
            if current not in nodes_seen:
                nodes_seen.add(current)
                nodes_to_visit.extend(self.graph[current].out_edges)

        return [node for node in self.topological_sort() if node in nodes_seen]

    def visualize(self, filename: str = "TaskGraph.png") -> None:
        """Visualize the graph using matplotlib and networkx."""
        G = nx.DiGraph()
        for node_name, node in self.graph.items():
            for successor in node.out_edges:
                G.add_edge(node_name, successor)

        # Use graphviz_layout for left-to-right directed graph layout
        pos = nx.nx_pydot.graphviz_layout(G, prog="dot")
        plt.figure(figsize=(10, 6))
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_size=2000,
            node_color="skyblue",
            font_size=12,
            font_weight="bold",
            arrowsize=20,
        )

        plt.savefig(filename)  # Save the visualization as a file
        plt.close()

    def __repr__(self) -> str:
        return f"TaskGraph({list(self.graph.values())})"


if __name__ == "__main__":
    dag = TaskGraph()
    dag.add_node("a")
    dag.add_node("b")
    dag.add_node("c")
    dag.add_node("d")

    dag.add_edge("a", "b")
    dag.add_edge("a", "d")
    dag.add_edge("b", "c")

    print("Topological Sort:", dag.topological_sort())
    print("All Downstreams of 'b':", dag.all_downstreams("b"))
    print("Graph Representation:", dag)

    # Visualize the DAG
    dag.visualize()
