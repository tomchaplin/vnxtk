from .abstract import VNetAlteration
from vnxtk import VNet
from typing import Tuple
from random import sample, randint

# NOTE: This class doesn't update modelled for you!


class RandomRewiring(VNetAlteration):
    def __init__(self, m: int):
        # Attempt to make m edge swaps
        self.m = m

    @staticmethod
    def swap_edges(
        V: VNet, edge0: Tuple[int, int], edge1: Tuple[int, int], idxs: Tuple[int, int]
    ) -> bool:
        new_edge0 = sorted((edge0[1 - idxs[0]], edge1[idxs[1]]))
        new_edge1 = sorted((edge1[1 - idxs[1]], edge0[idxs[0]]))
        # If edges already exist, can't swap, unless we are just swapping edge0 <-> edge1
        if V.underlying.has_edge(*new_edge0) and new_edge0 != edge1:
            return False
        if V.underlying.has_edge(*new_edge1) and new_edge1 != edge0:
            return False
        # Save data
        edge0_dt = V.underlying[edge0[0]][edge0[1]]
        edge1_dt = V.underlying[edge1[0]][edge1[1]]
        # Delete old edges
        V.underlying.remove_edge(*edge0)
        V.underlying.remove_edge(*edge1)
        # Add new edges
        V.underlying.add_edge(*new_edge0, **edge0_dt)
        V.underlying.add_edge(*new_edge1, **edge1_dt)
        return True

    def __call__(self, V: VNet):
        for _ in range(self.m):
            edges = sample(list(V.underlying.edges), 2)
            idxs = (randint(0, 1), randint(0, 1))
            RandomRewiring.swap_edges(V, edges[0], edges[1], idxs)
