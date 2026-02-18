from locust import HttpUser, task, between
import random

class ReservasUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def crear_reserva(self):
        voting_context = {}
        if random.random() < 0.1:
            voting_context["fail_strategy2"] = True
        if random.random() < 0.1:
            voting_context["fail_strategy3"] = True

        payload = {
            "username": f"user{random.randint(1, 10000)}",
            "identificacion": str(random.randint(100000, 999999)),
            "trips": [
                {
                    "trip_id": f"trip-{random.randint(1, 1000)}",
                    "status": "BORRADOR",
                    "operator": {
                        "operator_id": "op-001",
                        "name": "Hotel Estelar",
                        "operator_type": "HOTEL"
                    },
                    "items": [
                        {
                            "item_id": "item-001",
                            "description": "Habitación doble",
                            "quantity": 2,
                            "price": 150.0
                        }
                    ]
                }
            ],
            "voting_context": voting_context
        }
        self.client.post("/reservas/reserve", json=payload)