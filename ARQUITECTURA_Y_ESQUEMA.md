# 📋 ARQUITECTURA Y ESQUEMA DEL PROYECTO
## Sistema de Tracking de Paquetes - Documentación Completa

**Versión:** 1.0
**Última actualización:** Marzo 2026
**Propósito:** Documentación para personas externas al proyecto

---

## 📑 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Estructura General](#estructura-general)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Componentes Backend](#componentes-backend)
5. [Componentes Frontend](#componentes-frontend)
6. [Base de Datos](#base-de-datos)
7. [API REST - Endpoints Detallados](#api-rest---endpoints-detallados)
8. [Tecnologías Utilizadas](#tecnologías-utilizadas)
9. [Cómo Ejecutar el Proyecto](#cómo-ejecutar-el-proyecto)
10. [Flujos de Trabajo](#flujos-de-trabajo)
11. [Notas Pedagógicas](#notas-pedagógicas)

---

## 🎯 Resumen Ejecutivo

### ¿Qué es este proyecto?

Este es un **sistema de seguimiento de paquetes** (package tracking) diseñado como herramienta educativa. Permite:

- ✅ **Crear usuarios** que envíen paquetes
- ✅ **Registrar envíos** con códigos de seguimiento únicos
- ✅ **Actualizar estados** de envíos en tiempo real
- ✅ **Consultar historial** completo de eventos de cada paquete
- ✅ **Visualizar métricas** del sistema

### Propósito Pedagógico

El proyecto está **intencionalmente diseñado con malas prácticas** para que estudiantes de arquitectura de software puedan:

- Identificar problemas de diseño
- Aprender refactoring
- Practicar migración a microservicios
- Comprender el impacto de decisiones arquitectónicas

### Stack Tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| **Frontend** | Vue.js | 3.4.21 |
| **Backend** | FastAPI (Python) | 0.109.2 |
| **BD** | PostgreSQL | 15 |
| **DevOps** | Docker & Docker Compose | Latest |
| **Build** | Vite | 5.2.0 |

---

## 🏗️ Estructura General

```
proyecto_Malo/
│
├── docker-compose.yml              ← Orquestación de servicios
├── README.md                       ← Documentación principal
├── ARQUITECTURA_Y_ESQUEMA.md       ← Este archivo
│
├── 📁 backend/                     ← API REST (FastAPI + Python)
│   ├── main.py                     ← Lógica Principal [1]
│   ├── models.py                   ← Modelos ORM [2]
│   ├── database.py                 ← Configuración BD [3]
│   ├── seed.py                     ← Datos de Prueba [4]
│   ├── requirements.txt            ← Dependencias Python
│   ├── schema_mal_diseno.sql       ← Schema SQL (referencia)
│   ├── Dockerfile                  ← Imagen Docker
│   └── .dockerignore
│
└── 📁 frontend/                    ← Aplicación Web (Vue 3)
    ├── src/
    │   ├── main.js                 ← Entry Point [5]
    │   └── App.vue                 ← Componente Principal [6]
    ├── index.html                  ← HTML Base
    ├── package.json                ← Dependencias Node.js
    ├── vite.config.js              ← Configuración Vite
    ├── nginx.conf                  ← Config nginx (producción)
    ├── Dockerfile                  ← Build multi-stage
    ├── README.md                   ← Docs frontend específicas
    └── dist/                       ← Build compilado
```

**Archivos Críticos:**
- `[1]` main.py - Contiene TODA la lógica del backend (problema pedagógico)
- `[2]` models.py - Define estructura de BD (con denormalización)
- `[3]` database.py - Conexión a PostgreSQL
- `[4]` seed.py - Carga datos de prueba
- `[5]` main.js - Inicializa Vue
- `[6]` App.vue - Único componente (problema pedagógico)

---

## 🏛️ Arquitectura del Sistema

### Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENTE (NAVEGADOR WEB)                     │
│          Vue 3 + Vite (Puerto 5173 en desarrollo)              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    HTTP/HTTPS Requests
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│            NGINX (Puerto 8080 - Producción)                      │
│     Sirve archivos estáticos del frontend compilado (dist/)      │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                    API Calls (localhost:8000)
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│         FASTAPI (Puerto 8000 - Backend REST API)                 │
│                                                                  │
│  ├─ 8 Endpoints HTTP                                            │
│  ├─ CORS habilitado (* todas las origen - Pedagógico)          │
│  ├─ Manejo de solicitudes HTTP                                 │
│  └─ Lógica de negocio (TODO acoplado aquí)                      │
└────────┬──────────────────────────────────────────────┬──────────┘
         │                                              │
    SQL Queries                                   Configuration
         │                                              │
         ▼                                              ▼
┌──────────────────────────────┐        ┌──────────────────────────┐
│   SQLAlchemy ORM             │        │  Variables de Entorno    │
│  (Object Relation Mapping)   │        │                          │
│                              │        │ DB_HOST=postgres         │
│ Mapea:                       │        │ DB_PORT=5432             │
│ - Tablas SQL → Clases Python │        │ DB_USER=tracker          │
│ - User                       │        │ DB_PASSWORD=tracker_*    │
│ - TrackingData               │        │ DB_NAME=package_tracking │
└──────────────┬───────────────┘        └────────────────────────┘
               │
          SQL Queries
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│         PostgreSQL 15 (Puerto 5432 - Base de Datos)             │
│                                                                  │
│  Tablas:                                                        │
│  ├─ users                    (Información de usuarios)           │
│  └─ tracking_data            (Eventos de paquetes)              │
│                                                                  │
│  Volumen Persistente: pg_data  (Datos persisten entre reinicios)│
└──────────────────────────────────────────────────────────────────┘
```

### Patrones de Comunicación

```
1. SOLICITUD DE USUARIO
   Usuario → Navegador → Vue Component → fetch() → POST /createUser

2. PROCESAMIENTO EN BACKEND
   FastAPI recibe POST → Parse JSON → Lógica en main.py → Query BD

3. RESPUESTA A CLIENTE
   Backend → JSON Response → Vue recibe → Actualiza estado reactivo

4. ACTUALIZACIÓN UI
   Vue detecta cambio en ref → Re-render automático → Usuario ve cambios
```

---

## 🔧 Componentes Backend

### 1️⃣ database.py - Conexión a Base de Datos

**Propósito:** Configurar y gestionar conexión a PostgreSQL

```python
# Estructura simplificada
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:pass@host:port/dbname"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Factory para crear sesiones de BD"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Variables de Entorno Utilizadas:**
```
DB_HOST      → Host del servidor PostgreSQL (default: postgres)
DB_PORT      → Puerto (default: 5432)
DB_USER      → Usuario BD (default: tracker)
DB_PASSWORD  → Contraseña (default: tracker_secret)
DB_NAME      → Nombre de BD (default: package_tracking)
```

---

### 2️⃣ models.py - Modelos ORM (SQLAlchemy)

**Propósito:** Definir estructura de BD como clases Python

#### Modelo 1: User (Usuario)

```python
class User(Base):
    __tablename__ = "users"

    id: int                    # Clave primaria, auto-incrementada
    username: str              # Nombre único del usuario
    email: str                 # Email del usuario
```

**Tabla SQL Equivalente:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL
);
```

**Ejemplo de Datos:**
```
ID | Username  | Email
---|-----------|------------------
1  | ana_lopez | ana@example.com
2  | ben_kim   | ben@example.com
3  | carla_m   | carla@example.com
```

---

#### Modelo 2: TrackingData (Información de Paquetes)

```python
class TrackingData(Base):
    __tablename__ = "tracking_data"

    # Campos del usuario (REDUNDANTES - Problema Pedagógico)
    user_id: int                      # ID del usuario (SIN Foreign Key)
    username_redundant: str           # ⚠️ Copia de username
    user_email_copy: str              # ⚠️ Copia de email

    # Información del paquete
    tracking_code: str                # Código único de seguimiento
    package_title: str                # Descripción del paquete

    # Estado actual
    status: str                       # Estado del envío
    location: str                     # Ubicación actual
    city: str                         # Ciudad del evento

    # Metadata
    event_note: str                   # Nota del evento
    recorded_at: datetime             # Timestamp de creación
```

**Tabla SQL Equivalente:**
```sql
CREATE TABLE tracking_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,                    /* ⚠️ Sin Foreign Key */
    username_redundant VARCHAR(100),             /* Duplicado */
    user_email_copy VARCHAR(255),                /* Duplicado */
    tracking_code VARCHAR(64) NOT NULL UNIQUE,
    package_title VARCHAR(200) NOT NULL,
    status VARCHAR(50) NOT NULL,
    location VARCHAR(200),
    city VARCHAR(100),
    event_note TEXT,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ix_tracking_data_tracking_code
ON tracking_data (tracking_code);
```

**Ejemplo de Datos:**
```
ID | User_ID | Username_Redundant | Tracking_Code    | Status       | Location
---|---------|-------------------|------------------|--------------|----------
1  | 1       | ana_lopez         | TRK-SEED-1001   | CREATED      | Bodega Central
2  | 1       | ana_lopez         | TRK-SEED-1001   | IN_TRANSIT   | Hub Norte
3  | 1       | ana_lopez         | TRK-SEED-1001   | OUT_FOR_DELIVERY | Camión 12
```

---

### 3️⃣ seed.py - Datos de Prueba

**Propósito:** Cargar datos iniciales para pruebas

**Usuarios Creados:**

| ID | Username | Email |
|----|----------|-------|
| 1 | ana_lopez | ana@example.com |
| 2 | ben_kim | ben@example.com |
| 3 | carla_m | carla@example.com |

**Paquetes de Prueba:**

| Tracking Code | Usuario | Título | Estados |
|---|---|---|---|
| TRK-SEED-1001 | ana_lopez | Libros | CREATED → IN_TRANSIT → OUT_FOR_DELIVERY |
| TRK-SEED-2002 | ben_kim | Electrónica | CREATED → IN_TRANSIT |
| TRK-SEED-3003 | carla_m | Regalo | CREATED → EXCEPTION → IN_TRANSIT → DELIVERED |

**Total de registros iniciales:** 10 eventos distribuidos entre 3 paquetes

---

### 4️⃣ main.py - Lógica Principal (Backend)

**Propósito:** Define todos los endpoints HTTP y lógica de negocio

**Estructura del Archivo:**

```
Líneas 1-26       ├─ Imports y configuración CORS
Líneas 28-40      ├─ Estados válidos (constant)
Líneas 43-51      ├─ Evento startup (@app.on_event)
Líneas 54-319     └─ 8 Endpoints HTTP
```

#### Estados Válidos

```python
Estados permitidos para un paquete:
├─ CREATED            # Paquete creado recientemente
├─ IN_TRANSIT         # En camino
├─ OUT_FOR_DELIVERY   # Listo para entrega
├─ DELIVERED          # Entregado
└─ EXCEPTION          # Problema en envío
```

#### Funciones Internas Clave

**Función 1: `_open_db()`**
```python
def _open_db():
    """Abre conexión a BD y retorna sesión SQLAlchemy"""
    - Crea nueva sesión
    - Se llama en CADA endpoint (problema de diseño)
    - No usa dependency injection
```

**Función 2: `_make_tracking_code()`**
```python
def _make_tracking_code():
    """Genera código de seguimiento único"""
    Formato: "TRK-{6-dígitos-aleatorios}-{timestamp}"
    Ejemplo: "TRK-945832-1234"
```

**Función 3: `_notify_user_channel()`**
```python
def _notify_user_channel(user_id, message):
    """Notifica a usuario (simulado)"""
    - Imprime a stdout (en lugar de usar WebSocket/cola real)
    - Acoplado al endpoint (no es event-driven)
```

---

## 📱 Componentes Frontend

### Estructura de Vue

**Archivo:** `/frontend/src/App.vue`

```vue
<template>
  <!-- Todo el HTML de la UI en un solo archivo -->
  <!-- Formularios, tablas, secciones -->
</template>

<script setup>
  // Todo el estado (ref, computed)
  // Toda la lógica (funciones, fetch calls)
  // Sin separación de responsabilidades
</script>

<style scoped>
  /* Estilos del componente */
</style>
```

### Estado Reactivo (ref)

El componente mantiene este estado:

```javascript
// ═══════════════════════════════════════
// CREAR USUARIO
// ═══════════════════════════════════════
nombre = ref("")                    // Input: nombre de usuario
email = ref("")                     // Input: email

// ═══════════════════════════════════════
// CREAR PAQUETE
// ═══════════════════════════════════════
descPaquete = ref("")               // Input: descripción
origen = ref("")                    // Input: ubicación origen
destino = ref("")                   // Input: ciudad destino
idUsuarioPaquete = ref("")          // Input: ID usuario propietario

// ═══════════════════════════════════════
// ACTUALIZAR ESTADO
// ═══════════════════════════════════════
codigoTracking = ref("")            // Input: código de paquete
nuevoEstado = ref("")               // Input: nuevo estado
ubicacionNueva = ref("")            // Input: ubicación actual
notaNueva = ref("")                 // Input: nota de evento

// ═══════════════════════════════════════
// BUSCAR PAQUETE
// ═══════════════════════════════════════
buscarCodigo = ref("")              // Input: código a buscar
resultadoTracking = ref(null)       // Resultado de búsqueda

// ═══════════════════════════════════════
// ESTADOS DE RESPUESTA
// ═══════════════════════════════════════
data1 = ref(null)                   // Respuesta de /createUser
info = ref("")                      // Respuesta general
temp = ref("")                      // Temp storage
mensajePaquete = ref("")            // Mensaje de feedback
```

### Computed Properties

```javascript
infoExtra = computed(() => {
    return info.value + temp.value  // Combina dos strings
    // Problema: Lógica simple que podría estar en template
})
```

### Funciones HTTP (Fetch)

#### Función 1: `crearUsuarioMalHecho()`

```javascript
async function crearUsuarioMalHecho() {
    try {
        const response = await fetch('http://localhost:8000/createUser', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: nombre.value,
                email: email.value
            })
        });

        const data = await response.json();

        if (data.ok) {
            info.value = `Usuario ${data.username} creado`;
            // ⚠️ Problema pedagógico: Guardar ID en window
            window.__lastUserIdForPackages = data.user_id;
        }
    } catch (error) {
        console.error(error);  // Manejo de error genérico
    }
}
```

**Problemas identificados:**
- ❌ URL hardcodeada
- ❌ Fetches acoplados al componente
- ❌ Manejo de error genérico
- ❌ Estado global en `window.__lastUserIdForPackages`

#### Función 2: `crearPaqueteCopiaFetch()`

```javascript
async function crearPaqueteCopiaFetch() {
    try {
        const response = await fetch('http://localhost:8000/createPackage', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: parseInt(idUsuarioPaquete.value),
                package_title: descPaquete.value,
                location: origen.value,
                city: destino.value
            })
        });

        const data = await response.json();

        if (data.ok) {
            temp.value = data.tracking_code;  // Muestra tracking code
            mensajePaquete.value = `Paquete creado: ${data.tracking_code}`;
        }
    } catch (error) {
        console.error(error);
    }
}
```

**Problema:** Mismo patrón de fetch repetido (NO REUTILIZABLE)

#### Función 3: `actualizarEstadoOtraVezFetchIgual()`

```javascript
async function actualizarEstadoOtraVezFetchIgual() {
    try {
        const response = await fetch('http://localhost:8000/updateStatus', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tracking_code: codigoTracking.value,
                new_status: nuevoEstado.value,
                location: ubicacionNueva.value,
                note: notaNueva.value
            })
        });

        const data = await response.json();

        if (data.ok) {
            info.value = `Estado actualizado a: ${data.status}`;
        }
    } catch (error) {
        console.error(error);
    }
}
```

**Problema:** Tercera repetición del patrón de fetch

#### Función 4: `buscarTracking()`

```javascript
async function buscarTracking() {
    try {
        const response = await fetch(
            `http://localhost:8000/getTracking/${buscarCodigo.value}`
        );
        const data = await response.json();

        resultadoTracking.value = data;  // Guarda historial completo
    } catch (error) {
        console.error(error);
    }
}
```

---

## 🗄️ Base de Datos

### Esquema SQL Completo

```sql
-- ════════════════════════════════════════════════════════════
-- TABLA 1: USUARIOS
-- ════════════════════════════════════════════════════════════

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL
);

