class PaymentProcessingService:
    def __init__(self, payment_consumer, payment_processor):
        """
        payment_consumer: instancia de PaymentEventConsumerPort
        payment_processor: callable o servicio de dominio para procesar el pago
        """
        self.payment_consumer = payment_consumer
        self.payment_processor = payment_processor

    def process_ready_for_payments_events(self):
        from payments.application.metrics import payments_requests_total
        for event in self.payment_consumer.consume():
            payments_requests_total.inc()
            self.payment_processor(event)
