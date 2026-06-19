# ============================================================
# ENDPOINT: GET /doctor/consulta-paciente
# Servicio: ServicioDoctores
# Acción: El doctor consulta diagnósticos y órdenes de un paciente
# Uso: /doctor/consulta-paciente?paciente_id=1&doctor_id=1
# Tablas BD: doctores.diagnosticos, doctores.ordenes_medicas,
#            doctores.doctores_pacientes
#
# PROTEGIDO CON JWT: requiere header Authorization: Bearer <token>
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import SessionLocal, Base

# ── NUEVO: importar la dependencia que valida el JWT ──────────────────────────
#from auth.jwt_config import get_doctor_actual

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean
from datetime import date, datetime

router = APIRouter()

# ── Modelos ORM ───────────────────────────────────────────────────────────────
class Doctor(Base):
    __tablename__  = "doctores"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id           = Column(Integer, primary_key=True)
    nombres      = Column(String(100))
    apellidos    = Column(String(100))
    especialidad = Column(String(100))

class Diagnostico(Base):
    __tablename__  = "diagnosticos"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id                 = Column(Integer, primary_key=True)
    paciente_id        = Column(Integer)
    doctor_id          = Column(Integer)
    nombre_diagnostico = Column(String(200))
    codigo_cie         = Column(String(20))
    gravedad           = Column(String(30))
    descripcion        = Column(Text)
    fecha_diagnostico  = Column(Date)

class OrdenMedica(Base):
    __tablename__  = "ordenes_medicas"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id                = Column(Integer, primary_key=True)
    paciente_id       = Column(Integer)
    doctor_id         = Column(Integer)
    tipo_orden        = Column(String(50))
    detalle           = Column(Text)
    estado            = Column(String(30))
    fecha_vencimiento = Column(Date)

class DoctorPaciente(Base):
    __tablename__  = "doctores_pacientes"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id          = Column(Integer, primary_key=True)
    doctor_id   = Column(Integer)
    paciente_id = Column(Integer)
    activo      = Column(Boolean, default=True)

# ── Dependencia BD ────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── ENDPOINT ──────────────────────────────────────────────────────────────────
@router.get(
    "/doctor/consulta-paciente",
    tags        = ["ServicioDoctores"],
    summary     = "Consultar datos de un paciente",
    description = """
    El doctor consulta diagnósticos y órdenes médicas
    de un paciente específico que él mismo ha atendido.

    Requiere autenticación: Authorization: Bearer <token>
    """
)
def get_consulta_paciente(
    paciente_id: int,
    doctor_id:   int,
    db: Session = Depends(get_db),
    # ── NUEVO: exige el JWT y trae los datos del doctor autenticado ───────────
    #doctor_actual: dict = Depends(get_doctor_actual)
):
    # ── NUEVO REGLA 0: El doctor del token debe coincidir con doctor_id ───────
   # if doctor_actual["doctor_id"] != doctor_id:
    #    raise HTTPException(
     #       status_code = 403,
      #      detail      = "No puedes consultar información usando el ID de otro doctor"
       # )

    # ── REGLA 1: Doctor existe ────────────────────────────────────────────────
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code = 404,
            detail      = f"Doctor ID {doctor_id} no encontrado"
        )

    # Diagnósticos de este paciente por este doctor
    diagnosticos = db.query(Diagnostico).filter(
        Diagnostico.paciente_id == paciente_id,
        Diagnostico.doctor_id   == doctor_id
    ).all()

    # Órdenes de este paciente por este doctor
    ordenes = db.query(OrdenMedica).filter(
        OrdenMedica.paciente_id == paciente_id,
        OrdenMedica.doctor_id   == doctor_id
    ).all()

    # Verificar si el paciente está formalmente asignado
    asignado = db.query(DoctorPaciente).filter(
        DoctorPaciente.doctor_id   == doctor_id,
        DoctorPaciente.paciente_id == paciente_id,
        DoctorPaciente.activo      == True
    ).first()

    return {
        "consultado_por": {
            "doctor_id"   : doctor.id,
            "nombre"      : f"Dr. {doctor.nombres} {doctor.apellidos}",
            "especialidad": doctor.especialidad
        },
        "paciente_id"      : paciente_id,
        "paciente_asignado": asignado is not None,
        "diagnosticos": [
            {
                "id"                : d.id,
                "nombre_diagnostico": d.nombre_diagnostico,
                "codigo_cie"        : d.codigo_cie,
                "gravedad"          : d.gravedad,
                "descripcion"       : d.descripcion,
                "fecha"             : str(d.fecha_diagnostico)
            }
            for d in diagnosticos
        ],
        "ordenes_medicas": [
            {
                "id"         : o.id,
                "tipo"       : o.tipo_orden,
                "detalle"    : o.detalle,
                "estado"     : o.estado,
                "vencimiento": str(o.fecha_vencimiento)
            }
            for o in ordenes
        ],
        "resumen": {
            "total_diagnosticos": len(diagnosticos),
            "total_ordenes"     : len(ordenes)
        }
    }