-- ════════════════════════════════════════════════════════════
-- TABLA 2: TRACKING DE PAQUETES (Denormalizada - Pedagógico)
-- ════════════════════════════════════════════════════════════

CREATE TABLE tracking_data (
    -- Identificador
    id SERIAL PRIMARY KEY,

    -- Referencia a usuario (⚠️ SIN Foreign Key Constraint)
    user_id INTEGER NOT NULL,

    -- ⚠️ CAMPOS REDUNDANTES - Denormalización
    username_redundant VARCHAR(100) NOT NULL,
    user_email_copy VARCHAR(255) NOT NULL,

    -- Información del paquete
    tracking_code VARCHAR(64) NOT NULL UNIQUE,
    package_title VARCHAR(200) NOT NULL,

    -- Estado del envío
    status VARCHAR(50) NOT NULL,
    location VARCHAR(200),
    city VARCHAR(100),

    -- Metadata
    event_note TEXT,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para búsquedas rápidas por tracking_code
CREATE INDEX ix_tracking_data_tracking_code
ON tracking_data (tracking_code);
```

### Volumen Persistente (Docker)

```yaml
volumes:
  pg_data:  # Volumen nombrado de Docker
    driver: local
```

**Propósito:** Los datos persisten incluso si el contenedor se detiene/reinicia

**Ubicación en host:** `/var/lib/docker/volumes/proyecto_malo_pg_data/_data/`

---

## 🔌 API REST - Endpoints Detallados

### Resumen de Endpoints

| Método | Ruta | Descripción | Auth | Datos |
|--------|------|-------------|------|-------|
| POST | `/createUser` | Crear nuevo usuario | ❌ | username, email |
| GET | `/getUsers` | Listar usuarios | ❌ | - |
| POST | `/createPackage` | Crear paquete | ❌ | user_id, title, location, city |
| GET | `/getAllPackages` | Último estado por paquete | ❌ | - |
| POST | `/updateStatus` | Actualizar estado | ❌ | tracking_code, status, location, note |
| GET | `/getTracking/{code}` | Historial de paquete | ❌ | tracking_code (URL) |
| GET | `/health` | Health check | ❌ | - |
| GET | `/metrics` | Métricas del sistema | ❌ | - |

### 1️⃣ POST /createUser - Crear Usuario

**Descripción:** Registra un nuevo usuario en el sistema

**URL:** `http://localhost:8000/createUser`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "nuevo_usuario",
  "email": "usuario@ejemplo.com"
}
```

**Response (201 Created):**
```json
{
  "ok": true,
  "user_id": 4,
  "username": "nuevo_usuario"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "bad input"
}
```

**Validaciones:**
- ✅ username debe ser string no vacío
- ✅ email debe ser string no vacío
- ❌ No valida formato de email

---

### 2️⃣ GET /getUsers - Listar Usuarios

**Descripción:** Obtiene lista de todos los usuarios registrados

**URL:** `http://localhost:8000/getUsers`

