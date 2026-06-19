# ============================================================
# ENDPOINT: GET /pacientes/{paciente_id}/recetas
# Servicio: ServicioDoctores
# Acción: Lista TODAS las recetas de un paciente, sin importar
#         qué doctor las emitió. Pensado para que OTROS SERVICIOS
#         (ServicioPaciente, ServicioClinicas, etc.) lo consuman.
# Tabla BD: pacientes.recetas
#
# SIN AUTENTICACIÓN por ahora (endpoint público entre servicios),
# igual que GET /doctores. Más adelante se puede proteger con
# una API Key de servicio.
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal, Base

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

router = APIRouter()

# ── Modelo ORM ──────────────────────────────────────────────────────────────
class Receta(Base):
    """Mapea pacientes.recetas de PostgreSQL"""
    __tablename__  = "recetas"
    __table_args__ = {"schema": "pacientes", "extend_existing": True}

    id                = Column(Integer,    primary_key=True)
    paciente_id       = Column(Integer,    nullable=False)
    doctor_id         = Column(Integer,    nullable=False)
    orden_medica_id   = Column(Integer)
    medicamento       = Column(String(150),nullable=False)
    dosis             = Column(String(100))
    duracion          = Column(String(100))
    indicaciones      = Column(Text)
    fecha_emision     = Column(Date,       default=date.today)
    fecha_vencimiento = Column(Date)
    estado            = Column(String(30), default="VIGENTE")
    creado_en         = Column(DateTime,   default=datetime.utcnow)

# ── Schema Pydantic ───────────────────────────────────────────────────────────
class RecetaPublicaResponse(BaseModel):
    """
    CONTRATO DE SALIDA
    Lo que recibe el servicio que consume este endpoint
    """
    id:                 int
    paciente_id:        int
    doctor_id:          int
    orden_medica_id:    Optional[int]
    medicamento:        str
    dosis:              Optional[str]
    duracion:           Optional[str]
    indicaciones:       Optional[str]
    fecha_emision:      Optional[date]
    fecha_vencimiento:  Optional[date]
    estado:             str

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
    "/pacientes/{paciente_id}/recetas",
    response_model = List[RecetaPublicaResponse],
    tags           = ["ServicioDoctores"],
    summary        = "Listar recetas de un paciente (consumo entre servicios)",
    description    = """
    Devuelve TODAS las recetas emitidas a un paciente, sin importar el doctor.
    Pensado para que OTROS SERVICIOS (ServicioPaciente, ServicioClinicas, etc.)
    consulten directamente por el ID del paciente.

    Filtro opcional:
    - estado: VIGENTE | ENTREGADO | CADUCADO

    NOTA: Este endpoint NO requiere autenticación por ahora,
    igual que GET /doctores.
    """
)
def get_recetas_por_paciente(
    paciente_id: int,
    estado: Optional[str] = Query(None, description="Filtrar por estado: VIGENTE, ENTREGADO, CADUCADO"),
    db: Session = Depends(get_db)
):
    query = db.query(Receta).filter(Receta.paciente_id == paciente_id)

    if estado:
        estados_validos = ["VIGENTE", "ENTREGADO", "CADUCADO"]
        if estado.upper() not in estados_validos:
            raise HTTPException(
                status_code = 400,
                detail      = f"Estado inválido. Opciones: {estados_validos}"
            )
        query = query.filter(Receta.estado == estado.upper())

    recetas = query.order_by(Receta.fecha_emision.desc()).all()

    return recetas