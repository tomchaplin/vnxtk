from .abstract import VNetAlteration
from vnxtk import VNet
from random import random, randint
from typing import Tuple


class RandomRemoval(VNetAlteration):
    def __init__(self, p: float | None = None, m: int | None = None):
        # Remove each edge with probability p
        self.p = p
        # Remove m edges at random
        self.m = m
        if (p is None and m is None) or not ((p is None) or (m is None)):
            raise ValueError("Must provide exactly one of p or m")

    def __call__(self, V: VNet):
        if self.p is not None:
            RandomRemoval.indep_random_edge_removal(V, self.p)
        elif self.m is not None:
            RandomRemoval.m_random_edge_removal(V, self.m)

    @staticmethod
    def remove_edge(V: VNet, edge: Tuple[int, int]):
        V.underlying.remove_edge(*edge)
        if V.modelled is None:
            return
        if V.modelled.has_edge(*edge):
            V.modelled.remove_edge(*edge)
        else:
            V.modelled.remove_edge(edge[1], edge[0])

    @staticmethod
    def indep_random_edge_removal(V: VNet, p: float):
        for edge in V.underlying.edges:
            remove = random() <= p
            if remove:
                RandomRemoval.remove_edge(V, edge)

    @staticmethod
    def m_random_edge_removal(V: VNet, m: int):
        if m <= 0:
            return
        nedges = V.underlying.number_of_edges()
        edge_idx_to_remove = randint(0, nedges - 1)
        edge_to_remove = list(V.underlying.edges)[edge_idx_to_remove]
        RandomRemoval.remove_edge(V, edge_to_remove)
        RandomRemoval.m_random_edge_removal(V, m - 1)