**Request:** Sin body

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "username": "ana_lopez",
    "email": "ana@example.com"
  },
  {
    "id": 2,
    "username": "ben_kim",
    "email": "ben@example.com"
  },
  {
    "id": 3,
    "username": "carla_m",
    "email": "carla@example.com"
  }
]
```

**Performance:** Sin paginación (problema pedagógico)

---

### 3️⃣ POST /createPackage - Crear Paquete

**Descripción:** Registra un nuevo envío/paquete

**URL:** `http://localhost:8000/createPackage`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": 1,
  "package_title": "Libros de programación",
  "location": "Bodega Central",
  "city": "Santiago"
}
```

**Response (201 Created):**
```json
{
  "ok": true,
  "tracking_code": "TRK-945832-1234",
  "status": "CREATED",
  "id": 15
}
```

**Procesos internos:**
1. ✅ Valida que user_id exista
2. ✅ Genera `tracking_code` único
3. ✅ Crea registro en `tracking_data` con estado CREATED
4. ✅ Duplica datos de usuario (problema pedagógico)
5. ✅ Retorna tracking_code al cliente

**Formato del tracking_code:**
```
Patrón: "TRK-{6-dígitos-aleatorios}-{timestamp-short}"
Ejemplo: TRK-945832-1234
```

---

### 4️⃣ GET /getAllPackages - Listar Paquetes (Último Estado)

**Descripción:** Obtiene el último estado registrado de cada paquete

**URL:** `http://localhost:8000/getAllPackages`

