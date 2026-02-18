from abc import ABC, abstractmethod

class EventProducer(ABC):
    @abstractmethod
    def send_event(self, event: dict):
        pass