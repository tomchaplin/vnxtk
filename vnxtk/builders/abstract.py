from abc import ABC, abstractmethod
from vnxtk import VNet


class VNetBuilder(ABC):
    @abstractmethod
    def __call__(self) -> VNet:
        pass
