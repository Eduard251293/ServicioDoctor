# ============================================================
# receta.py
# Ubicación: EcoSistemaSalud/shared/models/receta.py
# Modelos de recetas médicas y medicamentos
# Una receta contiene una lista de medicamentos
# ============================================================

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from enum import Enum


# Estados posibles de una receta
class EstadoReceta(str, Enum):
    ACTIVA     = "activa"
    CANCELADA  = "cancelada"
    EXPIRADA   = "expirada"
    DISPENSADA = "dispensada"   # Cuando ya fue entregada en farmacia


class Medicamento(BaseModel):
    # Datos del medicamento dentro de la receta
    nombre:        str
    dosis:         str            # Ej: "500mg"
    frecuencia:    str            # Ej: "cada 8 horas"
    duracion_dias: int            # Ej: 7
    indicaciones:  Optional[str] = None  # Ej: "tomar después de comer"


class Receta(BaseModel):
    id:          UUID
    paciente_id: UUID
    doctor_id:   UUID

    # Lista de medicamentos recetados
    medicamentos: List[Medicamento]

    # Fechas
    fecha_emision:    datetime = Field(default_factory=datetime.now)
    fecha_expiracion: datetime

    # Estado inicial siempre es ACTIVA
    estado: EstadoReceta = EstadoReceta.ACTIVA

    notas_adicionales: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "medicamentos": [
                    {
                        "nombre":        "Losartán",
                        "dosis":         "50mg",
                        "frecuencia":    "cada 24 horas",
                        "duracion_dias": 30
                    }
                ],
                "fecha_expiracion": "2026-06-22T00:00:00"
            }
        }