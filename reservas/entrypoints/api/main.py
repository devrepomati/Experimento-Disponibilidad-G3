from flask import Flask, Blueprint, jsonify, request
from reservas.application.services import ReserveService
from reservas.infrastructure.kafka_producer import KafkaEventProducer

app = Flask(__name__)

# Blueprint para las rutas de reservas
reserve_bp = Blueprint("reserve", __name__)

# Composición de dependencias:
# Aquí se instancia la implementación concreta del productor de eventos (KafkaEventProducer)
# y se inyecta en el servicio de aplicación (ReserveService).
# El Blueprint utiliza el servicio, cumpliendo con la arquitectura hexagonal.
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "RESERVAS"
event_producer = KafkaEventProducer(KAFKA_BROKER, KAFKA_TOPIC)
reserve_service = ReserveService(event_producer)

@reserve_bp.route("/reserve", methods=["POST"])
def create_reserve_endpoint():
    data = request.get_json()
    reserve = reserve_service.create_reserve(data)
    return jsonify({"reserve_id": reserve.reserve_id, "status": "CREADA"}), 201

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# Registrar el Blueprint en la app principal
app.register_blueprint(reserve_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
