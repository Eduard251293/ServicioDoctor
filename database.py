# ============================================================
# database.py
# Ubicación: ServicioDoctor/database.py
# Conexión compartida a PostgreSQL (Supabase) para todos los endpoints
# Ahora lee las credenciales desde el archivo .env
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

# ── Cargar el archivo .env ────────────────────────────────────────────────────
# load_dotenv() busca el archivo .env en la carpeta actual y carga las variables
# Esto permite que os.getenv() las encuentre sin exponerlas en el código
load_dotenv()

# ── Credenciales de PostgreSQL ────────────────────────────────────────────────
# Ahora vienen del .env, no del código fuente
# Si no están en .env, usa los valores por defecto (para no romper nada aún)
DB_USER     = os.getenv("DB_USER",     "postgres.jwoebzpkhufnpbjvvlym")
DB_PASSWORD = os.getenv("DB_PASSWORD", "t67jVRVwqcDBNlJ5")
DB_HOST     = os.getenv("DB_HOST",     "aws-1-us-west-1.pooler.supabase.com")
DB_PORT     = os.getenv("DB_PORT",     "5432")
DB_NAME     = os.getenv("DB_NAME",     "postgres")

# quote_plus convierte caracteres especiales en la contraseña a formato URL seguro
# Ejemplo: "Aa12345!" → "Aa12345%21"
password_segura = quote_plus(DB_PASSWORD)

# ── Cadena de conexión a PostgreSQL ───────────────────────────────────────────
DATABASE_URL = f"postgresql://{DB_USER}:{password_segura}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

# ── Motor de conexión ─────────────────────────────────────────────────────────
# echo=False → no muestra SQL en consola (cámbialo a True si quieres ver las queries)
engine = create_engine(DATABASE_URL, echo=False)

# ── Fábrica de sesiones ───────────────────────────────────────────────────────
# Cada endpoint abre una sesión al empezar y la cierra al terminar
# autocommit=False → los cambios no se guardan hasta hacer db.commit()
# autoflush=False  → SQLAlchemy no envía cambios automáticamente a la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Clase base para los modelos ORM ──────────────────────────────────────────
# Todos los modelos (Doctor, Diagnostico, etc.) heredan de esta clase
Base = declarative_base()