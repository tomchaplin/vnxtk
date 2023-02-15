from .abstract import VNetAlteration
from vnxtk import VNet
from random import sample


class RandomBoundary(VNetAlteration):
    def __init__(self, n_inlets: int = 1, n_outlets: int = 1):
        self.n_inlets = n_inlets
        self.n_outlets = n_outlets

    def __call__(self, V: VNet):
        node_list = list(V.underlying.nodes)
        new_boundary = sample(node_list, self.n_inlets + self.n_outlets)
        for node, ndt in V.underlying.nodes(data=True):
            ndt["external_current"] = (
                -1
                if node in new_boundary[0 : self.n_inlets]
                else 1
                if node in new_boundary[self.n_inlets :]
                else 0
            )
