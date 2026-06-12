# ============================================================
# standard_response.py
# Ubicación: EcoSistemaSalud/shared/responses/standard_response.py
# Respuesta estándar que TODOS los servicios deben devolver
# Garantiza que el frontend siempre reciba el mismo formato JSON
# ============================================================

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional
from datetime import datetime
from enum import Enum

# T representa el tipo de dato que va dentro de "data"
# Puede ser Paciente, Doctor, una lista, un dict, etc.
T = TypeVar('T')


class StatusEnum(str, Enum):
    SUCCESS = "success"
    ERROR   = "error"
    WARNING = "warning"


class StandardResponse(BaseModel, Generic[T]):
    # Estado de la operación
    status: StatusEnum

    # Datos devueltos (None si hubo error)
    data: Optional[T] = None

    # Mensaje legible para el frontend
    message: str

    # Fecha y hora automática de la respuesta
    timestamp: datetime = Field(default_factory=datetime.now)

    # Código de error opcional (ej: "P001", "AUTH002")
    error_code: Optional[str] = None

    # ── Métodos de fábrica ────────────────────────────────────────────────────

    @classmethod
    def success(cls, data: T, message: str = "Operación exitosa"):
        """Respuesta exitosa con datos"""
        return cls(status=StatusEnum.SUCCESS, data=data, message=message)

    @classmethod
    def error(cls, message: str, error_code: str = None):
        """Respuesta de error sin datos"""
        return cls(status=StatusEnum.ERROR, message=message, error_code=error_code)

    @classmethod
    def warning(cls, data: T, message: str):
        """Respuesta con advertencia pero con datos"""
        return cls(status=StatusEnum.WARNING, data=data, message=message)

    class Config:
        json_schema_extra = {
            "example_success": {
                "status":    "success",
                "data":      {"id": "123", "nombre": "Ana Pérez"},
                "message":   "Paciente registrado correctamente",
                "timestamp": "2026-05-22T10:30:00"
            },
            "example_error": {
                "status":     "error",
                "data":       None,
                "message":    "Paciente no encontrado",
                "timestamp":  "2026-05-22T10:30:00",
                "error_code": "P001"
            }
        }