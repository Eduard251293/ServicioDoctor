# ============================================================
# ENDPOINT: POST /auth/registro
# Servicio: ServicioDoctor
# Acción: Registrar credenciales de login para un doctor existente
# Quién lo usa: El administrador del sistema
# Flujo: El otro servicio ya creó al doctor en doctores.doctores
#        Este endpoint le asigna usuario + contraseña para poder hacer login
# Tabla BD: doctores.doctor_credenciales
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal, Base

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from pydantic import BaseModel, field_validator
from passlib.context import CryptContext
from datetime import datetime

router = APIRouter()

# ── Configuración de bcrypt ───────────────────────────────────────────────────
# CryptContext maneja el hasheo de contraseñas con bcrypt
# bcrypt es el algoritmo recomendado: lento a propósito para dificultar ataques
# deprecated="auto" actualiza automáticamente contraseñas con algoritmos viejos
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Modelos ORM ───────────────────────────────────────────────────────────────

class Doctor(Base):
    """Mapea doctores.doctores — solo para verificar que el doctor existe"""
    __tablename__  = "doctores"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id                 = Column(Integer, primary_key=True)
    nombres            = Column(String(100))
    apellidos          = Column(String(100))
    numero_colegiatura = Column(String(50))
    activo             = Column(Boolean, default=True)


class DoctorCredencial(Base):
    """Mapea doctores.doctor_credenciales — la tabla que creamos en el Paso 1"""
    __tablename__  = "doctor_credenciales"
    __table_args__ = {"schema": "doctores", "extend_existing": True}

    id                 = Column(Integer,  primary_key=True)
    doctor_id          = Column(Integer,  nullable=False)
    numero_colegiatura = Column(String(50), nullable=False, unique=True)
    password_hash      = Column(String(255), nullable=False)
    activo             = Column(Boolean,  default=True)
    creado_en          = Column(DateTime, default=datetime.utcnow)
    actualizado_en     = Column(DateTime, default=datetime.utcnow)


# ── Schemas Pydantic ──────────────────────────────────────────────────────────

class RegistroRequest(BaseModel):
    """
    CONTRATO DE ENTRADA
    Lo que el administrador envía para crear credenciales a un doctor
    """
    # El número de colegiatura del doctor (debe existir en doctores.doctores)
    numero_colegiatura: str

    # La contraseña que se asignará al doctor (mínimo 6 caracteres)
    password: str

    @field_validator("password")
    @classmethod
    def validar_password(cls, v):
        """Valida que la contraseña tenga al menos 6 caracteres"""
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v

    @field_validator("numero_colegiatura")
    @classmethod
    def validar_colegiatura(cls, v):
        """Limpia espacios del número de colegiatura"""
        return v.strip().upper()


class RegistroResponse(BaseModel):
    """CONTRATO DE SALIDA — lo que devolvemos al administrador"""
    mensaje:            str
    doctor_id:          int
    nombre_doctor:      str
    numero_colegiatura: str


# ── Dependencia BD ────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── ENDPOINT ──────────────────────────────────────────────────────────────────
@router.post(
    "/auth/registro",
    response_model = RegistroResponse,
    status_code    = 201,
    tags           = ["Autenticación"],
    summary        = "Registrar credenciales de login para un doctor",
    description    = """
    Registra usuario y contraseña para un doctor que ya existe en el sistema.
    El número de colegiatura debe existir en doctores.doctores.
    Solo se puede registrar UNA VEZ por doctor (no duplicados).
    """
)
def post_auth_registro(
    datos: RegistroRequest,
    db:    Session = Depends(get_db)
):
    # ── PASO 1: Verificar que el doctor existe en doctores.doctores ───────────
    # Si el otro servicio aún no lo creó, no podemos registrar credenciales
    doctor = db.query(Doctor).filter(
        Doctor.numero_colegiatura == datos.numero_colegiatura
    ).first()

    if not doctor:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = f"No existe ningún doctor con colegiatura '{datos.numero_colegiatura}'. "
                          f"El doctor debe ser creado primero por el servicio correspondiente."
        )

    # ── PASO 2: Verificar que el doctor esté activo ───────────────────────────
    if not doctor.activo:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = f"El doctor con colegiatura '{datos.numero_colegiatura}' está inactivo."
        )

    # ── PASO 3: Verificar que no tenga credenciales ya registradas ────────────
    # Cada doctor solo puede tener UN registro de credenciales
    credencial_existente = db.query(DoctorCredencial).filter(
        DoctorCredencial.numero_colegiatura == datos.numero_colegiatura
    ).first()

    if credencial_existente:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail      = f"El doctor con colegiatura '{datos.numero_colegiatura}' "
                          f"ya tiene credenciales registradas. Usa el endpoint de cambio de contraseña."
        )

    # ── PASO 4: Hashear la contraseña con bcrypt ──────────────────────────────
    # NUNCA guardamos la contraseña real, siempre el hash
    # bcrypt genera un hash diferente cada vez (incluye salt automático)
    # Ejemplo: "mi_clave" → "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8..."
    password_hasheada = pwd_context.hash(datos.password)

    # ── PASO 5: Guardar las credenciales en la BD ─────────────────────────────
    nueva_credencial = DoctorCredencial(
        doctor_id          = doctor.id,
        numero_colegiatura = datos.numero_colegiatura,
        password_hash      = password_hasheada,
        activo             = True
    )

    db.add(nueva_credencial)
    db.commit()
    db.refresh(nueva_credencial)

    # ── Registrar en consola (para debug) ─────────────────────────────────────
    print(f"[AUTH] CREDENCIALES_REGISTRADAS → "
          f"Dr. {doctor.nombres} {doctor.apellidos} | "
          f"Colegiatura: {datos.numero_colegiatura}")

    return RegistroResponse(
        mensaje            = "Credenciales registradas exitosamente",
        doctor_id          = doctor.id,
        nombre_doctor      = f"Dr. {doctor.nombres} {doctor.apellidos}",
        numero_colegiatura = datos.numero_colegiatura
    )