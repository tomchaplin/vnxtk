from .abstract import VNetBuilder
from vnxtk import VNet
import networkx as nx
from scipy.spatial import Voronoi
import numpy as np


class VoronoiVNetBuilder(VNetBuilder):
    def __init__(self, n_points: int = 40, points=None):
        self.n_points = n_points
        self.points = points

    # Return a list of voronoi.vertices indexes whose coordinates are in the unit cube
    def _get_good_vertices(self):
        all_vs = self.voronoi.vertices
        return (
            np.argwhere(
                np.logical_and(np.all(all_vs >= 0, axis=1), np.all(all_vs <= 1, axis=1))
            )
            .flatten()
            .tolist()
        )

    def _compute_voronoi(self):
        points = (
            self.points if self.points is not None else np.random.rand(self.n_points, 2)
        )
        self.voronoi = Voronoi(points)

    def _add_edges(self, G):
        good_vs = self._get_good_vertices()
        for edge in self.voronoi.ridge_vertices:
            # Only add edges between vertices inside unit cube
            if any(v_idx not in good_vs for v_idx in edge):
                continue
            edge_len = np.linalg.norm(
                self.voronoi.vertices[edge[1]] - self.voronoi.vertices[edge[0]]
            )
            G.add_edge(edge[0], edge[1], diam=1, length=edge_len)

    def _add_spatial_information(self, G):
        good_vs = self._get_good_vertices()
        for v in good_vs:
            if not G.has_node(v):
                G.add_node(v)
            G.nodes[v]["x"] = self.voronoi.vertices[v, 0]
            G.nodes[v]["y"] = self.voronoi.vertices[v, 1]
            G.nodes[v]["z"] = 0

    # Unit source on left-most, unit sink on right-most
    def _impose_boundary_conditions(self, G):
        good_vs = self._get_good_vertices()
        source_idx = np.argmin(self.voronoi.vertices[good_vs, 0])
        source = good_vs[source_idx]
        sink_idx = np.argmax(self.voronoi.vertices[good_vs, 0])
        sink = good_vs[sink_idx]
        for node, data in G.nodes(data=True):
            data["external_current"] = (
                1 if node == source else -1 if node == sink else 0
            )

    def __call__(self) -> VNet:
        self._compute_voronoi()
        G = nx.Graph()
        self._add_edges(G)
        self._impose_boundary_conditions(G)
        self._add_spatial_information(G)
        G = nx.convert_node_labels_to_integers(G, label_attribute="grid_name")
        return VNet(G)
