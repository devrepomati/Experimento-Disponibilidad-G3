# Entrypoints

Esta carpeta contiene los puntos de entrada del microservicio **billing** bajo la arquitectura hexagonal.

## Propósito

La capa de entrypoints define cómo los clientes externos interactúan con el microservicio.

- Controladores HTTP/REST

Esta capa recibe las solicitudes externas, las traduce y delega la lógica a la capa de aplicación.