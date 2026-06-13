# ============================================================
# doctor.py
# Ubicación: EcoSistemaSalud/shared/models/doctor.py
# Modelo Pydantic del Doctor compartido por todos los servicios
# Incluye el enum de especialidades médicas
# ============================================================

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum


# Especialidades disponibles en el sistema
class Especialidad(str, Enum):
    CARDIOLOGIA      = "cardiologia"
    PEDIATRIA        = "pediatria"
    GINECOLOGIA      = "ginecologia"
    MEDICINA_GENERAL = "medicina_general"
    TRAUMATOLOGIA    = "traumatologia"


class Doctor(BaseModel):
    # ID único universal
    id: UUID = Field(default_factory=uuid4)

    # Datos obligatorios
    nombre:           str = Field(..., min_length=2, max_length=100)
    email:            EmailStr
    especialidad:     Especialidad
    colegiado_numero: str   # Número de colegiatura médica

    # Datos opcionales
    telefono:   Optional[str]  = None
    clinica_id: Optional[UUID] = None  # Clínica donde trabaja (si aplica)

    class Config:
        json_schema_extra = {
            "example": {
                "nombre":           "Dr. Carlos Rodríguez",
                "email":            "carlos.rodriguez@clinica.com",
                "especialidad":     "cardiologia",
                "colegiado_numero": "12345ABC"
            }
        }