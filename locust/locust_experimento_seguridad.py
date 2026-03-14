import time
import uuid
import requests
from locust import HttpUser, task, between
from locust.exception import StopUser

AUTHORIZER_URL = "http://authorizer:7000/token"
ACCOUNT_BLOCKER_URL = "http://account_blocker:5001/accounts/{actorId}/lock-status"
RESERVAS_URL = "/reservas/reserve"

def get_jwt(actor_id):
    resp = requests.post(AUTHORIZER_URL, json={"actorId": actor_id}, timeout=3)
    return resp.json()["token"]

def poll_lock_status(actor_id, timeout=15):
    url = ACCOUNT_BLOCKER_URL.format(actorId=actor_id)
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200 and resp.json().get("locked"):
                return True
        except Exception as e:
            print(f"[WARN] Error consultando lock-status: {e}")
        time.sleep(0.5)
    return False

class ASR1_C1_RetryLegitimo(HttpUser):
    wait_time = between(1, 2)
    def on_start(self):
        self.actor_id = f"usuario-c1-{uuid.uuid4()}"
        self.token = get_jwt(self.actor_id)
        self.key = f"key-c1-{uuid.uuid4()}"
        self.payload = {"valor": 100, "concepto": "pago"}

    @task
    def retry_legitimo(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Idempotency-Key": self.key,
            "X-request-Id": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }
        # Primer request
        print(f"[Locust][ASR1_C1_step1_create] POST {RESERVAS_URL} headers={headers} payload={self.payload}")
        resp1 = self.client.post(RESERVAS_URL, json=self.payload, headers=headers, name="ASR1_C1_step1_create")
        print(f"[Locust][ASR1_C1_step1_create] Status: {resp1.status_code} Response: {resp1.text}")
        print(f"[Locust][ASR1_C1_step2_retry] POST {RESERVAS_URL} headers={headers} payload={self.payload}")
        resp2 = self.client.post(RESERVAS_URL, json=self.payload, headers=headers, name="ASR1_C1_step2_retry")
        print(f"[Locust][ASR1_C1_step2_retry] Status: {resp2.status_code} Response: {resp2.text}")
        # No assertions ni StopUser

class ASR1_C2_Suplantacion(HttpUser):
    wait_time = between(1, 2)
    def on_start(self):
        # Usar actor_id y key fijos para forzar conflicto de idempotencia
        self.actor_id = "usuario-c2-conflicto"
        self.token = get_jwt(self.actor_id)
        self.key = "key-c2-conflicto"
        self.payload1 = {"valor": 200, "concepto": "pago"}
        self.payload2 = {"valor": 999, "concepto": "pago"}

    @task
    def suplantacion(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Idempotency-Key": self.key,
            "X-request-Id": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }
        # Primer request
        print(f"[Locust][ASR1_C2_step1_create] POST {RESERVAS_URL} headers={headers} payload={self.payload1}")
        resp1 = self.client.post(RESERVAS_URL, json=self.payload1, headers=headers, name="ASR1_C2_step1_create")
        print(f"[Locust][ASR1_C2_step1_create] Status: {resp1.status_code} Response: {resp1.text}")
        print(f"[Locust][ASR1_C2_step2_conflict] POST {RESERVAS_URL} headers={headers} payload={self.payload2}")
        resp2 = self.client.post(RESERVAS_URL, json=self.payload2, headers=headers, name="ASR1_C2_step2_conflict")
        print(f"[Locust][ASR1_C2_step2_conflict] Status: {resp2.status_code} Response: {resp2.text}")
        # Polling y verificación de bloqueo omitidos para solo generar tráfico
        headers_contencion = headers.copy()
        headers_contencion["Idempotency-Key"] = f"key-c2-cont-{uuid.uuid4()}"
        print(f"[Locust][ASR1_C2_step3_containment] POST {RESERVAS_URL} headers={headers_contencion} payload={self.payload1}")
        resp3 = self.client.post(RESERVAS_URL, json=self.payload1, headers=headers_contencion, name="ASR1_C2_step3_containment")
        print(f"[Locust][ASR1_C2_step3_containment] Status: {resp3.status_code} Response: {resp3.text}")
        # No assertions ni StopUser

class ASR1_C3_ControlFalsoPositivo(HttpUser):
    wait_time = between(1, 2)
    def on_start(self):
        self.actor_id = f"usuario-c3-{uuid.uuid4()}"
        self.token = get_jwt(self.actor_id)
        self.key = f"key-c3-{uuid.uuid4()}"
        self.payload1 = {"valor": 300, "concepto": "pago"}
        self.payload2 = {"concepto": "pago", "valor": 300}

    @task
    def control_falso_positivo(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Idempotency-Key": self.key,
            "X-request-Id": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }
        # Primer request
        print(f"[Locust][ASR1_C3_step1_create] POST {RESERVAS_URL} headers={headers} payload={self.payload1}")
        resp1 = self.client.post(RESERVAS_URL, json=self.payload1, headers=headers, name="ASR1_C3_step1_create")
        print(f"[Locust][ASR1_C3_step1_create] Status: {resp1.status_code} Response: {resp1.text}")
        print(f"[Locust][ASR1_C3_step2_retry_reordered] POST {RESERVAS_URL} headers={headers} payload={self.payload2}")
        resp2 = self.client.post(RESERVAS_URL, json=self.payload2, headers=headers, name="ASR1_C3_step2_retry_reordered")
        print(f"[Locust][ASR1_C3_step2_retry_reordered] Status: {resp2.status_code} Response: {resp2.text}")
        # No assertions ni StopUser

