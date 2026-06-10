# ============================================================
# database.py
# Ubicación: EcoSistemaSalud/database.py
# Conexión compartida a PostgreSQL para TODOS los servicios
# ServicioDoctores, ServicioPacientes, ServicioClinicas
# todos importan desde aquí
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

# ── Credenciales de PostgreSQL ────────────────────────────────────────────────
DB_USER     = "postgres.jwoebzpkhufnpbjvvlym"
DB_PASSWORD = "t67jVRVwqcDBNlJ5"       # Tu contraseña de PostgreSQL
DB_HOST     = "aws-1-us-west-1.pooler.supabase.com"
DB_PORT     = "5432"
DB_NAME     = "postgres"

# quote_plus convierte caracteres especiales como ! en formato seguro para URL
# Ejemplo: "Aa12345!" → "Aa12345%21"
password_segura = quote_plus(DB_PASSWORD)

# Cadena de conexión a PostgreSQL
DATABASE_URL = f"postgresql://{DB_USER}:{password_segura}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

# create_engine: motor que gestiona la conexión real a PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=False       # True = muestra SQL en consola (útil para debug)
)

# SessionLocal: abre y cierra sesiones de trabajo con la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: clase padre de todos los modelos ORM (tablas)
Base = declarative_base()