"""
Topology Graph Utilities for MASim.

This module provides NetworkX-based topology management for the multi-agent
simulation framework. It handles:
- Building directed graphs from topology configuration
- Querying targets (successors) and senders (predecessors)
- Computing execution levels from seed nodes (BFS)
- Topology visualization

Usage:
    from masim.utils.topology import TopologyGraph

    graph = TopologyGraph(topology_config)
    targets = graph.get_targets("player_1")
    senders = graph.get_senders("player_1")
    levels = graph.get_execution_levels()  # Uses seeds from config
    graph.visualize()
"""

from typing import Any, Dict, List, Optional

import networkx as nx


class TopologyGraph:
    """
    NetworkX-based topology graph for player communication.

    Wraps a directed graph where edges represent allowed message paths.
    An edge from A to B means A can send messages to B.

    Supports execution level computation via BFS from seed nodes.

    Attributes:
        graph: The underlying NetworkX DiGraph
        seeds: List of seed player IDs for execution ordering
    """

    def __init__(self, topology_config: Optional[Dict[str, Any]] = None):
        """
        Initialize topology graph from configuration.

        Args:
            topology_config: Topology config dict with 'connections' and optional 'seeds'.
                            If None, creates empty graph.
        """
        self.graph: nx.DiGraph = nx.DiGraph()
        self.seeds: List[str] = []
        if topology_config:
            self._build_from_config(topology_config)

    def _build_from_config(self, config: Dict[str, Any]) -> None:
        """
        Build graph from topology configuration.

        Args:
            config: Dict with 'connections' mapping player_id -> [target_ids]
                   and optional 'seeds' list for execution ordering
        """
        # Extract seeds if present
        if "seeds" in config:
            self.seeds = list(config["seeds"])

        if "connections" not in config:
            return

        connections = config["connections"]
        for sender_id, targets in connections.items():
            # Add sender node (even if no targets)
            self.graph.add_node(sender_id)
            # Add edges to targets
            for target_id in targets:
                self.graph.add_edge(sender_id, target_id)

    def get_targets(self, player_id: str) -> List[str]:
        """
        Get list of players this player can send to.

        Args:
            player_id: The sender's ID

        Returns:
            List of target player IDs (successors in graph)
        """
        if player_id not in self.graph:
            return []
        return list(self.graph.successors(player_id))

    def get_senders(self, player_id: str) -> List[str]:
        """
        Get list of players that can send to this player.

        Args:
            player_id: The receiver's ID

        Returns:
            List of sender player IDs (predecessors in graph)
        """
        if player_id not in self.graph:
            return []
        return list(self.graph.predecessors(player_id))

    def can_send(self, sender_id: str, target_id: str) -> bool:
        """
        Check if sender can send to target.

        Args:
            sender_id: The sender's ID
            target_id: The target's ID

        Returns:
            True if edge exists from sender to target
        """
        return self.graph.has_edge(sender_id, target_id)

    def get_all_players(self) -> List[str]:
        """
        Get list of all player IDs in the topology.

        Returns:
            List of all node IDs
        """
        return list(self.graph.nodes())

    def get_execution_levels(self) -> List[List[str]]:
        """
        Compute execution levels via BFS from seed nodes.

        Seeds execute first (Level 0), then their successors (Level 1), etc.
        Players in the same level execute in parallel.

        Returns:
            List of levels, where each level is a list of player IDs.
            Empty list if no seeds configured.

        Example:
            topology:
              seeds: [coordinator]
              connections:
                coordinator: [player_1, player_2]
                player_1: [coordinator]
                player_2: [coordinator]

            get_execution_levels() -> [
                ['coordinator'],        # Level 0
                ['player_1', 'player_2']  # Level 1
            ]
        """
        if not self.seeds:
            # No seeds: all players in single level (parallel)
            all_players = self.get_all_players()
            return [all_players] if all_players else []

        # BFS from seeds
        levels: List[List[str]] = []
        visited: set = set()

        # Level 0: seeds
        current_level = [s for s in self.seeds if s in self.graph]
        if not current_level:
            return []

        levels.append(current_level)
        visited.update(current_level)

        # BFS to discover subsequent levels
        while True:
            next_level = []
            for node in current_level:
                for successor in self.graph.successors(node):
                    if successor not in visited:
                        next_level.append(successor)
                        visited.add(successor)

            if not next_level:
                break

            levels.append(next_level)
            current_level = next_level

        return levels

    def visualize(
        self, save_path: Optional[str] = None, title: str = "Topology"
    ) -> None:
        """
        Visualize the topology graph.

        Args:
            save_path: If provided, save figure to this path
            title: Title for the plot
        """
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 8))
        plt.title(title)

        # Use spring layout for positioning
        pos = nx.spring_layout(self.graph, k=2, iterations=50)

        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            node_color="lightblue",
            node_size=2000,
            alpha=0.9,
        )

        # Draw edges with arrows
        nx.draw_networkx_edges(
            self.graph,
            pos,
            edge_color="gray",
            arrows=True,
            arrowsize=20,
            arrowstyle="->",
            connectionstyle="arc3,rad=0.1",
        )

        # Draw labels
        nx.draw_networkx_labels(
            self.graph,
            pos,
            font_size=10,
            font_weight="bold",
        )

        plt.axis("off")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")

        plt.show()

    def to_ascii(self) -> str:
        """
        Generate ASCII representation of topology.

        Returns:
            ASCII string showing connections
        """
        lines = ["Topology Connections:", "=" * 40]
        for node in sorted(self.graph.nodes()):
            targets = self.get_targets(node)
            if targets:
                lines.append(f"  {node} -> {', '.join(sorted(targets))}")
            else:
                lines.append(f"  {node} -> (no targets)")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"TopologyGraph(nodes={len(self.graph.nodes())}, edges={len(self.graph.edges())})"
