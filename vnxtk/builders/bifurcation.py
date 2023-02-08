from .abstract import VNetBuilder
from vnxtk import VNet
import networkx as nx


class BifurcationVNetBuilder(VNetBuilder):
    def __init__(self, depth: int = 1, thinned: bool = False):
        self.depth = depth
        self.thinned = thinned

    def __call__(self) -> VNet:
        G = nx.Graph()
        return VNet(G)