**Request:** Sin body

**Response (200 OK):**
```json
[
  {
    "tracking_code": "TRK-SEED-1001",
    "username_redundant": "ana_lopez",
    "status": "OUT_FOR_DELIVERY",
    "package_title": "Libros",
    "location": "Camión 12"
  },
  {
    "tracking_code": "TRK-SEED-2002",
    "username_redundant": "ben_kim",
    "status": "IN_TRANSIT",
    "package_title": "Electrónica",
    "location": "Hub Norte"
  }
]
```

**Nota:** Solo muestra el evento más reciente por tracking_code

---

### 5️⃣ POST /updateStatus - Actualizar Estado

**Descripción:** Registra un evento de cambio de estado en un paquete

**URL:** `http://localhost:8000/updateStatus`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "tracking_code": "TRK-945832-1234",
  "new_status": "IN_TRANSIT",
  "location": "Hub Norte",
  "note": "Paquete en transporte regional"
}
```

**Response (200 OK):**
```json
{
  "ok": true,
  "tracking_code": "TRK-945832-1234",
  "status": "IN_TRANSIT"
}
```

**Estados Válidos:**
```
CREATED
IN_TRANSIT
OUT_FOR_DELIVERY
DELIVERED
EXCEPTION
```

**Procesos internos:**
1. ✅ Busca paquete por tracking_code
2. ✅ Valida estado sea uno de los 5 permitidos
3. ✅ Crea nuevo registro en tracking_data (event log)
4. ✅ Duplica datos de usuario (problema pedagógico)
5. ✅ Llama a `_notify_user_channel()` (imprime a stdout)

---

### 6️⃣ GET /getTracking/{tracking_code} - Historial Completo

**Descripción:** Obtiene todos los eventos históricos de un paquete

**URL:** `http://localhost:8000/getTracking/TRK-945832-1234`

