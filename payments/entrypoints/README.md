# Entrypoints

Esta carpeta contiene los puntos de entrada del microservicio **payments** bajo la arquitectura hexagonal.

## Propósito

La capa de entrypoints define cómo los clientes externos interactúan con el microservicio. Aquí se implementan:

- Controladores HTTP/REST (por ejemplo, endpoints de la API)
- Consumidores de mensajes (por ejemplo, suscriptores de Kafka)
- Interfaces de línea de comandos (CLI) si aplica

Esta capa recibe las solicitudes externas, las traduce y delega la lógica a la capa de aplicación.

## Ejemplo de contenido

- `api/`: Controladores y rutas HTTP/REST.
- `events/`: Consumidores de eventos/mensajes.