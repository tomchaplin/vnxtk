from abc import ABC, abstractmethod
import networkx as nx


class VNetModel(ABC):
    @abstractmethod
    def __call__(self, underlying: nx.Graph) -> nx.DiGraph:
        pass
