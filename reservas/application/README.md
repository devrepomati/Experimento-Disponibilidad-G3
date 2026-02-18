# Application

Esta carpeta contiene la lógica de aplicación (casos de uso) del microservicio **reservas** bajo la arquitectura hexagonal.

## Propósito

La capa de aplicación orquesta los casos de uso del dominio, coordinando la interacción entre los adaptadores y el núcleo de negocio. 

- Implementa los casos de uso del sistema en servicios.
- No contiene lógica de infraestructura ni detalles tecnológicos.
- El servicio en este caso procesa la solicitud de reserva y envia un evento a kafka