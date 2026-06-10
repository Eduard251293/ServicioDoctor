# ============================================================
# ENDPOINT: POST /doctor/diagnostico
# Servicio: ServicioDoctores
# Acción: El doctor emite un diagnóstico para un paciente
# Tabla BD: doctores.diagnosticos
# ============================================================

import sys
import os

# Subir dos niveles para llegar a EcoSistemaSalud/database.py
# ServicioDoctores/Endpoints/ → ServicioDoctores/ → EcoSistemaSalud/
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import SessionLocal, Base

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

# ── Router ────────────────────────────────────────────────────────────────────
# APIRouter es como un "mini-app" que se conecta al main.py
router = APIRouter()

# ── Modelos ORM ───────────────────────────────────────────────────────────────
class Doctor(Base):
    """Mapea doctores.doctores de PostgreSQL"""
    __tablename__  = "doctores"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id       = Column(Integer, primary_key=True)
    nombres  = Column(String(100))
    apellidos= Column(String(100))
    activo   = Column(Boolean, default=True)

class Diagnostico(Base):
    """Mapea doctores.diagnosticos de PostgreSQL"""
    __tablename__  = "diagnosticos"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id                 = Column(Integer, primary_key=True)
    paciente_id        = Column(Integer,     nullable=False)
    doctor_id          = Column(Integer,     nullable=False)
    codigo_cie         = Column(String(20))
    nombre_diagnostico = Column(String(200), nullable=False)
    descripcion        = Column(Text)
    fecha_diagnostico  = Column(Date,        default=date.today)
    gravedad           = Column(String(30))
    creado_en          = Column(DateTime,    default=datetime.utcnow)

# ── Schemas Pydantic ──────────────────────────────────────────────────────────
class DiagnosticoCreate(BaseModel):
    """
    CONTRATO DE ENTRADA
    Lo que el cliente debe enviar al llamar este endpoint
    """
    paciente_id:        int
    doctor_id:          int
    codigo_cie:         Optional[str] = None  # Ej: J06.9=Gripe, I10=Hipertensión
    nombre_diagnostico: str
    descripcion:        Optional[str] = None
    gravedad:           Optional[str] = "LEVE"  # LEVE|MODERADO|GRAVE|CRITICO

class DiagnosticoResponse(BaseModel):
    """
    CONTRATO DE SALIDA
    Lo que el servicio devuelve al cliente
    """
    id:                 int
    paciente_id:        int
    doctor_id:          int
    codigo_cie:         Optional[str]
    nombre_diagnostico: str
    descripcion:        Optional[str]
    fecha_diagnostico:  Optional[date]
    gravedad:           Optional[str]
    class Config:
        from_attributes = True

# ── Dependencia de sesión BD ──────────────────────────────────────────────────
def get_db():
    """Abre y cierra la sesión de BD por cada request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── ENDPOINT ──────────────────────────────────────────────────────────────────
@router.post(
    "/doctor/diagnostico",
    response_model = DiagnosticoResponse,
    status_code    = 201,
    tags           = ["ServicioDoctores"],
    summary        = "Emitir diagnóstico médico",
    description    = """
    El doctor registra un diagnóstico para un paciente.
    Incluye código CIE-10 (estándar internacional de enfermedades).
    Ejemplos: J06.9=Gripe, I10=Hipertensión, E11=Diabetes tipo 2
    """
)
def post_doctor_diagnostico(
    datos: DiagnosticoCreate,
    db:    Session = Depends(get_db)
):
    # ── REGLA 1: Verificar que el doctor existe ───────────────────────────────
    doctor = db.query(Doctor).filter(
        Doctor.id == datos.doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code = 404,
            detail      = f"Doctor ID {datos.doctor_id} no encontrado"
        )

    # ── REGLA 2: Validar gravedad ─────────────────────────────────────────────
    gravedades_validas = ["LEVE", "MODERADO", "GRAVE", "CRITICO"]
    gravedad = (datos.gravedad or "LEVE").upper()

    if gravedad not in gravedades_validas:
        raise HTTPException(
            status_code = 400,
            detail      = f"Gravedad inválida. Opciones: {gravedades_validas}"
        )

    # ── GUARDAR en PostgreSQL ─────────────────────────────────────────────────
    nuevo = Diagnostico(
        paciente_id        = datos.paciente_id,
        doctor_id          = datos.doctor_id,
        codigo_cie         = datos.codigo_cie,
        nombre_diagnostico = datos.nombre_diagnostico,
        descripcion        = datos.descripcion,
        gravedad           = gravedad,
        fecha_diagnostico  = date.today()
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    # ── EVENTO SOA (simulado) ─────────────────────────────────────────────────
    # En producción: publicar a RabbitMQ/Kafka
    print(f"[EVENTO] DIAGNOSTICO_EMITIDO → "
          f"Dr. {doctor.nombres} {doctor.apellidos} | "
          f"Paciente ID: {datos.paciente_id} | "
          f"CIE: {datos.codigo_cie} | "
          f"Diagnóstico: {datos.nombre_diagnostico}")

    return nuevo