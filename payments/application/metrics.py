from prometheus_client import Counter

payments_requests_total = Counter(
    "payments_requests_total",
    "Cantidad total de requests recibidos por el servicio de payments"
)

payments_processed_total = Counter(
    "payments_processed_total",
    "Cantidad total de pagos procesados exitosamente"
)

payments_dlq_total = Counter(
    "payments_dlq_total",
    "Cantidad total de pagos enviados a la DLQ"
)
