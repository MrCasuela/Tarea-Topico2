"""
Tracking Service - Microservicio de Eventos de Seguimiento
Responsabilidad: registrar eventos de estado y consultar historial de paquetes.
"""
import os
import logging

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.sql import func
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Base de datos ──────────────────────────────────────────────────────────────
DB_URL = (
    f"postgresql://{os.getenv('DB_USER','tracker')}:"
    f"{os.getenv('DB_PASSWORD','tracker_secret')}@"
    f"{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','5432')}/"
    f"{os.getenv('DB_NAME','tracking_db')}"
)
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

VALID_STATUSES = {"CREATED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED", "EXCEPTION"}


class TrackingEvent(Base):
    __tablename__ = "tracking_events"
    id            = Column(Integer, primary_key=True, index=True)
    tracking_code = Column(String(64), nullable=False, index=True)
    status        = Column(String(50), nullable=False)
    location      = Column(String(200), nullable=True)
    note          = Column(Text, nullable=True)
    recorded_at   = Column(DateTime(timezone=True), server_default=func.now())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Schemas ────────────────────────────────────────────────────────────────────
class EventCreate(BaseModel):
    tracking_code: str
    status: str
    location: str = ""
    note: str = ""

class EventResponse(BaseModel):
    id: int
    tracking_code: str
    status: str
    location: str | None
    note: str | None
    recorded_at: str | None
    class Config:
        from_attributes = True

class TrackingHistory(BaseModel):
    tracking_code: str
    current_status: str
    events: list[EventResponse]


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="Tracking Service", version="1.0.0",
              description="Microservicio de eventos de seguimiento de paquetes")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Tracking Service iniciado — tablas listas")


@app.get("/health")
def health():
    return {"service": "tracking-service", "status": "up"}


@app.post("/tracking/events", response_model=EventResponse, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    """Registra un nuevo evento de tracking (llamado por package-service o directamente)."""
    status_upper = payload.status.upper()
    if status_upper not in VALID_STATUSES:
        raise HTTPException(status_code=400,
                            detail=f"Estado inválido. Válidos: {VALID_STATUSES}")
    event = TrackingEvent(
        tracking_code=payload.tracking_code,
        status=status_upper,
        location=payload.location,
        note=payload.note or f"Estado actualizado a {status_upper}",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    logger.info(f"Evento registrado: {payload.tracking_code} → {status_upper}")
    # Serializamos recorded_at manualmente para el response
    event_dict = {
        "id": event.id,
        "tracking_code": event.tracking_code,
        "status": event.status,
        "location": event.location,
        "note": event.note,
        "recorded_at": event.recorded_at.isoformat() if event.recorded_at else None,
    }
    return event_dict


@app.post("/tracking/update")
def update_status(payload: EventCreate, db: Session = Depends(get_db)):
    """Actualiza el estado de un paquete creando un nuevo evento."""
    status_upper = payload.status.upper()
    if status_upper not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Estado inválido")

    # Verificar que existe al menos un evento previo
    exists = db.query(TrackingEvent).filter(
        TrackingEvent.tracking_code == payload.tracking_code
    ).first()
    if not exists:
        raise HTTPException(status_code=404,
                            detail="No se encontraron eventos para este código de tracking")

    event = TrackingEvent(
        tracking_code=payload.tracking_code,
        status=status_upper,
        location=payload.location,
        note=payload.note or f"Cambio de estado a {status_upper}",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    logger.info(f"Estado actualizado: {payload.tracking_code} → {status_upper}")
    return {"ok": True, "tracking_code": payload.tracking_code, "status": status_upper}


@app.get("/tracking/{tracking_code}", response_model=TrackingHistory)
def get_tracking(tracking_code: str, db: Session = Depends(get_db)):
    """Retorna el historial completo de eventos de un paquete."""
    events = (
        db.query(TrackingEvent)
        .filter(TrackingEvent.tracking_code == tracking_code)
        .order_by(TrackingEvent.recorded_at.asc())
        .all()
    )
    if not events:
        raise HTTPException(status_code=404, detail="Código de tracking no encontrado")

    events_list = [
        {
            "id": e.id,
            "tracking_code": e.tracking_code,
            "status": e.status,
            "location": e.location,
            "note": e.note,
            "recorded_at": e.recorded_at.isoformat() if e.recorded_at else None,
        }
        for e in events
    ]
    return {
        "tracking_code": tracking_code,
        "current_status": events[-1].status,
        "events": events_list,
    }
