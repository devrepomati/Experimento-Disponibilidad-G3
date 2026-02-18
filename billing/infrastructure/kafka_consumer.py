from kafka import KafkaConsumer
import json

class KafkaEventConsumer:
    def __init__(self, broker_url: str, topic: str, group_id: str):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=broker_url,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True
        )

    def consume(self):
        for message in self.consumer:
            yield message.value