"""Topology Graph Utilities for MASim.

This module provides NetworkX-based topology management for the multi-agent
simulation framework. It handles:
- Building directed graphs from topology configuration
- Querying targets (successors) and senders (predecessors)
- Computing execution levels from source nodes (BFS)
- Topology visualization

Usage:
    from masim.utils.topology import TopologyGraph

    graph = TopologyGraph(topology_config)
    targets = graph.get_targets("player_1")
    senders = graph.get_senders("player_1")
    levels = graph.get_execution_levels()  # Uses sources from config
    graph.visualize()
"""

from typing import Any, Dict, List, Optional
import os

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx


class TopologyGraph:
    """
    NetworkX-based topology graph for player communication.

    Wraps a directed graph where edges represent allowed message paths.
    An edge from A to B means A can send messages to B.

    Supports execution level computation via BFS from source nodes.

    Attributes:
        graph: The underlying NetworkX DiGraph
        sources: List of source player IDs for execution ordering
    """

    def __init__(self, topology_config: Optional[Dict[str, Any]] = None):
        """
        Initialize topology graph from configuration.

        Args:
            topology_config: Topology config dict with 'connections' and optional 'sources'.
                            If None, creates empty graph.
        """
        self.graph: nx.DiGraph = nx.DiGraph()
        self.sources: List[str] = []
        self.levels: List[List[str]] = []  # Cached execution levels
        # True once levels have been computed. Invalidated by topology mutations.
        self._levels_valid: bool = False
        # Hash of the last saved edge set — used to skip redundant diagram renders.
        # None means no diagram has been saved yet (forces first render).
        self._last_saved_edge_hash: Optional[frozenset] = None
        if topology_config:
            self._build_from_config(topology_config)

    def _build_from_config(self, config: Dict[str, Any]) -> None:
        """
        Build graph from topology configuration.

        Args:
            config: Dict with 'connections' mapping player_id -> [target_ids]
                   and optional 'sources' list for execution ordering
        """
        # Extract sources if present
        if "sources" in config:
            self.sources = list(config["sources"])

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
        Compute execution levels via BFS from source nodes.

        Result is cached after the first call. The cache is valid as long as
        the topology graph is not mutated (no add_edge / remove_edge calls).
        If the topology changes mid-simulation, call invalidate_levels_cache()
        before calling this method.

        Sources execute first (Level 0), then their successors (Level 1), etc.
        Players in the same level execute in parallel.

        Returns:
            List of levels, where each level is a list of player IDs.
            Empty list if no sources configured.

        Example:
            topology:
              sources: [coordinator]
              connections:
                coordinator: [player_1, player_2]
                player_1: [coordinator]
                player_2: [coordinator]

            get_execution_levels() -> [
                ['coordinator'],        # Level 0
                ['player_1', 'player_2']  # Level 1
            ]
        """
        if self._levels_valid:
            return self.levels

        if not self.sources:
            # No sources: all players in single level (parallel)
            all_players = self.get_all_players()
            self.levels = [all_players] if all_players else []
            self._levels_valid = True
            return self.levels

        # BFS from sources
        levels: List[List[str]] = []
        visited: set = set()

        # Level 0: sources
        current_level = [s for s in self.sources if s in self.graph]
        if not current_level:
            self.levels = []
            self._levels_valid = True
            return self.levels

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

        self.levels = levels
        self._levels_valid = True
        return self.levels

    def invalidate_levels_cache(self) -> None:
        """
        Invalidate the cached execution levels.

        Call this after any topology mutation (add_edge, remove_edge, etc.)
        so that the next get_execution_levels() call recomputes from scratch.
        """
        self._levels_valid = False
        self.levels = []

    # Edge style configurations
    FORWARD_EDGE_CONFIG = {
        "edge_color": "blue",
        "style": "solid",
        "width": 2.5,
        "arrowsize": 25,
        "alpha": 0.8,
    }
    BACKWARD_EDGE_CONFIG = {
        "edge_color": "red",
        "style": "dashed",
        "width": 1.5,
        "arrowsize": 20,
        "alpha": 0.7,
    }
    # Arc radius for curved edges (positive/negative to avoid overlap)
    FORWARD_ARC_RAD = 0.15
    BACKWARD_ARC_RAD = -0.25

    def visualize(
        self,
        save_path: str,
    ) -> None:
        """
        Visualize the topology graph with differentiated edge styles.

        Edge styles based on execution flow:
        - Forward edges (out): blue, solid, thick, curved upward
        - Backward edges (in): red, dashed, thin, curved downward

        The edges use different arc radii to avoid overlap.

        Args:
            save_path: Path to save the figure
        """
        plt.switch_backend("Agg")

        # Ensure levels are computed
        if not self.levels:
            self.get_execution_levels()

        fig, ax = plt.subplots(figsize=(12, 9))

        # Use spring layout for positioning
        pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)

        # Build node -> level mapping
        node_level = {}
        for level_idx, level_nodes in enumerate(self.levels):
            for node in level_nodes:
                node_level[node] = level_idx

        forward_edges = []  # out: blue, solid
        backward_edges = []  # in: red, dashed
        edge_levels = {}  # edge -> level label (source node's level)

        for u, v in self.graph.edges():
            u_level = node_level[u]
            v_level = node_level[v]
            # Edge label = source node's level (where the edge originates)
            edge_levels[(u, v)] = f"L{u_level}"
            if u_level <= v_level:
                forward_edges.append((u, v))
            else:
                backward_edges.append((u, v))

        # Identify source nodes (level 0)
        source_nodes = [n for n, lvl in node_level.items() if lvl == 0]
        non_source_nodes = [n for n, lvl in node_level.items() if lvl > 0]

        # Draw non-source nodes (lightblue)
        if non_source_nodes:
            nx.draw_networkx_nodes(
                self.graph,
                pos,
                ax=ax,
                nodelist=non_source_nodes,
                node_color="lightblue",
                node_size=2500,
                alpha=0.9,
                edgecolors="darkblue",
                linewidths=2,
            )

        # Draw source nodes (light red)
        if source_nodes:
            nx.draw_networkx_nodes(
                self.graph,
                pos,
                ax=ax,
                nodelist=source_nodes,
                node_color="mistyrose",
                node_size=2500,
                alpha=0.9,
                edgecolors="darkred",
                linewidths=2,
            )

        # Draw forward edges (out): blue, solid, thick
        if forward_edges:
            nx.draw_networkx_edges(
                self.graph,
                pos,
                ax=ax,
                edgelist=forward_edges,
                arrows=True,
                arrowstyle="-|>",
                connectionstyle=f"arc3,rad={self.FORWARD_ARC_RAD}",
                node_size=2500,
                **self.FORWARD_EDGE_CONFIG,
            )

        # Draw backward edges (in): red, dashed, thin
        if backward_edges:
            nx.draw_networkx_edges(
                self.graph,
                pos,
                ax=ax,
                edgelist=backward_edges,
                arrows=True,
                arrowstyle="-|>",
                connectionstyle=f"arc3,rad={self.BACKWARD_ARC_RAD}",
                node_size=2500,
                **self.BACKWARD_EDGE_CONFIG,
            )

        # Draw edge labels (level)
        # For forward edges
        if forward_edges:
            forward_labels = {e: edge_levels[e] for e in forward_edges}
            nx.draw_networkx_edge_labels(
                self.graph,
                pos,
                ax=ax,
                edge_labels=forward_labels,
                font_size=7,
                font_color="blue",
                label_pos=0.3,
                connectionstyle=f"arc3,rad={self.FORWARD_ARC_RAD}",
            )
        # For backward edges
        if backward_edges:
            backward_labels = {e: edge_levels[e] for e in backward_edges}
            nx.draw_networkx_edge_labels(
                self.graph,
                pos,
                ax=ax,
                edge_labels=backward_labels,
                font_size=7,
                font_color="red",
                label_pos=0.3,
                connectionstyle=f"arc3,rad={self.BACKWARD_ARC_RAD}",
            )

        # Draw node labels
        nx.draw_networkx_labels(
            self.graph,
            pos,
            ax=ax,
            font_size=8,
            font_weight="bold",
        )

        ax.axis("off")
        fig.tight_layout()

        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

    def save_round_diagram(
        self, output_dir: str, round_num: int, format: str = "png"
    ) -> Optional[str]:
        """
        Save topology diagram for a specific round — only when topology changes.

        Compares the current edge set hash against the last saved hash.
        If unchanged (static topology), skips the expensive spring_layout render
        entirely. For a typical static simulation, only 1 diagram is ever written
        regardless of save_diagram_interval.

        Args:
            output_dir: Directory to save the diagram
            round_num: Round number for naming
            format: Output format ("png" or "pdf")

        Returns:
            Path to saved diagram file, or None if topology was unchanged.
        """
        current_hash = frozenset(self.graph.edges())
        if current_hash == self._last_saved_edge_hash:
            return None  # topology unchanged — skip render

        self._last_saved_edge_hash = current_hash
        os.makedirs(output_dir, exist_ok=True)

        filename = f"topology_r{round_num:06d}.{format}"
        save_path = os.path.join(output_dir, filename)
        self.visualize(save_path=save_path)

        return save_path

    def __repr__(self) -> str:
        return f"TopologyGraph(nodes={len(self.graph.nodes())}, edges={len(self.graph.edges())})"
