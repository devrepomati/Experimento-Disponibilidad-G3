from kafka import KafkaProducer
import json
from reservas.adapters.event_producer import EventProducer

class KafkaEventProducer(EventProducer):
    def __init__(self, broker_url: str, topic: str):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=broker_url,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

    def send_event(self, event: dict):
        self.producer.send(self.topic, event)
        self.producer.flush()