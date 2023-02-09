import networkx as nx


class VNet:
    def __init__(self, underlying: nx.Graph, modelled: nx.DiGraph | None = None):
        self.underlying = underlying
        self.modelled = modelled
