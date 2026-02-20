import os
from payments.infrastructure.payment_event_consumer import PaymentKafkaEventConsumer
from payments.application.services import PaymentProcessingService
from payments.application.payment_processor import payment_processor
from payments.infrastructure.kafka_producer import KafkaEventProducer

if __name__ == "__main__":
    KAFKA_BROKER = "kafka:9092"
    GROUP_ID = "payments-group"
    DLQ_TOPIC = "PAYMENTS_DLQ"

    consumer = PaymentKafkaEventConsumer(KAFKA_BROKER, GROUP_ID)
    dlq_producer = KafkaEventProducer(KAFKA_BROKER, DLQ_TOPIC)
    # Crear un wrapper para pasar el producer a payment_processor
    def processor_with_dlq(event):
        return payment_processor(event, dlq_producer=dlq_producer)
    service = PaymentProcessingService(consumer, processor_with_dlq)
    service.process_ready_for_payments_events()
