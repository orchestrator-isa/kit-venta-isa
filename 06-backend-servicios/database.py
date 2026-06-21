"""
Database configuration for ISA ChatCommerce
Neon PostgreSQL + asyncpg + SQLAlchemy 2.0
"""
import os
import re
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

# ============================================================
# CONFIGURACIÓN NEON - AUTO-CONVERSIÓN RENDER
# ============================================================
RAW_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # Fallback para desarrollo - REEMPLAZA con tu URL real
    "postgresql+asyncpg://neondb_owner:TU_PASSWORD@ep-solitary-sun-a2ssoxsd-pooler.eu-central-1.aws.neon.tech:5432/neondb"
)

def clean_database_url(url: str) -> str:
    """Convierte URL de Render/Neon a formato asyncpg válido."""
    if not url:
        raise ValueError("DATABASE_URL está vacía. Setea la variable de entorno o edita este archivo.")

    # Convertir prefijo
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Eliminar channel_binding (asyncpg no lo soporta)
    url = re.sub(r'[&?]channel_binding=[^&]+', '', url)

    # Eliminar sslmode de la URL (asyncpg no lo acepta como kwarg)
    # SSL se pasa via connect_args={"ssl": True}
    url = re.sub(r'[&?]sslmode=[^&]+', '', url)

    # Limpiar ? o & sueltos al final
    url = url.rstrip('?&')

    # Asegurar puerto 5432
    if ".neon.tech/" in url and ".neon.tech:" not in url:
        url = url.replace(".neon.tech/", ".neon.tech:5432/", 1)

    return url

DATABASE_URL = clean_database_url(RAW_DATABASE_URL)

# Log seguro
safe_url = re.sub(r'(://[^:]+:)([^@]+)(@)', r'\1***\3', DATABASE_URL)
print(f"[DB] URL: {safe_url}")

# Engine async optimizado para Neon
# SSL se pasa por connect_args, NO en la URL
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=3,
    max_overflow=2,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "ssl": True,       # ✅ SSL para Neon (reemplaza sslmode=require)
        "timeout": 10,
        "command_timeout": 30,
    }
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()

# Dependency para FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Crear tablas
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[DB] ✅ Tablas creadas/verificadas")

# Test de conexión
async def test_connection():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version(), now()"))
            row = result.fetchone()
            print(f"[DB] ✅ PostgreSQL: {row[0][:60]}...")
            print(f"[DB] ✅ Hora servidor: {row[1]}")
        return True
    except Exception as e:
        print(f"[DB] ❌ Error: {e}")
        return False
