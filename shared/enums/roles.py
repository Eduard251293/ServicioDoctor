# ============================================================
# roles.py
# Ubicación: EcoSistemaSalud/shared/enums/roles.py
# Define los roles del sistema compartidos por todos los servicios
# ============================================================

from enum import Enum

class RolSistema(str, Enum):
    PACIENTE       = "paciente"
    DOCTOR         = "doctor"
    CLINICA        = "clinica"
    ADMINISTRADOR  = "administrador"
    FARMACIA       = "farmacia"