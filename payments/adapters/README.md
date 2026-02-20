# Adapters

Esta carpeta contiene los adaptadores de la arquitectura hexagonal para el microservicio **payments**.

## Propósito

Los adaptadores son responsables de conectar el núcleo de la aplicación (dominio y casos de uso) con el mundo exterior. 

- Mensajería (por ejemplo, integración con Kafka)
- APIs externas o servicios de terceros

Cada adaptador traduce las llamadas y datos entre el dominio y la tecnología específica utilizada.