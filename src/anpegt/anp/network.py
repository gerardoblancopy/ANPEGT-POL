"""ANP network graph construction from YAML configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Union

import yaml

from anpegt.schema.anp import ANPEdge, ANPNode
from anpegt.util.logging import get_logger

logger = get_logger("anp.network")


class ANPNetwork:
    """In-memory representation of an ANP network graph."""

    def __init__(
        self,
        nodes: dict[str, ANPNode],
        edges: list[ANPEdge],
        clusters: dict[str, list[str]],
    ) -> None:
        self.nodes = nodes
        self.edges = edges
        self.clusters = clusters
        self.adjacency: dict[str, dict[str, float]] = {}
        self._build_adjacency()

    def _build_adjacency(self) -> None:
        """Build adjacency dict from edges.  adjacency[source][target] = weight."""
        self.adjacency = {}
        for edge in self.edges:
            self.adjacency.setdefault(edge.source_id, {})[edge.target_id] = edge.weight

    def get_node_ids(self) -> list[str]:
        """Return all node IDs in a stable order."""
        return list(self.nodes.keys())

    def get_cluster_node_ids(self, cluster_id: str) -> list[str]:
        """Return node IDs belonging to the given cluster."""
        return list(self.clusters.get(cluster_id, []))


def load_anp_network(config_path_or_dict: Union[str, Path, dict]) -> ANPNetwork:
    """Load an ANP network from a YAML file path or an already-parsed dict.

    Parameters
    ----------
    config_path_or_dict:
        Either a filesystem path to ``anp_network.yaml`` or a dict with keys
        ``nodes``, ``edges``, and ``clusters``.

    Returns
    -------
    ANPNetwork
    """
    if isinstance(config_path_or_dict, dict):
        raw = config_path_or_dict
    else:
        path = Path(config_path_or_dict)
        logger.info("Loading ANP network from %s", path)
        with open(path, "r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)

    # --- nodes ---------------------------------------------------------------
    nodes: dict[str, ANPNode] = {}
    for entry in raw.get("nodes", []):
        node = ANPNode(**entry)
        nodes[node.node_id] = node

    # --- edges ---------------------------------------------------------------
    edges: list[ANPEdge] = [ANPEdge(**e) for e in raw.get("edges", [])]

    # --- clusters ------------------------------------------------------------
    clusters: dict[str, list[str]] = {}
    for cluster_def in raw.get("clusters", []):
        cid = cluster_def["id"]
        clusters[cid] = [
            nid for nid, n in nodes.items() if n.cluster_id == cid
        ]

    logger.info(
        "ANP network loaded: %d nodes, %d edges, %d clusters",
        len(nodes),
        len(edges),
        len(clusters),
    )

    return ANPNetwork(nodes=nodes, edges=edges, clusters=clusters)
