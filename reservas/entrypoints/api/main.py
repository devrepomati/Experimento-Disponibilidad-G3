from flask import Flask, Blueprint, jsonify, request
from reservas.application.services import ReserveService
from reservas.infrastructure.kafka_producer import KafkaEventProducer
import requests
import json
import hashlib
from kafka import KafkaProducer

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

IDEMPOTENCY_STORE_URL = "http://idempotency_store:5002/idempotency/records"
SECURITY_EVENTS_TOPIC = "security.events"
KAFKA_SECURITY_BROKER = "kafka:9092"

import jwt

SECRET_KEY = "supersecretkey"  # Debe ser igual al usado en authorizer

def require_jwt(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.actor_id = payload.get("actorId")
            if not request.actor_id:
                return jsonify({"error": "Invalid token: no actorId"}), 401
        except Exception as e:
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401
        return f(*args, **kwargs)
    return decorated

@reserve_bp.route("/reserve", methods=["POST"])
@require_jwt
def create_reserve_endpoint():
    data = request.get_json()
    headers = request.headers
    idempotency_key = headers.get("Idempotency-Key")
    trace_id = headers.get("X-request-Id")
    actor_id = request.actor_id  # Derivado del JWT
    reservation_id = data.get("reservation_id") or "N/A"
    operation_type = "create"
    canonical_payload = json.dumps(data, sort_keys=True, separators=(',', ':'))
    payload_hash = hashlib.sha256(canonical_payload.encode()).hexdigest()

    params = {
        "actorId": actor_id,
        "reservationId": reservation_id,
        "operationType": operation_type,
        "idempotencyKey": idempotency_key
    }
    resp = requests.get(IDEMPOTENCY_STORE_URL, params=params)
    if resp.status_code == 404:
        put_data = {
            "actorId": actor_id,
            "reservationId": reservation_id,
            "operationType": operation_type,
            "idempotencyKey": idempotency_key,
            "payloadHash": payload_hash,
            "ttlSeconds": 600
        }
        print(f"[RESERVAS] Nuevo registro: actor_id={actor_id}, reservation_id={reservation_id}, idempotency_key={idempotency_key}, payload_hash={payload_hash}, payload={data}")
        requests.put(IDEMPOTENCY_STORE_URL, json=put_data)
        reserve = reserve_service.create_reserve(data)
        return jsonify({"reserve_id": reserve.reserve_id, "status": "CREADA"}), 201
    else:
        record = resp.json()
        hash_old = record.get("payloadHash")
        print(f"[RESERVAS] Registro existente: actor_id={actor_id}, reservation_id={reservation_id}, idempotency_key={idempotency_key}, hash_old={hash_old}, hash_new={payload_hash}, payload={data}")
        if hash_old == payload_hash:
            print("[RESERVAS] Retry legítimo detectado")
            return jsonify({"status": "RETRY", "message": "Idempotent request"}), 200
        else:
            print("[RESERVAS] Conflicto de idempotencia detectado")
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_SECURITY_BROKER],
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            event = {
                "type": "IdempotencyConflictDetected",
                "actorId": actor_id,
                "reservationId": reservation_id,
                "operationType": operation_type,
                "idempotencyKey": idempotency_key,
                "hashOld": hash_old,
                "hashNew": payload_hash,
                "traceId": trace_id,
                "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z"
            }
            producer.send(SECURITY_EVENTS_TOPIC, event)
            producer.flush()
            # Registrar conflicto en IdempotencyStore (métrica Prometheus)
            try:
                requests.post("http://idempotency_store:5002/idempotency/conflict")
            except Exception as e:
                print(f"Error registrando conflicto en métricas: {e}")
            return jsonify({"status": "CONFLICT", "message": "Idempotency conflict detected"}), 409

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# Registrar el Blueprint en la app principal
app.register_blueprint(reserve_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
