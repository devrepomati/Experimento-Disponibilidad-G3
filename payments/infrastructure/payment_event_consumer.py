from kafka import KafkaConsumer
import json
from payments.adapters.payment_event_consumer_port import PaymentEventConsumerPort

class PaymentKafkaEventConsumer(PaymentEventConsumerPort):
    def __init__(self, broker_url: str, group_id: str):
        self.consumer = KafkaConsumer(
            "PAYMENTS",
            bootstrap_servers=broker_url,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True
        )

    def consume(self):
        for message in self.consumer:
            yield message.value