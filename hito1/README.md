# Hito 1 — Migración de Monolito a Microservicios
## Sistema de Tracking de Paquetes

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

```bash
cd docker
docker compose up --build
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
