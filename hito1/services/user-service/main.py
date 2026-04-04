"""
User Service - Microservicio de Gestión de Usuarios
Responsabilidad: CRUD de usuarios del sistema de tracking de paquetes.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from prometheus_fastapi_instrumentator import Instrumentator
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Base de datos ──────────────────────────────────────────────────────────────
DB_URL = (
    f"postgresql://{os.getenv('DB_USER','tracker')}:"
    f"{os.getenv('DB_PASSWORD','tracker_secret')}@"
    f"{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','5432')}/"
    f"{os.getenv('DB_NAME','users_db')}"
)
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True)
    email    = Column(String(255), nullable=False, unique=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Schemas ────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="User Service", version="1.0.0", description="Microservicio de usuarios")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Prometheus metrics
Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    logger.info("User Service iniciado — tablas listas")


@app.get("/health")
def health():
    return {"service": "user-service", "status": "up"}


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(
        (UserModel.username == payload.username) | (UserModel.email == payload.email)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Usuario ya existe")
    user = UserModel(username=payload.username, email=payload.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Usuario creado: id={user.id}, username={user.username}")
    return user


@app.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
