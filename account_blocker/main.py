from flask import Flask, jsonify
import redis
from prometheus_client import generate_latest, Counter, Gauge
from kafka import KafkaConsumer
import threading
import json
import os

app = Flask(__name__)

# Configuración de Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Métricas Prometheus
REQUEST_COUNT = Counter('accountblocker_requests_total', 'Total requests to AccountBlocker')
LOCKED_ACCOUNTS = Gauge('locked_accounts', 'Current locked accounts')
ACCOUNT_BLOCKED_TOTAL = Counter('account_blocked_total', 'Total accounts blocked due to security events')

KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = "security.events"
BLOCK_TTL_SECONDS = 600  # 10 minutos

def kafka_consumer_thread():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        group_id='account_blocker_group'
    )
    for message in consumer:
        event = message.value
        if event.get("type") == "IdempotencyConflictDetected":
            actor_id = event.get("actorId")
            if actor_id:
                key = f"locked:{actor_id}"
                redis_client.setex(key, BLOCK_TTL_SECONDS, "1")
                LOCKED_ACCOUNTS.set(redis_client.dbsize())
                ACCOUNT_BLOCKED_TOTAL.inc()

@app.route('/accounts/<actor_id>/lock-status', methods=['GET'])
def lock_status(actor_id):
    REQUEST_COUNT.inc()
    key = f"locked:{actor_id}"
    ttl = redis_client.ttl(key)
    locked = ttl > 0
    expires_at = None
    if locked:
        expires_at = redis_client.ttl(key) + int(redis_client.time()[0])
    return jsonify({
        "locked": locked,
        "expiresAt": expires_at
    }), 200

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; version=0.0.4; charset=utf-8'}

if __name__ == '__main__':
    t = threading.Thread(target=kafka_consumer_thread, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5001)