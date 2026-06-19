# ============================================================
# auth/jwt_config.py
# Ubicación: ServicioDoctor/auth/jwt_config.py
# Propósito: Todo lo relacionado con JWT
#   - Crear tokens cuando el doctor hace login
#   - Verificar tokens cuando el doctor llama a un endpoint protegido
#   - Extraer el doctor actual del token
# ============================================================

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

# ── Cargar variables de entorno ───────────────────────────────────────────────
load_dotenv()

# ── Configuración del JWT ─────────────────────────────────────────────────────
# Estos valores vienen del archivo .env
SECRET_KEY      = os.getenv("JWT_SECRET_KEY", "clave_por_defecto_insegura")
ALGORITHM       = os.getenv("JWT_ALGORITHM",  "HS256")
EXPIRE_MINUTES  = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# ── OAuth2PasswordBearer ──────────────────────────────────────────────────────
# Le dice a FastAPI dónde espera recibir el token
# tokenUrl="/auth/login" → apunta al endpoint de login que crearemos
# Cuando un endpoint use Depends(oauth2_scheme), FastAPI extrae
# automáticamente el token del header: Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── FUNCIÓN: Crear un token JWT ───────────────────────────────────────────────
def crear_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea y firma un token JWT con los datos del doctor.

    Parámetros:
        data: diccionario con los datos a guardar en el token
              Ej: {"sub": "CMP-001", "doctor_id": 1, "nombre": "Ana Torres"}
        expires_delta: tiempo de vida del token (si no se pasa, usa el del .env)

    Retorna:
        El token JWT como string (lo que se devuelve al doctor en el login)
    """
    # Copiamos el diccionario para no modificar el original
    payload = data.copy()

    # Calculamos cuándo expira el token
    if expires_delta:
        expira = datetime.now(timezone.utc) + expires_delta
    else:
        expira = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)

    # Agregamos la fecha de expiración al payload del token
    # "exp" es un campo estándar del JWT que jose valida automáticamente
    payload.update({"exp": expira})

    # Firmamos y codificamos el token con la clave secreta
    # jwt.encode() convierte el diccionario a un string JWT firmado
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


# ── FUNCIÓN: Verificar y decodificar un token ─────────────────────────────────
def verificar_token(token: str) -> dict:
    """
    Verifica que el token sea válido y no haya expirado.
    Si algo falla, lanza HTTPException 401 (No autorizado).

    Parámetros:
        token: el string JWT que llegó en el header Authorization

    Retorna:
        El payload (diccionario) con los datos del doctor
    """
    # Preparamos el error que lanzaremos si algo falla
    # Este es el error estándar HTTP para "no autorizado"
    credenciales_invalidas = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail      = "Token inválido o expirado. Vuelve a hacer login.",
        headers     = {"WWW-Authenticate": "Bearer"},
    )

    try:
        # jwt.decode() verifica la firma y la fecha de expiración automáticamente
        # Si el token fue alterado o expiró, lanza JWTError
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificamos que el token tenga el campo "sub" (subject = numero_colegiatura)
        colegiatura: str = payload.get("sub")
        if colegiatura is None:
            raise credenciales_invalidas

        return payload

    except JWTError:
        # Cualquier error de JWT (firma inválida, expirado, mal formado)
        raise credenciales_invalidas


# ── DEPENDENCIA: Obtener el doctor actual desde el token ──────────────────────
#def get_doctor_actual(token: str = Depends(oauth2_scheme)) -> dict:
  #  """
#    Dependencia de FastAPI que extrae el doctor autenticado del token JWT.

#    Cómo usarla en un endpoint:
#        @router.get("/mi-endpoint")
#        def mi_endpoint(doctor = Depends(get_doctor_actual)):
            # doctor tiene: sub, doctor_id, nombre, especialidad
#            return {"mensaje": f"Hola Dr. {doctor['nombre']}"}

#    Si el token no es válido o no existe, FastAPI responde automáticamente
 #   con HTTP 401 antes de ejecutar el endpoint.
 #   """
    # verificar_token ya lanza HTTPException si algo falla
#    payload = verificar_token(token)
#    return payload