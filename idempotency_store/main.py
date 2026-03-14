from flask import Flask, request, jsonify
import redis
import hashlib
import time
from prometheus_client import generate_latest, Counter, Gauge

app = Flask(__name__)

# Métrica de conflictos de idempotencia
IDEMPOTENCY_CONFLICT_TOTAL = Counter('idempotency_conflict_total', 'Total idempotency conflicts detected')

# Configuración de Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Métricas Prometheus
REQUEST_COUNT = Counter('idempotency_requests_total', 'Total requests to IdempotencyStore')
RECORDS_GAUGE = Gauge('idempotency_records', 'Current idempotency records stored')

@app.route('/idempotency/records', methods=['PUT'])
def put_record():
    REQUEST_COUNT.inc()
    data = request.json
    key = f"{data['actorId']}:{data['reservationId']}:{data['operationType']}:{data['idempotencyKey']}"
    payload_hash = data['payloadHash']
    ttl = int(data.get('ttlSeconds', 3600))
    record = {
        'payloadHash': payload_hash,
        'createdAt': int(time.time()),
        'expiresAt': int(time.time()) + ttl
    }
    redis_client.hmset(key, record)
    redis_client.expire(key, ttl)
    RECORDS_GAUGE.set(redis_client.dbsize())
    return jsonify({'status': 'ok'}), 201

@app.route('/idempotency/records', methods=['GET'])
def get_record():
    REQUEST_COUNT.inc()
    actorId = request.args.get('actorId')
    reservationId = request.args.get('reservationId')
    operationType = request.args.get('operationType')
    idempotencyKey = request.args.get('idempotencyKey')
    key = f"{actorId}:{reservationId}:{operationType}:{idempotencyKey}"
    record = redis_client.hgetall(key)
    if not record:
        return jsonify({'error': 'not found'}), 404
    # Decodificar bytes a string
    record = {k.decode(): v.decode() for k, v in record.items()}
    return jsonify(record), 200

@app.route('/idempotency/conflict', methods=['POST'])
def register_conflict():
    IDEMPOTENCY_CONFLICT_TOTAL.inc()
    return jsonify({'status': 'conflict registered'}), 201

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; version=0.0.4; charset=utf-8'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
