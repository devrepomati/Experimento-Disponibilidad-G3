# Experimento Travel Hub

Este es un proyecto de experimentación para evaluar decisiones de diseño orientadas a la **disponibilidad funcional** (disponibilidad de software) en sistemas basados en microservicios.

## Descripción del Experimento

El objetivo de este experimento es verificar la hipótesis de que la aplicación de tácticas de diseño como **monitoreo (detección de errores)** y **voting (enmascaramiento de errores)** favorecen la disponibilidad funcional del sistema. Se busca observar cómo la arquitectura y los mecanismos de monitoreo permiten detectar y enmascarar fallos, mejorando la resiliencia y la disponibilidad de los servicios.

Hipotesis: Si se implementa una estrategia de voting para los cálculos de facturación sumado a un monitoreo con health checks cada 10 segundos tendremos: 1. Detección de inconsistencias de cálculos en menos de 500ms. 2. No se entregan resultados incorrectos.

## Estructura del Proyecto

- **reservas/**: Microservicio de reservas (Flask, arquitectura hexagonal)
- **billing/**: Microservicio de facturación (Flask, arquitectura hexagonal)
- **payments/**: Microservicio de pagos (Flask, arquitectura hexagonal)
- **nginx/**: Configuración del API Gateway (nginx)
- **monitor/**: Componente para monitoreo periódico de los servicios
- **docker-compose.yaml**: Orquestación de todos los servicios, Kafka, Zookeeper y el gateway

Cada microservicio sigue la arquitectura hexagonal:
- `adapters/`: Adaptadores de entrada/salida (REST, DB, Kafka, etc.)
- `application/`: Lógica de aplicación y casos de uso
- `domain/`: Núcleo de negocio, entidades, puertos y eventos
- `entrypoints/`: Puntos de entrada (API, eventos, CLI)
- `infrastructure/config/`: Configuración de base de datos, Kafka y variables de entorno

## Instrucciones de Ejecución

### 1. Requisitos

- Docker y Docker Compose instalados en el sistema.

### 2. Construcción y despliegue

Desde la raíz del proyecto, ejecute:

```bash
docker-compose up --build
```

Esto construirá y levantará los microservicios, el API Gateway (nginx), Kafka, Zookeeper y el monitor.

### 3. Verificación de los endpoints /health

Una vez los contenedores estén en ejecución, puede verificar el estado de cada microservicio accediendo a los siguientes endpoints (por defecto, expuestos a través de nginx en el puerto 8080):

- [http://localhost:8080/reservas/health](http://localhost:8080/reservas/health)
- [http://localhost:8080/billing/health](http://localhost:8080/billing/health)
- [http://localhost:8080/payments/health](http://localhost:8080/payments/health)
- [http://localhost:8080/health](http://localhost:8080/health) (API Gateway)


### 4. Detener los servicios

Para detener y eliminar los contenedores, ejecute:

```bash
docker-compose down
```

---

## Prometheus
### Queries útiles para el experimento

- **Cantidad de inconsistencias detectadas (discrepancia entre estrategias):**
  ```
  voting_inconsistencies_detected
  ```
- **Cantidad de inconsistencias enmascaradas exitosamente (voting 2 de 3):**
  ```
  voting_inconsistencies_masked
  ```
- **Cantidad de inconsistencias no enmascaradas (fallback, los 3 difieren):**
  ```
  voting_inconsistencies_unmasked
  ```
- **Porcentaje de enmascaramiento exitoso:**
  ```
  (voting_inconsistencies_masked / voting_inconsistencies_detected) * 100
  ```
- **Latencia de detección/enmascaramiento (percentil 95):**
  ```
  histogram_quantile(0.95, sum(rate(voting_detection_duration_seconds_bucket[5m])) by (le))
  ```