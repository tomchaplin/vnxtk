import networkx as nx


class VNet:
    def __init__(self, underlying: nx.Graph):
        self.underlying = underlying
