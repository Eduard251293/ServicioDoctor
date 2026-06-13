# ============================================================
# ENDPOINT: GET /doctor/{id}/pacientes-atendidos
# Servicio: ServicioDoctores
# Acción: Lista pacientes asignados + actividad clínica del doctor
# Tablas BD: doctores.doctores, doctores.doctores_pacientes,
#            doctores.diagnosticos, doctores.ordenes_medicas
#
# PROTEGIDO CON JWT: requiere header Authorization: Bearer <token>
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import SessionLocal, Base

# ── NUEVO: importar la dependencia que valida el JWT ──────────────────────────
from auth.jwt_config import get_doctor_actual

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean
from datetime import date, datetime

router = APIRouter()

# ── Modelos ORM ───────────────────────────────────────────────────────────────
class Doctor(Base):
    __tablename__  = "doctores"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id                 = Column(Integer, primary_key=True)
    nombres            = Column(String(100))
    apellidos          = Column(String(100))
    especialidad       = Column(String(100))
    numero_colegiatura = Column(String(50))
    activo             = Column(Boolean, default=True)

class DoctorPaciente(Base):
    __tablename__  = "doctores_pacientes"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id               = Column(Integer,  primary_key=True)
    doctor_id        = Column(Integer,  nullable=False)
    paciente_id      = Column(Integer,  nullable=False)
    fecha_asignacion = Column(DateTime, default=datetime.utcnow)
    activo           = Column(Boolean,  default=True)

class Diagnostico(Base):
    __tablename__  = "diagnosticos"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id                 = Column(Integer, primary_key=True)
    paciente_id        = Column(Integer)
    doctor_id          = Column(Integer)
    nombre_diagnostico = Column(String(200))
    codigo_cie         = Column(String(20))
    gravedad           = Column(String(30))
    fecha_diagnostico  = Column(Date)

class OrdenMedica(Base):
    __tablename__  = "ordenes_medicas"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id                = Column(Integer, primary_key=True)
    paciente_id       = Column(Integer)
    doctor_id         = Column(Integer)
    tipo_orden        = Column(String(50))
    estado            = Column(String(30))
    fecha_vencimiento = Column(Date)

# ── Dependencia BD ────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── ENDPOINT ──────────────────────────────────────────────────────────────────
@router.get(
    "/doctor/{doctor_id}/pacientes-atendidos",
    tags        = ["ServicioDoctores"],
    summary     = "Pacientes atendidos por el doctor",
    description = """
    Lista todos los pacientes asignados al doctor
    y su historial de diagnósticos y órdenes médicas emitidas.

    Requiere autenticación: Authorization: Bearer <token>
    """
)
def get_pacientes_atendidos(
    doctor_id: int,
    db: Session = Depends(get_db),
    # ── NUEVO: exige el JWT y trae los datos del doctor autenticado ───────────
    doctor_actual: dict = Depends(get_doctor_actual)
):
    # ── NUEVO REGLA 0: El doctor del token debe coincidir con el de la URL ────
    if doctor_actual["doctor_id"] != doctor_id:
        raise HTTPException(
            status_code = 403,
            detail      = "No puedes consultar la información de otro doctor"
        )

    # ── REGLA 1: Doctor existe ────────────────────────────────────────────────
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code = 404,
            detail      = f"Doctor ID {doctor_id} no encontrado"
        )

    # Pacientes asignados activos
    relaciones = db.query(DoctorPaciente).filter(
        DoctorPaciente.doctor_id == doctor_id,
        DoctorPaciente.activo    == True
    ).all()

    # Diagnósticos emitidos por este doctor
    diagnosticos = db.query(Diagnostico).filter(
        Diagnostico.doctor_id == doctor_id
    ).all()

    # Órdenes médicas emitidas por este doctor
    ordenes = db.query(OrdenMedica).filter(
        OrdenMedica.doctor_id == doctor_id
    ).all()

    return {
        "doctor": {
            "id"          : doctor.id,
            "nombre"      : f"Dr. {doctor.nombres} {doctor.apellidos}",
            "especialidad": doctor.especialidad,
            "colegiatura" : doctor.numero_colegiatura
        },
        "pacientes_asignados": [
            {
                "paciente_id"     : r.paciente_id,
                "fecha_asignacion": str(r.fecha_asignacion)
            }
            for r in relaciones
        ],
        "total_pacientes"  : len(relaciones),
        "diagnosticos_emitidos": [
            {
                "id"                : d.id,
                "paciente_id"       : d.paciente_id,
                "nombre_diagnostico": d.nombre_diagnostico,
                "codigo_cie"        : d.codigo_cie,
                "gravedad"          : d.gravedad,
                "fecha"             : str(d.fecha_diagnostico)
            }
            for d in diagnosticos
        ],
        "total_diagnosticos": len(diagnosticos),
        "ordenes_emitidas": [
            {
                "id"         : o.id,
                "paciente_id": o.paciente_id,
                "tipo"       : o.tipo_orden,
                "estado"     : o.estado,
                "vencimiento": str(o.fecha_vencimiento)
            }
            for o in ordenes
        ],
        "total_ordenes": len(ordenes)
    }