from .abstract import VNetAlteration
from vnxtk import VNet
from typing import Tuple
from random import sample, randint


class RandomRewiring(VNetAlteration):
    def __init__(self, m: int):
        # Attempt to make m edge swaps
        self.m = m

    # TODO: Implement
    @staticmethod
    def swap_edges(
        V: VNet, edge0: Tuple[int, int], edge1: Tuple[int, int], idxs: Tuple[int, int]
    ) -> bool:
        new_edge0 = (edge0[1 - idxs[0]], edge1[idxs[1]])
        new_edge1 = (edge1[1 - idxs[1]], edge0[idxs[0]])
        # TODO: Check that swap can take place
        # TODO: Figure out correct orientation in modelled
        # TODO: Execute swap in underlying and modelled
        return False

    # TODO: Implement
    def __call__(self, V: VNet):
        for i in range(self.m):
            edges = sample(list(V.underlying.edges), 2)
            idxs = (randint(0, 1), randint(0, 1))
            RandomRewiring.swap_edges(V, edges[0], edges[1], idxs)