**Request:** Sin body (parámetro en URL)

**Response (200 OK):**
```json
{
  "tracking_code": "TRK-945832-1234",
  "current_status": "OUT_FOR_DELIVERY",
  "username_redundant": "ana_lopez",
  "events": [
    {
      "id": 10,
      "status": "CREATED",
      "location": "Bodega Central",
      "note": "Ingreso de paquete",
      "at": "2026-03-31T10:00:00.000000+00:00"
    },
    {
      "id": 11,
      "status": "IN_TRANSIT",
      "location": "Hub Norte",
      "note": "En ruta hacia destino",
      "at": "2026-03-31T10:30:00.000000+00:00"
    },
    {
      "id": 12,
      "status": "OUT_FOR_DELIVERY",
      "location": "Camión 12",
      "note": "En camión de reparto",
      "at": "2026-03-31T11:15:00.000000+00:00"
    }
  ]
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Tracking code not found"
}
```

---

### 7️⃣ GET /health - Health Check

**Descripción:** Verifica que el API esté funcionando

**URL:** `http://localhost:8000/health`

**Response (200 OK):**
```json
{
  "status": "up"
}
```

**Uso:** Monitoreo, health checks en Docker, balanceadores de carga

---

### 8️⃣ GET /metrics - Métricas del Sistema

**Descripción:** Estadísticas básicas del sistema

**URL:** `http://localhost:8000/metrics`

**Response (200 OK):**
```json
{
  "total_packages": 5,
  "total_events": 14,
  "average_processing_time": 123.45,
  "generated_at": "2026-03-31T11:45:00.123456+00:00"
}
```

**Campos:**
- `total_packages` - Cantidad de paquetes únicos
- `total_events` - Total de registros en tracking_data
- `average_processing_time` - Tiempo promedio en minutos
- `generated_at` - Timestamp de generación

---

## 🛠️ Tecnologías Utilizadas

### Backend Stack

```
┌─────────────────────────────────────────────┐
│            BACKEND DEPENDENCIES             │
├─────────────────────────────────────────────┤
│                                             │
│  ✅ FastAPI 0.109.2                         │
│     └─ Framework web async moderno          │
│                                             │
│  ✅ Uvicorn 0.27.1                          │
│     └─ Servidor ASGI (async web server)     │
│                                             │
│  ✅ SQLAlchemy 2.0.25                       │
│     └─ ORM para manejo de BD                │
│                                             │
│  ✅ psycopg2-binary 2.9.9                   │
│     └─ Driver PostgreSQL para Python        │
│                                             │
│  ✅ python-multipart 0.0.9                  │
│     └─ Parser de datos multipart            │
│                                             │
└─────────────────────────────────────────────┘
```

