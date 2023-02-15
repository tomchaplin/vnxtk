from .abstract import VNetAlteration
from vnxtk import VNet
from random import sample
from typing import Tuple


class RandomBoundary(VNetAlteration):
    def __init__(self, n_nodes: int = 1):
        self.n_nodes = n_nodes
        pass

    def __call__(self, V: VNet):
        node_list = list(V.underlying.nodes)
        new_boundary = sample(node_list, 2 * self.n_nodes)
        for node, ndt in V.underlying.nodes(data=True):
            ndt["external_current"] = (
                -1
                if node in new_boundary[0 : self.n_nodes]
                else 1
                if node in new_boundary[self.n_nodes :]
                else 0
            )
