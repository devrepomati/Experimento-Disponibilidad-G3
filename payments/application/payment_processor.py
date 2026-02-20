import requests
import random
from payments.infrastructure.payment_repository import add_payment, init_db

# Inicializar la base de datos al importar el módulo
init_db()

def payment_processor(event, dlq_producer=None):
    """
    Procesa el evento realizando un POST al API externo.
    Persiste el resultado y envía a DLQ si hay error.
    """
    from payments.application.metrics import payments_processed_total, payments_dlq_total

    pay_id = event.get("pay_id")
    pay_value = event.get("pay_value", 99)
    should_fail = random.random() < 0.05  # 5% de probabilidad

    payload = {
        "pay_id": pay_id,
        "pay_value": pay_value,
        "should_fail": should_fail
    }

    # Realizar POST
    try:
        response = requests.post("http://wiremock:8080/api/pay", json=payload)
        response_text = response.text

        # Determinar status según respuesta
        if "ERROR" in response_text:
            status = "PAYMENT_IN_PROCESS"
            # Enviar a DLQ solo si hay error y si se pasó el producer
            if dlq_producer is not None:
                dlq_producer.send_event(event)
                payments_dlq_total.inc()
        else:
            status = "PAYED"
            payments_processed_total.inc()
    except requests.exceptions.RequestException as e:
        # Error de conexión u otro error de requests: enviar a DLQ
        status = "PAYMENT_IN_PROCESS"
        if dlq_producer is not None:
            dlq_producer.send_event(event)
            payments_dlq_total.inc()
        response_text = f"EXCEPTION: {e}"
        response = None

    # Guardar en base de datos
    payment_data = {
        "event_type": event.get("event_type"),
        "reserve_id": event.get("reserve_id"),
        "username": event.get("username"),
        "final_price": event.get("final_price"),
        "status": status,
        "pay_id": pay_id,
        "pay_value": pay_value,
        "should_fail": str(should_fail).lower()
    }
    add_payment(payment_data)

    print(f"POST {payload} => {response.status_code} {response_text} | status: {status}")
    return response