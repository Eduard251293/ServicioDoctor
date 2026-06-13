# ============================================================
# paciente.py
# Ubicación: EcoSistemaSalud/shared/models/paciente.py
# Modelo Pydantic del Paciente compartido por todos los servicios
# Cualquier servicio que necesite datos de paciente importa desde aquí
# ============================================================

from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional
from uuid import UUID, uuid4


class Paciente(BaseModel):
    # ID único universal — se genera automáticamente si no se pasa
    id: UUID = Field(default_factory=uuid4)

    # Datos personales obligatorios
    nombre:               str = Field(..., min_length=2, max_length=100)
    email:                EmailStr
    fecha_nacimiento:     date
    documento_identidad:  str = Field(..., min_length=6, max_length=20)

    # Datos opcionales
    telefono:      Optional[str] = None
    direccion:     Optional[str] = None
    seguro_medico: Optional[str] = None

    class Config:
        # Ejemplo que aparecerá en la documentación Swagger automática
        json_schema_extra = {
            "example": {
                "nombre":              "Ana María Pérez",
                "email":               "ana.perez@email.com",
                "fecha_nacimiento":    "1985-06-15",
                "documento_identidad": "12345678"
            }
        }