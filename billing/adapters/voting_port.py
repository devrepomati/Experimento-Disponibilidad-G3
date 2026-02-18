from abc import ABC, abstractmethod

class VotingPort(ABC):
    @abstractmethod
    def calculate(self, base_price, context=None):
        pass