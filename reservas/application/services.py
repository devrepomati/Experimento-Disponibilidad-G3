from reservas.domain.models import Reserve, Trip, TripItem, TripOperator, ReserveStatus, TripStatus, TripOperatorType
import uuid

class ReserveService:
    def __init__(self, event_producer):
        self.event_producer = event_producer

    def create_reserve(self, data):
        username = data.get("username")
        identificacion = data.get("identificacion")
        trips_data = data.get("trips", [])

        trips = []
        for t in trips_data:
            operator_data = t.get("operator")
            operator = TripOperator(
                operator_id=operator_data["operator_id"],
                name=operator_data["name"],
                operator_type=TripOperatorType(operator_data["operator_type"])
            )
            items = [
                TripItem(
                    item_id=item["item_id"],
                    description=item["description"],
                    quantity=item["quantity"],
                    price=item["price"]
                )
                for item in t.get("items", [])
            ]
            trip = Trip(
                trip_id=t["trip_id"],
                operator=operator,
                items=items,
                status=TripStatus(t.get("status", "BORRADOR"))
            )
            trips.append(trip)

        reserve_id = str(uuid.uuid4())
        reserve = Reserve(
            reserve_id=reserve_id,
            username=username,
            identificacion=identificacion,
            trips=trips,
            status=ReserveStatus.CREADA
        )

        if self.event_producer:
            event = {
                "event_type": "RESERVE_CREATED",
                "reserve": reserve_to_event_payload(reserve)
            }
            # Se incluye en el request una variable para indicar si se debe o no simular fallas en el calculo.
            if data.get("voting_context") is not None:
                event["voting_context"] = data.get("voting_context")
            self.event_producer.send_event(event)

        return reserve

#evento reserva creada
def reserve_to_event_payload(reserve: Reserve):
    return {
        "reserve_id": reserve.reserve_id,
        "username": reserve.username,
        "identificacion": reserve.identificacion,
        "status": reserve.status,
        "trips": [
            {
                "trip_id": trip.trip_id,
                "status": trip.status,
                "operator": {
                    "operator_id": trip.operator.operator_id,
                    "name": trip.operator.name,
                    "operator_type": trip.operator.operator_type
                },
                "items": [
                    {
                        "item_id": item.item_id,
                        "description": item.description,
                        "quantity": item.quantity,
                        "price": item.price
                    }
                    for item in trip.items
                ]
            }
            for trip in reserve.trips
        ]
    }