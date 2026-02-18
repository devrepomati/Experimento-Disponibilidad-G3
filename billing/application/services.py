from billing.application.voting_coordinator import VotingCoordinator
from billing.domain.models import ReadyForPaymentEvent

def calculate_price_strategy1(base, context=None):
    # 10% de impuestos + 5 de fee fijo
    return round(base * 1.10 + 5, 2)

def calculate_price_strategy2(base, context=None):
    # 10% de impuestos + 5 de fee fijo, falla solo si context lo indica
    if context and context.get("fail_strategy2"):
        return round(base * 1.15 + 5, 2)  # error simulado
    return round(base * 1.10 + 5, 2)

def calculate_price_strategy3(base, context=None):
    # 10% de impuestos + 5 de fee fijo, falla solo si context lo indica
    if context and context.get("fail_strategy3"):
        return round(base * 1.10 + 10, 2)  # error simulado
    return round(base * 1.10 + 5, 2)

class BillingService:
    def __init__(self, voting_port):
        self.voting_port = voting_port

    def process_reserve(self, reserve_event):
        # Extraer información relevante de la reserva
        reserve = reserve_event.get("reserve", {})
        trips = reserve.get("trips", [])

        # Calcular el total de la reserva sumando los precios de todos los items
        total_price = 0.0
        for trip in trips:
            for item in trip.get("items", []):
                total_price += item.get("price", 0.0) * item.get("quantity", 1)

        # Extraer contexto de votación (por ejemplo, de un campo especial en el evento)
        voting_context = reserve_event.get("voting_context", {})

        # Usar el puerto de votación para el cálculo de cobros
        final_price = self.voting_port.calculate(total_price, context=voting_context)

        new_status = "CHECKING_OUT"

        # Construir el evento de dominio y devolver su mensaje serializable
        event = ReadyForPaymentEvent(
            reserve_id=reserve.get("reserve_id"),
            username=reserve.get("username"),
            final_price=final_price,
            status=new_status
        )
        return event.as_message()