**Archivo:** `/backend/requirements.txt`

### Frontend Stack

```
┌─────────────────────────────────────────────┐
│           FRONTEND DEPENDENCIES             │
├─────────────────────────────────────────────┤
│                                             │
│  ✅ Vue.js 3.4.21                           │
│     └─ Framework JavaScript progresivo      │
│                                             │
│  ✅ Vite 5.2.0                              │
│     └─ Build tool y dev server              │
│                                             │
│  ✅ @vitejs/plugin-vue 5.0.4                │
│     └─ Plugin Vite para archivos .vue       │
│                                             │
│  ✅ Nginx (imagen alpine)                   │
│     └─ Servidor web (solo en producción)    │
│                                             │
└─────────────────────────────────────────────┘
```

**Archivo:** `/frontend/package.json`

### Infraestructura

```
┌─────────────────────────────────────────────┐
│          INFRASTRUCTURE STACK               │
├─────────────────────────────────────────────┤
│                                             │
│  ✅ PostgreSQL 15-alpine                    │
│     └─ Base de datos relacional             │
│                                             │
│  ✅ Docker                                  │
│     └─ Containerización de aplicaciones     │
│                                             │
│  ✅ Docker Compose                          │
│     └─ Orquestación multi-contenedor        │
│                                             │
│  ✅ Nginx Alpine                            │
│     └─ Servidor web ligero                  │
│                                             │
└─────────────────────────────────────────────┘
```

**Archivo:** `docker-compose.yml`

---

## 🚀 Cómo Ejecutar el Proyecto

### Opción 1: Stack Completo con Docker Compose ⭐ RECOMENDADO

**Prerrequisitos:**
- Docker && Docker Compose instalados
- Puerto 8000, 8080, 5432 disponibles

**Pasos:**

```bash
# 1. Navega a la carpeta del proyecto
cd /media/pablo/hdd-linux/Proyecto_Universidad/proyecto_Malo/proyecto_Malo

# 2. Levanta todos los servicios
docker compose up --build

# 3. Espera ~30 segundos a que todo inicie
#    (PostgreSQL tarda un poco en iniciar)
```

**Acceso:**

| Componente | URL | Descripción |
|-----------|-----|-------------|
| Frontend | http://localhost:8080 | Interfaz web |
| Backend | http://localhost:8000 | API REST |
| Swagger API Docs | http://localhost:8000/docs | Documentación interactiva |
| ReDoc | http://localhost:8000/redoc | Documentación alternativa |

**Qué sucede:**

```
1. Compose crea red docker "proyecto_malo_default"
2. Levanta PostgreSQL en puerto 5432
   └─ Crea BD "package_tracking"
   └─ Crea tablas (users, tracking_data)
3. Levanta Backend (FastAPI)
   └─ Conecta a PostgreSQL
   └─ Ejecuta seed.py (carga datos iniciales)
   └─ Escucha en puerto 8000
4. Levanta Frontend (Nginx)
   └─ Sirve archivos compilados
   └─ Escucha en puerto 8080
```

**Para detener:**

```bash
docker compose down

# Si quieres eliminar base de datos:
docker compose down -v
```

---

### Opción 2: Solo Backend (Desarrollo)

**Prerrequisitos:**
- Python 3.9+
- PostgreSQL corriendo localmente en puerto 5432

**Pasos:**

```bash
# 1. Navega al backend
cd /media/pablo/hdd-linux/.../backend

# 2. Crea entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Configura variables de entorno
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=tracker
export DB_PASSWORD=tracker_secret
export DB_NAME=package_tracking

# 5. Ejecuta el servidor
uvicorn main:app --reload

# El servidor estará en http://localhost:8000
```

**Recargar automático:** Uvicorn detecta cambios en archivos (con `--reload`)

---

### Opción 3: Solo Frontend (Desarrollo)

**Prerrequisitos:**
- Node.js 18+
- Backend corriendo en http://localhost:8000

**Pasos:**

```bash
# 1. Navega al frontend
cd /media/pablo/hdd-linux/.../frontend

# 2. Instala dependencias
npm install

# 3. Inicia servidor de desarrollo (con hot reload)
npm run dev

# El servidor estará en http://localhost:5173
```

**Hot Reload:** Cambios en Vue se reflejan automáticamente en navegador

---

### Opción 4: Build Frontend para Producción

```bash
# Navega a frontend
cd frontend

# Compilar (minificado, optimizado)
npm run build

# Los archivos compilados están en: dist/

# Previsualizar build
npm run preview
# Accede a http://localhost:4173
```

---

## 📊 Flujos de Trabajo

### Flujo 1: Crear Usuario Completo

