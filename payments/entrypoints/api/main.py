from flask import Flask, jsonify, Response
from payments.infrastructure.payment_repository import get_all_payments
from payments.application.metrics import registry
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/payments", methods=["GET"])
def get_payments():
    payments = get_all_payments()
    result = []
    for p in payments:
        result.append({
            "id": p.id,
            "event_type": p.event_type,
            "reserve_id": p.reserve_id,
            "username": p.username,
            "final_price": p.final_price,
            "status": p.status,
            "pay_id": p.pay_id,
            "pay_value": p.pay_value,
            "should_fail": p.should_fail,
            "created_at": p.created_at.isoformat() if p.created_at else None
        })
    return jsonify(result)

@app.route("/metrics")
def metrics():
    data = generate_latest(registry)
    return Response(data, mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004)
