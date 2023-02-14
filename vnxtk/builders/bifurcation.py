from .abstract import VNetBuilder
from vnxtk import VNet
import networkx as nx
import math
from enum import Enum


class BifurcationBoundaryConditions(Enum):
    USUAL = 1
    CROSS_LOAD = 2


class BifurcationBuilder(VNetBuilder):
    def __init__(
        self,
        depth: int = 1,
        thinned: bool = False,
        boundary_conditions: BifurcationBoundaryConditions = BifurcationBoundaryConditions.USUAL,
    ):
        self.depth = depth
        self.thinned = thinned
        self.boundary_conditions = boundary_conditions

    def _get_layer(self, layer):
        abs_layer = abs(layer)
        n_nodes = int(math.pow(2, self.depth - abs_layer))
        prev_layer = layer - 1 if layer > 0 else layer + 1
        return [
            (
                (prev_layer, 2 * i),
                (layer, i),
                {
                    "length": 1,
                    "diam": math.sqrt(1 / (2 * n_nodes)) if self.thinned else 1,
                },
            )
            for i in range(n_nodes)
        ] + [
            (
                (prev_layer, 2 * i + 1),
                (layer, i),
                {
                    "length": 1,
                    "diam": math.sqrt(1 / (2 * n_nodes)) if self.thinned else 1,
                },
            )
            for i in range(n_nodes)
        ]

    def _impose_boundary_conditions(self, G):
        for node, data in G.nodes(data=True):
            if self.boundary_conditions == BifurcationBoundaryConditions.USUAL:
                data["external_current"] = (
                    1
                    if node[0] == -self.depth
                    else (-1 if node[0] == self.depth else 0)
                )
            elif self.boundary_conditions == BifurcationBoundaryConditions.CROSS_LOAD:
                data["external_current"] = (
                    1
                    if node == (0, 0)
                    else (-1 if node == (0, int(math.pow(2, self.depth)) - 1) else 0)
                )

    def _add_spatial_information(self, G):
        n_central_nodes = int(math.pow(2, self.depth))
        central_gap = 1.0 / (math.pow(2, self.depth) - 1)
        for i in range(n_central_nodes):
            G.nodes[(0, i)]["x"] = 0
            G.nodes[(0, i)]["y"] = i * central_gap
            G.nodes[(0, i)]["z"] = 0
        for layer in range(1, self.depth + 1):
            n_nodes = int(math.pow(2, self.depth - layer))
            for i in range(n_nodes):
                G.nodes[(layer, i)]["x"] = layer
                G.nodes[(layer, i)]["y"] = (1 / 2) * (
                    G.nodes[(layer - 1, 2 * i)]["y"]
                    + G.nodes[(layer - 1, 2 * i + 1)]["y"]
                )
                G.nodes[(layer, i)]["z"] = 0
                G.nodes[(-layer, i)]["x"] = -layer
                G.nodes[(-layer, i)]["y"] = (1 / 2) * (
                    G.nodes[(layer - 1, 2 * i)]["y"]
                    + G.nodes[(layer - 1, 2 * i + 1)]["y"]
                )
                G.nodes[(-layer, i)]["z"] = 0

    def _add_edges(self, G):
        for i in range(1, self.depth + 1):
            G.add_edges_from(self._get_layer(i))
            G.add_edges_from(self._get_layer(-i))

    def __call__(self) -> VNet:
        G = nx.Graph()
        self._add_edges(G)
        self._impose_boundary_conditions(G)
        self._add_spatial_information(G)
        G = nx.convert_node_labels_to_integers(G, label_attribute="bifur_name")
        return VNet(G)
