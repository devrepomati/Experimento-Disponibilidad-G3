from abc import ABC, abstractmethod

class PaymentEventConsumerPort(ABC):
    @abstractmethod
    def consume(self):
        """Consume events from the PAYMENTS topic and yield READY_FOR_PAYMENTS messages."""
        pass