```
┌─ USUARIO ABRE NAVEGADOR
│
├─ 1. Escriba nombre de usuario
│     └─ input: "juan_perez"
│
├─ 2. Escriba email
│     └─ input: "juan@example.com"
│
├─ 3. Click botón "Crear Usuario"
│     └─ Llama crearUsuarioMalHecho()
│
├─ 4. Frontend → POST /createUser
│     REQUEST:
│     {
│       "username": "juan_perez",
│       "email": "juan@example.com"
│     }
│
├─ 5. Backend procesa:
│     ├─ Abre conexión BD
│     ├─ Valida inputs (básico)
│     ├─ INSERT en tabla users
│     ├─ Obtiene ID generado (ej: 4)
│     └─ Cierra conexión
│
├─ 6. Backend responde:
│     {
│       "ok": true,
│       "user_id": 4,
│       "username": "juan_perez"
│     }
│
├─ 7. Frontend recibe respuesta
│     ├─ Valida data.ok == true
│     ├─ Guarda user_id en window.__lastUserIdForPackages
│     ├─ Muestra mensaje: "Usuario juan_perez creado"
│     └─ Limpia inputs
│
└─ FIN: Usuario puede usar ID 4 para crear paquetes
```

---

### Flujo 2: Crear Paquete Completo

```
┌─ USUARIO NECESITA ENVIAR PAQUETE
│
├─ 1. Ingresa datos del formulario
│     ├─ Descripción: "Laptop"
│     ├─ Origen: "Tienda Centro"
│     ├─ Destino: "Los Ángeles"
│     └─ ID Usuario: 1 (lejemplo)
│
├─ 2. Click en "Crear Paquete"
│     └─ Llama crearPaqueteCopiaFetch()
│
├─ 3. Frontend → POST /createPackage
│     REQUEST:
│     {
│       "user_id": 1,
│       "package_title": "Laptop",
│       "location": "Tienda Centro",
│       "city": "Los Ángeles"
│     }
│
├─ 4. Backend procesa:
│     ├─ Abre BD
│     ├─ Valida user_id exista
│     ├─ Genera tracking_code: "TRK-834201-5678"
│     ├─ Inserta en tracking_data:
│     │   {
│     │     user_id: 1,
│     │     username_redundant: "ana_lopez",
│     │     user_email_copy: "ana@example.com",
│     │     tracking_code: "TRK-834201-5678",
│     │     package_title: "Laptop",
│     │     status: "CREATED",
│     │     location: "Tienda Centro",
│     │     city: "Los Ángeles"
│     │   }
│     └─ Cierra conexión
│
├─ 5. Backend responde:
│     {
│       "ok": true,
│       "tracking_code": "TRK-834201-5678",
│       "status": "CREATED",
│       "id": 25
│     }
│
├─ 6. Frontend recibe respuesta:
│     ├─ Guarda tracking_code en temp.value
│     ├─ Muestra: "Paquete creado: TRK-834201-5678"
│     └─ Limpia inputs
│
└─ FIN: Cliente recibe código para rastrear envío
```

---

### Flujo 3: Consultar Historial de Paquete

```
┌─ USUARIO QUIERE RASTREAR ENVÍO
│
├─ 1. Ingresa código de rastreo
│     └─ input: "TRK-834201-5678"
│
├─ 2. Click en "Buscar"
│     └─ Llama buscarTracking()
│
├─ 3. Frontend → GET /getTracking/TRK-834201-5678
│
├─ 4. Backend procesa:
│     ├─ Abre BD
│     ├─ Query todos registros con tracking_code
│     ├─ Obtiene:
│     │   [
│     │     {id:25, status:"CREATED", location:"Tienda Centro", ...},
│     │     {id:26, status:"IN_TRANSIT", location:"Hub Sur", ...},
│     │     {id:27, status:"OUT_FOR_DELIVERY", location:"Camión 5", ...}
│     │   ]
│     ├─ Organiza eventos
│     └─ Retorna respuesta
│
├─ 5. Backend responde:
│     {
│       "tracking_code": "TRK-834201-5678",
│       "current_status": "OUT_FOR_DELIVERY",
│       "events": [
│         {status:"CREATED", location:"Tienda Centro", ...},
│         {status:"IN_TRANSIT", location:"Hub Sur", ...},
│         {status:"OUT_FOR_DELIVERY", location:"Camión 5", ...}
│       ]
│     }
│
├─ 6. Frontend muestra historial:
│     ├─ Estado actual: "OUT_FOR_DELIVERY"
│     ├─ Tabla con eventos (estado, ubicación, timestamp)
│     └─ Usuario ve el progreso del envío
│
└─ FIN: Usuario sabe dónde está su paquete
```

---

## 📚 Notas Pedagógicas

### ¿Por qué el diseño es "malo"?

Este proyecto fue **intencionalmente diseñado con antipatrones** para enseñar:

#### ❌ Problemas Backend

| Problema | Por qué es malo | Solución ideal |
|----------|-----------------|----------------|
| **Monolito** | Todo en `main.py` | Separar en capas (controllers, services, repositories) |
| **Sin Separación de Capas** | HTTP + BD + Lógica mezclado | Usar arquitectura en capas |
| **Denormalización extrema** | Duplicación de datos | Usar Foreign Keys y normalización |
| **Sin transacciones** | BD inconsistente | Usar `@app.get()` con `@db.transaction()` |
| **Session Manual** | Acoplamiento | Dependency Injection |
| **CORS abierto** | Seguridad débil | Configurar origins específicos |
| **Validación tardía** | Errores en runtime | Usar Pydantic models |
| **No asincronía completa** | Bloqueos innecesarios | Usar async/await consistentemente |

