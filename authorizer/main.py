from flask import Flask, request, jsonify
import jwt
import datetime

app = Flask(__name__)

SECRET_KEY = "supersecretkey"  # En producción, usar variable de entorno

@app.route("/token", methods=["POST"])
def generate_token():
    data = request.get_json()
    actor_id = data.get("actorId")
    if not actor_id:
        return jsonify({"error": "actorId required"}), 400
    payload = {
        "actorId": actor_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)