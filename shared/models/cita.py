# ============================================================
# cita.py
# Ubicación: EcoSistemaSalud/shared/models/cita.py
# Modelo de citas médicas entre paciente, doctor y clínica
# ============================================================

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
from enum import Enum


# Estados del ciclo de vida de una cita
class EstadoCita(str, Enum):
    PENDIENTE   = "pendiente"    # Recién agendada
    CONFIRMADA  = "confirmada"   # Confirmada por la clínica
    CANCELADA   = "cancelada"    # Cancelada por cualquier parte
    COMPLETADA  = "completada"   # Atención realizada


class Cita(BaseModel):
    id:         UUID
    paciente_id: UUID
    doctor_id:   UUID
    clinica_id:  UUID

    # Fecha y hora exacta de la cita
    fecha_hora: datetime

    # Estado inicial siempre es PENDIENTE
    estado: EstadoCita = EstadoCita.PENDIENTE

    motivo:             Optional[str] = None
    duracion_minutos:   int           = 30   # Por defecto 30 minutos

    class Config:
        json_schema_extra = {
            "example": {
                "paciente_id":      "123e4567-e89b-12d3-a456-426614174000",
                "doctor_id":        "987fcdeb-51a2-43d7-9b56-141613174000",
                "clinica_id":       "555abcde-1234-5678-90ab-cdef12345678",
                "fecha_hora":       "2026-06-25T10:30:00",
                "motivo":           "Control de rutina"
            }
        }