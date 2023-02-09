from .abstract import VNetBuilder
from vnxtk import VNet
import networkx as nx
import math
from enum import Enum


class GridBoundaryConditions(Enum):
    USUAL = 1
    CROSS_LOAD = 2


class GridVNetBuilder(VNetBuilder):
    def __init__(
        self,
        size: int = 1,
        boundary_conditions: GridBoundaryConditions = GridBoundaryConditions.USUAL,
    ):
        self.size = size
        self.boundary_conditions = boundary_conditions

    def _add_nodes(self, G):
        for i in range(self.size - 1):
            G.add_edges_from(
                [
                    ((i, j), (i + 1, j), {"length": 1, "diam": 1})
                    for j in range(self.size)
                ]
            )
        for j in range(self.size - 1):
            G.add_edges_from(
                [
                    ((i, j), (i, j + 1), {"length": 1, "diam": 1})
                    for i in range(self.size)
                ]
            )

    def _impose_boundary_conditions(self, G):
        for node, data in G.nodes(data=True):
            if self.boundary_conditions == GridBoundaryConditions.USUAL:
                data["external_current"] = (
                    1.0 / self.size
                    if node[0] == 0
                    else (-1.0 / self.size if node[0] == self.size - 1 else 0)
                )
            elif self.boundary_conditions == GridBoundaryConditions.CROSS_LOAD:
                data["external_current"] = (
                    1.0
                    if node == (0, 0)
                    else (-1.0 if node == (self.size - 1, self.size - 1) else 0)
                )

    def _add_spatial_information(self, G):
        for node, data in G.nodes(data=True):
            data["x"] = node[0]
            data["y"] = node[1]
            data["z"] = 1

    def __call__(self) -> VNet:
        G = nx.Graph()
        self._add_nodes(G)
        self._impose_boundary_conditions(G)
        self._add_spatial_information(G)
        G = nx.convert_node_labels_to_integers(G, label_attribute="grid_name")
        return VNet(G)
