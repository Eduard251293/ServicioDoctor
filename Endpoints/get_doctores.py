# ============================================================
# ENDPOINT: GET /doctores
# Servicio: ServicioDoctores
# Acción: Lista los doctores registrados para que OTROS SERVICIOS
#         (ServicioClinicas, ServicioPaciente, etc.) los consuman.
# Tabla BD: doctores.doctores
#
# SIN AUTENTICACIÓN por ahora (endpoint público entre servicios).
# Más adelante se puede proteger con una API Key de servicio.
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import SessionLocal, Base

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()

# ── Modelo ORM ──────────────────────────────────────────────────────────────
class Doctor(Base):
    """Mapea doctores.doctores de PostgreSQL"""
    __tablename__  = "doctores"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id                 = Column(Integer, primary_key=True)
    nombres            = Column(String(100))
    apellidos          = Column(String(100))
    especialidad       = Column(String(100))
    numero_colegiatura = Column(String(50))
    telefono           = Column(String(20))
    email              = Column(String(100))
    activo             = Column(Boolean, default=True)
    fecha_registro     = Column(DateTime)

# ── Schema Pydantic ───────────────────────────────────────────────────────────
class DoctorResponse(BaseModel):
    """
    CONTRATO DE SALIDA
    Lo que recibe el servicio que consume este endpoint
    """
    id:                 int
    nombres:            str
    apellidos:          str
    especialidad:       str
    numero_colegiatura: str
    telefono:           Optional[str]
    email:              Optional[str]
    activo:             bool

    class Config:
        from_attributes = True

# ── Dependencia BD ────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── ENDPOINT ──────────────────────────────────────────────────────────────────
@router.get(
    "/doctores",
    response_model = List[DoctorResponse],
    tags           = ["ServicioDoctores"],
    summary        = "Listar doctores (consumo entre servicios)",
    description    = """
    Devuelve la lista de doctores registrados.
    Pensado para que OTROS SERVICIOS (ServicioClinicas, ServicioPaciente, etc.)
    obtengan el catálogo de doctores.

    Filtros opcionales:
    - especialidad: filtra por especialidad exacta (ej: "Cardiología")
    - activo: filtra por estado (true/false). Por defecto solo activos.

    NOTA: Este endpoint NO requiere autenticación por ahora.
    """
)
def get_doctores(
    especialidad: Optional[str] = Query(None, description="Filtrar por especialidad"),
    activo:       Optional[bool] = Query(True, description="Filtrar por estado activo/inactivo"),
    db: Session = Depends(get_db)
):
    # ── Construir la consulta base ────────────────────────────────────────────
    query = db.query(Doctor)

    # ── Filtro por estado activo ──────────────────────────────────────────────
    # Si activo=None, no se filtra (devuelve activos e inactivos)
    if activo is not None:
        query = query.filter(Doctor.activo == activo)

    # ── Filtro por especialidad (insensible a mayúsculas/minúsculas) ──────────
    if especialidad:
        query = query.filter(Doctor.especialidad.ilike(especialidad))

    doctores = query.order_by(Doctor.apellidos, Doctor.nombres).all()

    return doctores