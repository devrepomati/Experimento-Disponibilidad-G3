import concurrent.futures
from billing.adapters.voting_port import VotingPort
import threading
from prometheus_client import Counter, Histogram

class VotingCoordinator(VotingPort):
    _lock = threading.Lock()

    def __init__(self, strategies, registry=None):
        """
        strategies: lista de callables que reciben base_price y retornan el cálculo.
        """
        self.strategies = strategies
        # Prometheus metrics enfocadas en la hipótesis experimental
        self.requests_total = Counter(
            "voting_requests_total",
            "Cantidad total de solicitudes procesadas por el VotingCoordinator",
            registry=registry
        )
        self.requests_marked_for_error_total = Counter(
            "voting_requests_marked_for_error_total",
            "Cantidad de solicitudes marcadas para generar error (fail_strategy2 o fail_strategy3)",
            registry=registry
        )
        self.inconsistencies_detected = Counter(
            "voting_inconsistencies_detected",
            "Cantidad de requests con discrepancia entre estrategias",
            registry=registry
        )
        self.inconsistencies_masked = Counter(
            "voting_inconsistencies_masked",
            "Cantidad de requests donde el voting enmascaró la inconsistencia (2 de 3)",
            registry=registry
        )
        self.inconsistencies_unmasked = Counter(
            "voting_inconsistencies_unmasked",
            "Cantidad de requests donde no se pudo enmascarar (fallback, los 3 difieren)",
            registry=registry
        )
        self.detection_duration = Histogram(
            "voting_detection_duration_seconds",
            "Latencia de detección/enmascaramiento de inconsistencias en segundos",
            registry=registry
        )

    def calculate(self, base_price, context=None):
        import os
        import random
        # Incrementa el contador de solicitudes totales
        self.requests_total.inc()
        # Si la solicitud está marcada para error, incrementa el contador correspondiente
        if context and (context.get("fail_strategy2") or context.get("fail_strategy3")):
            self.requests_marked_for_error_total.inc()
        with self.detection_duration.time():
            voting_enabled = os.getenv("VOTING_ENABLED", "").lower() in ("1", "true", "yes")
            if voting_enabled:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(strategy, base_price, context) for strategy in self.strategies]
                    results = [f.result() for f in concurrent.futures.as_completed(futures)]

                with self._lock:
                    unique_results = set(results)
                    has_inconsistency = len(unique_results) > 1
                    masked = False
                    unmasked = False
                    final_value = None

                    # Voting 2 de 3 (incluyendo -1 como valor válido)
                    for value in results:
                        if results.count(value) >= 2:
                            final_value = value
                            if has_inconsistency:
                                self.inconsistencies_detected.inc()
                                masked = True
                                self.inconsistencies_masked.inc()
                            break
                    else:
                        # Si los 3 difieren, fallback (incluyendo -1)
                        final_value = sum(results) / 3
                        self.inconsistencies_detected.inc()
                        unmasked = True
                        self.inconsistencies_unmasked.inc()

                    # Log detallado por request
                    print(f"[VotingCoordinator] results={results}, final={final_value}, masked={masked}, unmasked={unmasked}, voting_enabled={voting_enabled}")

                return final_value
            else:
                # Voting deshabilitado: solo estrategia 1, con posibilidad de error simulado
                # El valor correcto
                valor_correcto = round(base_price * 1.10 + 5, 2)
                # El valor simulado (error)
                valor_simulado = round(base_price * 1.10 + 10, 2)
                # 80% chance de correcto, 20% de error simulado
                if random.random() < 0.2:
                    self.inconsistencies_detected.inc()
                    resultado = valor_simulado
                else:
                    resultado = valor_correcto
                print(f"[VotingCoordinator] voting deshabilitado, resultado={resultado}")
                return resultado
