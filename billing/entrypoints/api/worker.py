import time
from billing.infrastructure.kafka_consumer import KafkaEventConsumer
from billing.infrastructure.kafka_producer import KafkaEventProducer
from billing.application.services import BillingService, calculate_price_strategy1, calculate_price_strategy2, calculate_price_strategy3
from billing.application.voting_coordinator import VotingCoordinator

KAFKA_BROKER = "kafka:9092"
RESERVAS_TOPIC = "RESERVAS"
PAYMENTS_TOPIC = "PAYMENTS"
GROUP_ID = "billing-group"

def wait_for_kafka(broker_url, timeout=60):
    from kafka import KafkaProducer
    import sys
    start = time.time()
    while True:
        try:
            producer = KafkaProducer(bootstrap_servers=broker_url)
            producer.close()
            print("Kafka is available!")
            break
        except Exception:
            if time.time() - start > timeout:
                print("Timeout waiting for Kafka broker.", file=sys.stderr)
                sys.exit(1)
            print("Waiting for Kafka broker to be available...")
            time.sleep(2)

def main():
    from prometheus_client import CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
    from flask import Flask, Response
    import threading

    # Crear un registry personalizado y registrar solo las métricas de VotingCoordinator
    registry = CollectorRegistry()

    # Servidor Flask solo para /metrics
    metrics_app = Flask("metrics_app")

    @metrics_app.route("/metrics")
    def metrics():
        data = generate_latest(registry)
        return Response(data, mimetype=CONTENT_TYPE_LATEST)

    # Iniciar el servidor de métricas en un hilo aparte
    def run_metrics_server():
        metrics_app.run(host="0.0.0.0", port=8002, debug=False, use_reloader=False)

    threading.Thread(target=run_metrics_server, daemon=True).start()
    print("[Prometheus] Metrics server started on :8002/metrics (solo métricas de voting)")

    wait_for_kafka(KAFKA_BROKER)
    consumer = KafkaEventConsumer(KAFKA_BROKER, RESERVAS_TOPIC, GROUP_ID)
    producer = KafkaEventProducer(KAFKA_BROKER, PAYMENTS_TOPIC)
    # Composición de dependencias: inyectar VotingCoordinator como VotingPort
    voting_coordinator = VotingCoordinator([
        calculate_price_strategy1,
        calculate_price_strategy2,
        calculate_price_strategy3
    ], registry=registry)
    billing_service = BillingService(voting_coordinator)

    print("Billing worker started. Waiting for RESERVAS events...")
    for event in consumer.consume():
        print(f"Received event: {event}")
        payment_event = billing_service.process_reserve(event)
        print(f"Publishing payment event: {payment_event}")
        producer.send_event(payment_event)

if __name__ == "__main__":
    main()