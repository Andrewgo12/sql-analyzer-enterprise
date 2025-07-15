"""
Local NetworkX Implementation
Complete replacement for NetworkX graph operations used in SQL Analyzer.
This ensures the application works without external NetworkX dependency.
"""

from typing import Dict, List, Set, Any, Optional, Tuple
from collections import defaultdict, deque
import json


class Node:
    """Represents a graph node."""
    
    def __init__(self, node_id: str, **attributes):
        self.id = node_id
        self.attributes = attributes
    
    def __str__(self):
        return f"Node({self.id})"
    
    def __repr__(self):
        return self.__str__()


class Edge:
    """Represents a graph edge."""
    
    def __init__(self, source: str, target: str, **attributes):
        self.source = source
        self.target = target
        self.attributes = attributes
    
    def __str__(self):
        return f"Edge({self.source} -> {self.target})"
    
    def __repr__(self):
        return self.__str__()


class DiGraph:
    """
    Directed Graph implementation compatible with NetworkX DiGraph.
    Provides all methods needed by the SQL Analyzer schema analyzer.
    """
    
    def __init__(self):
        self.nodes_dict: Dict[str, Node] = {}
        self.edges_dict: Dict[Tuple[str, str], Edge] = {}
        self.successors_dict: Dict[str, Set[str]] = defaultdict(set)
        self.predecessors_dict: Dict[str, Set[str]] = defaultdict(set)
    
    def add_node(self, node_id: str, **attributes):
        """Add a node to the graph."""
        self.nodes_dict[node_id] = Node(node_id, **attributes)
        if node_id not in self.successors_dict:
            self.successors_dict[node_id] = set()
        if node_id not in self.predecessors_dict:
            self.predecessors_dict[node_id] = set()
    
    def add_edge(self, source: str, target: str, **attributes):
        """Add an edge to the graph."""
        # Ensure nodes exist
        if source not in self.nodes_dict:
            self.add_node(source)
        if target not in self.nodes_dict:
            self.add_node(target)
        
        # Add edge
        edge_key = (source, target)
        self.edges_dict[edge_key] = Edge(source, target, **attributes)
        self.successors_dict[source].add(target)
        self.predecessors_dict[target].add(source)
    
    def remove_node(self, node_id: str):
        """Remove a node and all its edges."""
        if node_id not in self.nodes_dict:
            return
        
        # Remove all edges involving this node
        edges_to_remove = []
        for (source, target) in self.edges_dict:
            if source == node_id or target == node_id:
                edges_to_remove.append((source, target))
        
        for edge_key in edges_to_remove:
            self.remove_edge(edge_key[0], edge_key[1])
        
        # Remove node
        del self.nodes_dict[node_id]
        del self.successors_dict[node_id]
        del self.predecessors_dict[node_id]
    
    def remove_edge(self, source: str, target: str):
        """Remove an edge from the graph."""
        edge_key = (source, target)
        if edge_key in self.edges_dict:
            del self.edges_dict[edge_key]
            self.successors_dict[source].discard(target)
            self.predecessors_dict[target].discard(source)
    
    def has_node(self, node_id: str) -> bool:
        """Check if node exists in graph."""
        return node_id in self.nodes_dict
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists in graph."""
        return (source, target) in self.edges_dict
    
    def nodes(self, data=False):
        """Return nodes, optionally with data."""
        if data:
            return [(node_id, node.attributes) for node_id, node in self.nodes_dict.items()]
        return list(self.nodes_dict.keys())
    
    def edges(self, data=False):
        """Return edges, optionally with data."""
        if data:
            return [(edge.source, edge.target, edge.attributes) for edge in self.edges_dict.values()]
        return [(edge.source, edge.target) for edge in self.edges_dict.values()]
    
    def successors(self, node_id: str) -> Set[str]:
        """Return successors of a node."""
        return self.successors_dict.get(node_id, set())
    
    def predecessors(self, node_id: str) -> Set[str]:
        """Return predecessors of a node."""
        return self.predecessors_dict.get(node_id, set())
    
    def neighbors(self, node_id: str) -> Set[str]:
        """Return neighbors of a node (successors in directed graph)."""
        return self.successors(node_id)
    
    def degree(self, node_id: str) -> int:
        """Return degree of a node (in-degree + out-degree)."""
        return len(self.successors_dict.get(node_id, set())) + len(self.predecessors_dict.get(node_id, set()))
    
    def in_degree(self, node_id: str) -> int:
        """Return in-degree of a node."""
        return len(self.predecessors_dict.get(node_id, set()))
    
    def out_degree(self, node_id: str) -> int:
        """Return out-degree of a node."""
        return len(self.successors_dict.get(node_id, set()))
    
    def number_of_nodes(self) -> int:
        """Return number of nodes."""
        return len(self.nodes_dict)
    
    def number_of_edges(self) -> int:
        """Return number of edges."""
        return len(self.edges_dict)
    
    def clear(self):
        """Clear the graph."""
        self.nodes_dict.clear()
        self.edges_dict.clear()
        self.successors_dict.clear()
        self.predecessors_dict.clear()
    
    def copy(self):
        """Return a copy of the graph."""
        new_graph = DiGraph()
        
        # Copy nodes
        for node_id, node in self.nodes_dict.items():
            new_graph.add_node(node_id, **node.attributes)
        
        # Copy edges
        for edge in self.edges_dict.values():
            new_graph.add_edge(edge.source, edge.target, **edge.attributes)
        
        return new_graph
    
    def subgraph(self, nodes: List[str]):
        """Return subgraph containing only specified nodes."""
        sub = DiGraph()
        
        # Add nodes
        for node_id in nodes:
            if node_id in self.nodes_dict:
                sub.add_node(node_id, **self.nodes_dict[node_id].attributes)
        
        # Add edges between nodes in subgraph
        for edge in self.edges_dict.values():
            if edge.source in nodes and edge.target in nodes:
                sub.add_edge(edge.source, edge.target, **edge.attributes)
        
        return sub
    
    def is_directed(self) -> bool:
        """Return True if graph is directed."""
        return True
    
    def reverse(self):
        """Return reversed graph."""
        reversed_graph = DiGraph()
        
        # Copy nodes
        for node_id, node in self.nodes_dict.items():
            reversed_graph.add_node(node_id, **node.attributes)
        
        # Reverse edges
        for edge in self.edges_dict.values():
            reversed_graph.add_edge(edge.target, edge.source, **edge.attributes)
        
        return reversed_graph
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation."""
        return {
            'nodes': {node_id: node.attributes for node_id, node in self.nodes_dict.items()},
            'edges': [
                {
                    'source': edge.source,
                    'target': edge.target,
                    'attributes': edge.attributes
                }
                for edge in self.edges_dict.values()
            ]
        }
    
    def __len__(self):
        """Return number of nodes."""
        return len(self.nodes_dict)
    
    def __contains__(self, node_id):
        """Check if node is in graph."""
        return node_id in self.nodes_dict
    
    def __iter__(self):
        """Iterate over nodes."""
        return iter(self.nodes_dict.keys())
    
    def __str__(self):
        return f"DiGraph with {len(self.nodes_dict)} nodes and {len(self.edges_dict)} edges"
    
    def __repr__(self):
        return self.__str__()


