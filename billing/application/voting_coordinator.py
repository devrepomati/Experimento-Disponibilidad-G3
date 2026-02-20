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
        # Incrementa el contador de solicitudes totales
        self.requests_total.inc()
        # Si la solicitud está marcada para error, incrementa el contador correspondiente
        if context and (context.get("fail_strategy2") or context.get("fail_strategy3")):
            self.requests_marked_for_error_total.inc()
        with self.detection_duration.time():
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
                print(f"[VotingCoordinator] results={results}, final={final_value}, masked={masked}, unmasked={unmasked}")

        return final_value
