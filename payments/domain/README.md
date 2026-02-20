# Domain

Esta carpeta contiene el núcleo de dominio del microservicio **payments** bajo la arquitectura hexagonal.

## Propósito

La capa de dominio encapsula la lógica de negocio, las reglas y los modelos fundamentales del sistema.

- Entidades
- Puertos (interfaces) que definen los puntos de entrada/salida del dominio (por ejemplo, repositorios, servicios de mensajería)
- Eventos de dominio

No debe haber dependencias hacia detalles tecnológicos ni hacia otras capas.