# Hito 1 — Migración de Monolito a Microservicios
## Sistema de Tracking de Paquetes

---

## Objetivo

Este hito implementa la migración de un monolito hacia una arquitectura de microservicios para un sistema de tracking de paquetes, incorporando:

- API Gateway
- 3 microservicios independientes
- Base de datos por servicio
- Observabilidad con Prometheus y Grafana
- Patrones de resiliencia (Circuit Breaker y Saga)

---

## Requisitos Previos

Para ejecutar el stack completo con Docker:

- Docker Engine `24+` (recomendado)
- Docker Compose Plugin `v2+` (usar `docker compose`, no `docker-compose`)
- Al menos 4 GB de RAM disponibles para contenedores
- Puertos libres: `3000`, `5432` (interno en contenedores), `8000`, `8001`, `8002`, `8003`, `9090`

Validar instalación:

```bash
docker --version
docker compose version
```

---

## Estructura del Repositorio

```
hito1/
├── docker/
│   └── docker-compose.yml          # Orquestación completa
├── services/
│   ├── api-gateway/                 # Nginx reverse proxy (puerto 8000)
│   ├── user-service/                # FastAPI usuarios (puerto 8001)
│   ├── package-service/             # FastAPI paquetes (puerto 8002)
│   └── tracking-service/            # FastAPI tracking (puerto 8003)
├── prometheus/
│   └── prometheus.yml               # Configuración de scraping
├── grafana/
│   ├── dashboards/                  # Dashboard JSON
│   └── provisioning/                # Auto-provisioning datasource + dashboard
└── docs/
    └── informe_hito1.docx           # Informe técnico completo
```

---

## Levantar el Stack Completo

Desde la carpeta `hito1/docker`:

```bash
cd docker
docker compose up --build
```

Para dejarlo en segundo plano:

```bash
docker compose up -d --build
```

Para detenerlo:

```bash
docker compose down
```

Para borrar volúmenes (reinicio total de datos):

```bash
docker compose down -v
```

| Servicio       | URL                          |
|----------------|------------------------------|
| API Gateway    | http://localhost:8000        |
| User Service   | http://localhost:8001/docs   |
| Package Service| http://localhost:8002/docs   |
| Tracking Svc   | http://localhost:8003/docs   |
| Prometheus     | http://localhost:9090        |
| Grafana        | http://localhost:3000        |

Credenciales Grafana: `admin / admin`

---

## Verificación Rápida

Comprobar estado de contenedores:

```bash
docker compose ps
```

Health checks directos:

```bash
curl http://localhost:8001/health
curl http://localhost:8003/health
```

Prueba mínima de flujo por gateway:

```bash
curl -X POST http://localhost:8000/users \
    -H "Content-Type: application/json" \
    -d '{"name":"Ana","email":"ana@example.com"}'
```

---

## Dependencias del Proyecto

### Infraestructura (Docker Images)

- `python:3.11-slim` (base de `user-service`, `package-service`, `tracking-service`)
- `nginx:1.25-alpine` (API Gateway)
- `postgres:15-alpine` (3 instancias, una por microservicio)
- `prom/prometheus:v2.51.0`
- `grafana/grafana:10.4.0`

### Dependencias Python por Servicio

`user-service`:

- `fastapi==0.109.2`
- `uvicorn[standard]==0.27.1`
- `sqlalchemy==2.0.25`
- `psycopg2-binary==2.9.9`
- `pydantic[email]==2.6.1`
- `prometheus-fastapi-instrumentator==6.1.0`

`package-service`:

- `fastapi==0.109.2`
- `uvicorn[standard]==0.27.1`
- `sqlalchemy==2.0.25`
- `psycopg2-binary==2.9.9`
- `pydantic==2.6.1`
- `httpx==0.27.0`
- `pybreaker==1.2.0`
- `prometheus-fastapi-instrumentator==6.1.0`

`tracking-service`:

- `fastapi==0.109.2`
- `uvicorn[standard]==0.27.1`
- `sqlalchemy==2.0.25`
- `psycopg2-binary==2.9.9`
- `pydantic==2.6.1`
- `prometheus-fastapi-instrumentator==6.1.0`

### Dependencias Frontend del Repositorio (opcional para Hito 1)

Aunque el stack principal de este hito funciona sin frontend, el repositorio incluye una app Vue/Vite con:

- `vue@^3.4.21`
- `vite@^5.2.0`
- `@vitejs/plugin-vue@^5.0.4`

---

## Endpoints Principales (a través del Gateway)

| Método | Ruta                        | Servicio        | Descripción               |
|--------|-----------------------------|-----------------|---------------------------|
| POST   | /users                      | user-service    | Crear usuario             |
| GET    | /users                      | user-service    | Listar usuarios           |
| GET    | /users/{id}                 | user-service    | Obtener usuario por ID    |
| POST   | /packages                   | package-service | Crear paquete (+ Saga)    |
| GET    | /packages                   | package-service | Listar paquetes           |
| POST   | /tracking/update            | tracking-service| Actualizar estado         |
| GET    | /tracking/{code}            | tracking-service| Historial de tracking     |

---

## Patrones Implementados

- **API Gateway**: Nginx enruta peticiones a los servicios correctos
- **Circuit Breaker**: pybreaker en package-service al llamar user-service
- **Saga Pattern**: package-service coordina creación de paquete + evento inicial; compensa ante fallo
- **Strangler Pattern**: el monolito original puede coexistir mientras se migra gradualmente

---

## Observabilidad

- **Prometheus** recolecta métricas de los 3 microservicios (latencia, throughput, errores)
- **Grafana** visualiza en tiempo real con dashboard pre-configurado
- Métricas expuestas en `/metrics` de cada servicio (prometheus-fastapi-instrumentator)

---

## Solución de Problemas Comunes

- Si falla por puertos ocupados, liberar `8000-8003`, `9090` y `3000`.
- Si un servicio no levanta, revisar logs:

```bash
docker compose logs -f user-service
docker compose logs -f package-service
docker compose logs -f tracking-service
```

- Si hay errores de conexión a BD tras cambios, recrear con limpieza:

```bash
docker compose down -v
docker compose up --build
```
