# ============================================================
# historial.py
# Ubicación: EcoSistemaSalud/shared/models/historial.py
# Modelos del historial clínico y diagnósticos
# Un paciente tiene un historial con múltiples diagnósticos
# ============================================================

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class Diagnostico(BaseModel):
    # ID opcional — se asigna al guardar en BD
    id: Optional[UUID] = None

    # Relaciones obligatorias
    paciente_id: UUID
    doctor_id:   UUID

    # Contenido del diagnóstico
    descripcion:   str = Field(..., min_length=5)
    observaciones: Optional[str] = None

    # Fecha automática al momento de crear
    fecha: datetime = Field(default_factory=datetime.now)


class HistorialClinico(BaseModel):
    paciente_id: UUID

    # Listas que se van llenando con el tiempo
    diagnosticos:         List[Diagnostico] = []
    alergias:             List[str]         = []
    condiciones_cronicas: List[str]         = []

    class Config:
        json_schema_extra = {
            "example": {
                "paciente_id":         "123e4567-e89b-12d3-a456-426614174000",
                "alergias":            ["penicilina", "polen"],
                "condiciones_cronicas": ["hipertensión"]
            }
        }