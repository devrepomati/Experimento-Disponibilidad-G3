# Monitor

Este componente es responsable de monitorear la disponibilidad de los microservicios del experimento.

## Propósito

- Realizar healthchecks periódicos (cada 10 segundos) a los endpoints `/health` de los servicios:
  - reservas
  - billing
  - payments
  - api-gateway (nginx)
- Registrar el estado de cada servicio

## Endpoints a monitorear

- http://reservas:8000/health
- http://billing:8000/health
- http://payments:8000/health
- http://api-gateway/health