class ASR1_C4_Evasion(HttpUser):
    wait_time = between(1, 2)
    def on_start(self):
        self.actor_id = f"usuario-c4-{uuid.uuid4()}"
        self.token = get_jwt(self.actor_id)
        self.key1 = f"key-c4-1-{uuid.uuid4()}"
        self.key2 = f"key-c4-2-{uuid.uuid4()}"
        self.payload1 = {"valor": 400, "concepto": "pago"}
        self.payload2 = {"valor": 999, "concepto": "pago"}

    @task
    def evasion(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-request-Id": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }
        # Primer request con key1
        headers["Idempotency-Key"] = self.key1
        print(f"[Locust][ASR1_C4_step1_create] POST {RESERVAS_URL} headers={headers} payload={self.payload1}")
        resp1 = self.client.post(RESERVAS_URL, json=self.payload1, headers=headers, name="ASR1_C4_step1_create")
        print(f"[Locust][ASR1_C4_step1_create] Status: {resp1.status_code} Response: {resp1.text}")
        headers["Idempotency-Key"] = self.key2
        print(f"[Locust][ASR1_C4_step2_new_key] POST {RESERVAS_URL} headers={headers} payload={self.payload2}")
        resp2 = self.client.post(RESERVAS_URL, json=self.payload2, headers=headers, name="ASR1_C4_step2_new_key")
        print(f"[Locust][ASR1_C4_step2_new_key] Status: {resp2.status_code} Response: {resp2.text}")
        # No assertions ni StopUser

class DefaultUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def run_all(self):
        # Escenario de retry legítimo
        actor_id = f"usuario-c1-{uuid.uuid4()}"
        token = get_jwt(actor_id)
        key = f"key-c1-{uuid.uuid4()}"
        payload = {"valor": 100, "concepto": "pago"}
        headers = {
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": key,
            "X-request-Id": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }
        print(f"[DefaultUser][ASR1_C1_step1_create] POST {RESERVAS_URL} headers={headers} payload={payload}")
        resp1 = self.client.post(RESERVAS_URL, json=payload, headers=headers, name="ASR1_C1_step1_create")
        print(f"[DefaultUser][ASR1_C1_step1_create] Status: {resp1.status_code} Response: {resp1.text}")
        print(f"[DefaultUser][ASR1_C1_step2_retry] POST {RESERVAS_URL} headers={headers} payload={payload}")
        resp2 = self.client.post(RESERVAS_URL, json=payload, headers=headers, name="ASR1_C1_step2_retry")
        print(f"[DefaultUser][ASR1_C1_step2_retry] Status: {resp2.status_code} Response: {resp2.text}")

        # Escenario de suplantación
        actor_id2 = "usuario-c2-conflicto"
        token2 = get_jwt(actor_id2)
        key2 = "key-c2-conflicto"
        payload1 = {"valor": 200, "concepto": "pago"}
        payload2 = {"valor": 999, "concepto": "pago"}
        headers2 = {
            "Authorization": f"Bearer {token2}",
            "Idempotency-Key": key2,
            "X-request-Id": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }
        print(f"[DefaultUser][ASR1_C2_step1_create] POST {RESERVAS_URL} headers={headers2} payload={payload1}")
        resp3 = self.client.post(RESERVAS_URL, json=payload1, headers=headers2, name="ASR1_C2_step1_create")
        print(f"[DefaultUser][ASR1_C2_step1_create] Status: {resp3.status_code} Response: {resp3.text}")
        print(f"[DefaultUser][ASR1_C2_step2_conflict] POST {RESERVAS_URL} headers={headers2} payload={payload2}")
        resp4 = self.client.post(RESERVAS_URL, json=payload2, headers=headers2, name="ASR1_C2_step2_conflict")
        print(f"[DefaultUser][ASR1_C2_step2_conflict] Status: {resp4.status_code} Response: {resp4.text}")
        headers_contencion = headers2.copy()
        headers_contencion["Idempotency-Key"] = f"key-c2-cont-{uuid.uuid4()}"
        print(f"[DefaultUser][ASR1_C2_step3_containment] POST {RESERVAS_URL} headers={headers_contencion} payload={payload1}")
        resp5 = self.client.post(RESERVAS_URL, json=payload1, headers=headers_contencion, name="ASR1_C2_step3_containment")
        print(f"[DefaultUser][ASR1_C2_step3_containment] Status: {resp5.status_code} Response: {resp5.text}")

        # Terminar el usuario después de ejecutar ambos escenarios
        from locust.exception import StopUser
        raise StopUser()