#### ❌ Problemas Frontend

| Problema | Por qué es malo | Solución ideal |
|----------|-----------------|----------------|
| **Componente único** | Inmantenible | Dividir en componentes reutilizables |
| **Fetch inline** | Acoplamiento a URLs | Crear servicio API |
| **Sin validación** | UX pobre | Validar inputs antes de enviar |
| **Estado global en window** | Contaminación | Usar Pinia (state management) |
| **URLs hardcodeadas** | No escalable | Usar variables de entorno |
| **Manejo de error genérico** | Errores ocultos | Manejo específico por tipo |
| **Sin composables** | Lógica dispersa | Crear composables reutilizables |
| **Sin paginación** | Performance | Implementar límites y offsets |

---

### Ejercicios de Refactoring

#### Ejercicio 1: Separar Backend en Capas

**Objetivo:** Transformar monolito a arquitectura de capas

```
Estructura objetivo:
backend/
├── main.py                    # Solo configuración FastAPI
├── core/
│   └── config.py             # Variables de entorno
├── api/
│   └── routes/
│       ├── users.py          # Endpoints de usuarios
│       └── packages.py       # Endpoints de paquetes
├── models/
│   └── database.py           # Modelos ORM
├── schemas/
│   └── request.py            # Validación Pydantic
├── services/
│   ├── user_service.py       # Lógica usuarios
│   └── package_service.py    # Lógica paquetes
├── repositories/
│   ├── user_repo.py          # Acceso BD usuarios
│   └── package_repo.py       # Acceso BD paquetes
```

#### Ejercicio 2: Crear Servicio API Frontend

**Objetivo:** Centralizar fetch calls

```javascript
// api/trackingService.js
export const trackingAPI = {
  createUser: async (data) => { /* fetch con validación */ },
  getUsers: async () => { /* fetch */ },
  createPackage: async (data) => { /* fetch */ },
  // ... resto de endpoints
};

// En App.vue:
import { trackingAPI } from './api/trackingService';
// Ya no hay fetch duplicado
```

#### Ejercicio 3: Normalizar Base de Datos

**Objetivo:** Eliminar redundancia

```sql
-- Estructura normalizada:
-- Tabla users (sin cambios)
-- Tabla packages (nueva)
-- Tabla package_events (nueva)
-- Eliminar campos redundantes de tracking_data
```

---

### Recursos de Aprendizaje

**Backend (Python/FastAPI):**
- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy: https://www.sqlalchemy.org
- Arquitectura en capas: `https://en.wikipedia.org/wiki/N-tier_architecture`

**Frontend (Vue 3):**
- Vue 3 Guide: https://vuejs.org
- Pinia (State Management): https://pinia.vuejs.org
- Vite: https://vitejs.dev

**DevOps (Docker):**
- Docker Docs: https://docs.docker.com
- Docker Compose: https://docs.docker.com/compose

---

## 📞 Soporte y Contacto

### Si tienes dudas:

1. **¿No arranca?**
   - Verifica que Docker esté corriendo: `docker ps`
   - Revisa logs: `docker compose logs -f`

2. **¿Puertos ocupados?**
   - Cambia puertos en `docker-compose.yml`

3. **¿Errores de conexión?**
   - Espera ~30s a que PostgreSQL inicie
   - Verifica variables de entorno

4. **¿Más información?**
   - Lee `/README.md` en raíz del proyecto
   - Lee `/frontend/README.md` para detalles frontend

---

## 📄 Resumen de Archivos

| Archivo | Líneas | Propósito |
|---------|--------|----------|
| `/backend/main.py` | ~320 | Toda la lógica del API |
| `/backend/models.py` | ~40 | Modelos ORM |
| `/backend/database.py` | ~20 | Conexión BD |
| `/backend/seed.py` | ~60 | Datos iniciales |
| `/frontend/src/App.vue` | ~500+ | UI + lógica frontend |
| `/frontend/src/main.js` | ~5 | Entry point |
| `/docker-compose.yml` | ~40 | Orquestación |
| `/backend/Dockerfile` | ~20 | Build backend |
| `/frontend/Dockerfile` | ~30 | Build frontend |

---

## 🎓 Conclusión

Este proyecto ejemplifica una **aplicación funcional pero mal diseñada** que:

✅ **Funciona** - Todos los endpoints operan correctamente
✅ **Es pedagógico** - Cada problema tiene razón de ser educativa
✅ **Es mejorablé** - Hay claros paths para refactoring
✅ **Enseña principios** - SOLID, Clean Code, arquitectura

**Para aprender efectivamente:**

1. Entiende cómo funciona actualmente
2. Identifica los problemas de diseño
3. Propón soluciones mejores
4. Implementa los cambios
5. Compara antes vs. después

---

**Generado:** Marzo 2026
**Última revisión:** 2026-03-31