# Graph algorithms
def shortest_path(graph: DiGraph, source: str, target: str) -> Optional[List[str]]:
    """Find shortest path between two nodes using BFS."""
    if source not in graph or target not in graph:
        return None
    
    if source == target:
        return [source]
    
    queue = deque([(source, [source])])
    visited = {source}
    
    while queue:
        current, path = queue.popleft()
        
        for neighbor in graph.successors(current):
            if neighbor == target:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None


def has_path(graph: DiGraph, source: str, target: str) -> bool:
    """Check if path exists between two nodes."""
    return shortest_path(graph, source, target) is not None


def is_connected(graph: DiGraph) -> bool:
    """Check if graph is weakly connected."""
    if len(graph) == 0:
        return True
    
    # Convert to undirected for connectivity check
    visited = set()
    start_node = next(iter(graph))
    stack = [start_node]
    
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            # Add both successors and predecessors (treat as undirected)
            for neighbor in graph.successors(node) | graph.predecessors(node):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return len(visited) == len(graph)


def topological_sort(graph: DiGraph) -> List[str]:
    """Return topological sort of the graph."""
    in_degree = {node: graph.in_degree(node) for node in graph}
    queue = deque([node for node, degree in in_degree.items() if degree == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        
        for successor in graph.successors(node):
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                queue.append(successor)
    
    if len(result) != len(graph):
        raise ValueError("Graph contains a cycle")
    
    return result


def strongly_connected_components(graph: DiGraph) -> List[List[str]]:
    """Find strongly connected components using Tarjan's algorithm."""
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = {}
    components = []
    
    for node in graph:
        if node not in index:
            strongconnect(node)
    
    return components


# Create module-level functions that match NetworkX API
def create_digraph():
    """Create a new directed graph."""
    return DiGraph()


# Make this module compatible with NetworkX imports
nx = type('nx', (), {
    'DiGraph': DiGraph,
    'shortest_path': shortest_path,
    'has_path': has_path,
    'is_connected': is_connected,
    'topological_sort': topological_sort,
    'strongly_connected_components': strongly_connected_components
})
