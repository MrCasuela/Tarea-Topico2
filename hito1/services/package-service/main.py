"""
Package Service - Microservicio de Gestión de Paquetes
Responsabilidad: creación y consulta de paquetes.
Implementa Circuit Breaker al validar usuario con user-service.
Participa como coordinador del Saga Pattern al crear un paquete.
"""
import os
import time
import random
import logging
import httpx
import pybreaker

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.sql import func
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Circuit Breaker ────────────────────────────────────────────────────────────
# Si user-service falla 3 veces consecutivas, el circuito se abre durante 30 seg.
user_service_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
TRACKING_SERVICE_URL = os.getenv("TRACKING_SERVICE_URL", "http://tracking-service:8003")

# ── Base de datos ──────────────────────────────────────────────────────────────
DB_URL = (
    f"postgresql://{os.getenv('DB_USER','tracker')}:"
    f"{os.getenv('DB_PASSWORD','tracker_secret')}@"
    f"{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','5432')}/"
    f"{os.getenv('DB_NAME','packages_db')}"
)
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PackageModel(Base):
    __tablename__ = "packages"
    id            = Column(Integer, primary_key=True, index=True)
    tracking_code = Column(String(64), nullable=False, unique=True, index=True)
    user_id       = Column(Integer, nullable=False)
    title         = Column(String(200), nullable=True)
    origin_city   = Column(String(100), nullable=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _make_tracking_code() -> str:
    return f"TRK-{random.randint(100000, 999999)}-{int(time.time()) % 10000}"


# ── Schemas ────────────────────────────────────────────────────────────────────
class PackageCreate(BaseModel):
    user_id: int
    title: str = "Sin título"
    origin_city: str = "ORIGEN"

class PackageResponse(BaseModel):
    id: int
    tracking_code: str
    user_id: int
    title: str | None
    origin_city: str | None
    class Config:
        from_attributes = True


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="Package Service", version="1.0.0",
              description="Microservicio de gestión de paquetes")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Package Service iniciado — tablas listas")


@app.get("/health")
def health():
    return {"service": "package-service", "status": "up"}


@user_service_breaker
def _validate_user_exists(user_id: int) -> bool:
    """
    Circuit Breaker: llama a user-service para validar que el usuario existe.
    Si el circuito está abierto, lanza CallNotPermittedError y evitamos
    cascada de fallos.
    """
    resp = httpx.get(f"{USER_SERVICE_URL}/users/{user_id}", timeout=3.0)
    return resp.status_code == 200


@app.post("/packages", response_model=PackageResponse, status_code=201)
def create_package(payload: PackageCreate, db: Session = Depends(get_db)):
    """
    SAGA PATTERN (coreografía simplificada):
    Paso 1 – Validar usuario  → user-service  (con Circuit Breaker)
    Paso 2 – Crear paquete    → packages_db   (este servicio)
    Paso 3 – Crear evento     → tracking-service (llamada HTTP síncrona)
    Si el paso 3 falla, se ejecuta compensación eliminando el paquete creado.
    """
    # ── Paso 1: validar usuario (Circuit Breaker) ──
    try:
        user_ok = _validate_user_exists(payload.user_id)
        if not user_ok:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except pybreaker.CircuitBreakerError:
        logger.warning("Circuit Breaker ABIERTO — user-service no disponible")
        raise HTTPException(status_code=503,
                            detail="Servicio de usuarios temporalmente no disponible")
    except httpx.RequestError:
        raise HTTPException(status_code=503,
                            detail="No se pudo contactar al servicio de usuarios")

    # ── Paso 2: crear paquete ──
    code = _make_tracking_code()
    pkg = PackageModel(
        tracking_code=code,
        user_id=payload.user_id,
        title=payload.title,
        origin_city=payload.origin_city,
    )
    db.add(pkg)
    db.commit()
    db.refresh(pkg)
    logger.info(f"Paquete creado: tracking_code={code}, user_id={payload.user_id}")

    # ── Paso 3: registrar evento inicial en tracking-service ──
    try:
        resp = httpx.post(
            f"{TRACKING_SERVICE_URL}/tracking/events",
            json={
                "tracking_code": code,
                "status": "CREATED",
                "location": payload.origin_city,
                "note": "Paquete registrado en el sistema",
            },
            timeout=3.0,
        )
        if resp.status_code not in (200, 201):
            raise Exception(f"tracking-service respondió {resp.status_code}")
    except Exception as e:
        # ── Compensación (rollback del Saga) ──
        logger.error(f"Saga compensación: eliminando paquete {code} — {e}")
        db.delete(pkg)
        db.commit()
        raise HTTPException(status_code=500,
                            detail="Error al registrar evento inicial; paquete revertido")

    return pkg


@app.get("/packages", response_model=list[PackageResponse])
def list_packages(db: Session = Depends(get_db)):
    return db.query(PackageModel).all()


@app.get("/packages/{tracking_code}", response_model=PackageResponse)
def get_package(tracking_code: str, db: Session = Depends(get_db)):
    pkg = db.query(PackageModel).filter(
        PackageModel.tracking_code == tracking_code
    ).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    return pkg
