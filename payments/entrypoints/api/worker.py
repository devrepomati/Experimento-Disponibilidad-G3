import os
from payments.infrastructure.payment_event_consumer import PaymentKafkaEventConsumer
from payments.application.services import PaymentProcessingService
from payments.application.payment_processor import payment_processor
from payments.infrastructure.kafka_producer import KafkaEventProducer

if __name__ == "__main__":
    import threading
    from flask import Flask, Response
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

    KAFKA_BROKER = "kafka:9092"
    GROUP_ID = "payments-group"
    DLQ_TOPIC = "PAYMENTS_DLQ"

    # Servidor Flask para exponer /metrics en el puerto 8005
    metrics_app = Flask("metrics_app")

    @metrics_app.route("/metrics")
    def metrics():
        data = generate_latest()
        return Response(data, mimetype=CONTENT_TYPE_LATEST)

    def run_metrics_server():
        metrics_app.run(host="0.0.0.0", port=8005, debug=False, use_reloader=False)

    threading.Thread(target=run_metrics_server, daemon=True).start()
    print("[Prometheus] Metrics server started on :8005/metrics (worker payments)")

    consumer = PaymentKafkaEventConsumer(KAFKA_BROKER, GROUP_ID)
    dlq_producer = KafkaEventProducer(KAFKA_BROKER, DLQ_TOPIC)
    # Crear un wrapper para pasar el producer a payment_processor
    def processor_with_dlq(event):
        return payment_processor(event, dlq_producer=dlq_producer)
    service = PaymentProcessingService(consumer, processor_with_dlq)
    service.process_ready_for_payments_events()
