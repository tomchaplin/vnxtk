from abc import ABC, abstractmethod
from vnxtk import VNet


class VNetAlteration(ABC):
    @abstractmethod
    def __call__(self, V: VNet):
        pass
