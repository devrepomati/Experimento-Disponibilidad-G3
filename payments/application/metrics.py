from prometheus_client import Counter, CollectorRegistry

registry = CollectorRegistry()

payments_requests_total = Counter(
    "payments_requests_total",
    "Cantidad total de requests recibidos por el servicio de payments",
    registry=registry
)

payments_processed_total = Counter(
    "payments_processed_total",
    "Cantidad total de pagos procesados exitosamente",
    registry=registry
)

payments_dlq_total = Counter(
    "payments_dlq_total",
    "Cantidad total de pagos enviados a la DLQ",
    registry=registry
)