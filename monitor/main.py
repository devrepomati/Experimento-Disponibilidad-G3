import os
import time
import threading
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# --- Configuración por ENV ---
POLL_INTERVAL_SECONDS = float("10")
REQUEST_TIMEOUT_SECONDS = float("0.5")

FAIL_THRESHOLD = int(os.getenv("FAIL_THRESHOLD", "1")) #con una sola falla, se reporta como degradado
RECOVER_THRESHOLD = int(os.getenv("RECOVER_THRESHOLD", "2")) # para considerarlo Ok debe pasar 2 health checks

TARGETS_ENV = os.getenv(
    "TARGETS",
    "billing=http://billing:8000/health,payments=http://payments:8000/health,reservas=http://reservas:8000/health"
)

def parse_targets(s: str):
    targets = {}
    for pair in s.split(","):
        pair = pair.strip()
        if not pair:
            continue
        name, url = pair.split("=", 1)
        targets[name.strip()] = url.strip()
    return targets

TARGETS = parse_targets(TARGETS_ENV)

# Memoria Estado
state_lock = threading.Lock()
targets_state = {
    name: {
        "url": url,
        "status": "UNKNOWN",           # OK | DEGRADED | UNKNOWN
        "last_ok_ts": None,
        "last_fail_ts": None,
        "consecutive_fails": 0,
        "consecutive_ok": 0,
        "last_error": None,
        "last_change_ts": None
    }
    for name, url in TARGETS.items()
}

def is_health_ok(resp: requests.Response) -> bool:
    if resp.status_code != 200:
        return False
    ctype = resp.headers.get("Content-Type", "")
    if "application/json" in ctype:
        try:
            data = resp.json()
            s = str(data.get("status", "")).lower()
            if s in ("ok", "healthy", "up"):
                return True
            if data.get("ok") is True:
                return True
        except Exception:
            return False
    return True

def set_status(name: str, new_status: str, error: str | None):
    now = time.time()
    st = targets_state[name]
    if st["status"] != new_status:
        print(f"[MONITOR] Service {name} status changed: {st['status']} -> {new_status} (error={error})")
        st["status"] = new_status
        st["last_change_ts"] = now
    st["last_error"] = error

def check_once():
    # Consultas en paralelo 
    session = requests.Session()

    def check_target(name, url):
        print(f"[MONITOR] Pinging {name} at {url} ...")
        try:
            r = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            ok = is_health_ok(r)
            print(f"[MONITOR] {name} responded: status_code={r.status_code}, health_ok={ok}")
            return (name, ok, None if ok else f"bad_status:{r.status_code}")
        except requests.Timeout:
            print(f"[MONITOR] {name} ping failed: timeout")
            return (name, False, "timeout")
        except requests.RequestException as e:
            print(f"[MONITOR] {name} ping failed: {type(e).__name__}")
            return (name, False, f"request_exception:{type(e).__name__}")

    threads = []
    results = []

    def runner(n, u):
        results.append(check_target(n, u))

    for name, url in TARGETS.items():
        t = threading.Thread(target=runner, args=(name, url), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    now = time.time()
    with state_lock:
        for name, ok, err in results:
            st = targets_state[name]

            if ok:
                st["consecutive_ok"] += 1
                st["consecutive_fails"] = 0
                st["last_ok_ts"] = now

                if st["consecutive_ok"] >= RECOVER_THRESHOLD:
                    set_status(name, "OK", None)
            else:
                st["consecutive_fails"] += 1
                st["consecutive_ok"] = 0
                st["last_fail_ts"] = now

                if st["consecutive_fails"] >= FAIL_THRESHOLD:
                    set_status(name, "DEGRADED", err)

def poll_loop():
    while True:
        start = time.time()
        check_once()
        elapsed = time.time() - start
        to_sleep = max(0.0, POLL_INTERVAL_SECONDS - elapsed)
        time.sleep(to_sleep)

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.get("/targets")
def targets():
    with state_lock:
        snapshot = {k: dict(v) for k, v in targets_state.items()}

        overall = "OK" if all(v["status"] == "OK" for v in snapshot.values()) and len(snapshot) > 0 else "DEGRADED"
        if any(v["status"] != "OK" for v in snapshot.values()):
            overall = "DEGRADED"
        if any(v["status"] == "UNKNOWN" for v in snapshot.values()):
            overall = "DEGRADED"

        return jsonify({
            "overall": overall,
            "poll_interval_seconds": POLL_INTERVAL_SECONDS,
            "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
            "fail_threshold": FAIL_THRESHOLD,
            "recover_threshold": RECOVER_THRESHOLD,
            "targets": snapshot
        })

@app.get("/health/targets")
def health_targets():
    with state_lock:
        result = []
        for name, st in targets_state.items():
            last_check = st["last_ok_ts"]
            if st["last_fail_ts"] and (not last_check or st["last_fail_ts"] > last_check):
                last_check = st["last_fail_ts"]
            if last_check:
                last_check_str = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(last_check))
            else:
                last_check_str = None
            result.append({
                "service": name,
                "lastStatus": st["status"],
                "lastCheck": last_check_str
            })
        return jsonify(result)

def start_background_poller():
    t = threading.Thread(target=poll_loop, daemon=True)
    t.start()

start_background_poller()

# Debug
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)