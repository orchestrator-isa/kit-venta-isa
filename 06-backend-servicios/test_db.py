#!/usr/bin/env python3
"""
Test standalone de conexión a Neon DB.
Copia a la raíz de tu proyecto y ejecútalo.
"""
import os
import sys
import asyncio
import re

# ============================================================
# CONFIGURA AQUÍ TU URL DE RENDER
# ============================================================
RAW_URL = os.getenv(
    "DATABASE_URL",
    # PEGA AQUÍ TU URL REAL DE RENDER (la que empieza con postgresql://)
    "postgresql://neondb_owner:TU_PASSWORD@ep-solitary-sun-a2ssoxsd-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

def clean_url(url: str) -> str:
    if not url or "TU_PASSWORD" in url:
        return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Eliminar channel_binding
    url = re.sub(r'[&?]channel_binding=[^&]+', '', url)
    # Eliminar sslmode (asyncpg no lo acepta como kwarg)
    url = re.sub(r'[&?]sslmode=[^&]+', '', url)
    # Limpiar ? o & sueltos
    url = url.rstrip('?&')

    # Asegurar puerto 5432
    if ".neon.tech/" in url and ".neon.tech:" not in url:
        url = url.replace(".neon.tech/", ".neon.tech:5432/", 1)
    return url

async def test():
    print("=" * 60)
    print("DIAGNÓSTICO NEON + asyncpg")
    print("=" * 60)

    if not RAW_URL or "TU_PASSWORD" in RAW_URL:
        print("\n❌ ERROR: Edita test_db.py línea 14 y pon tu DATABASE_URL real")
        print("   O exporta: export DATABASE_URL='postgresql://...'")
        sys.exit(1)

    clean = clean_url(RAW_URL)
    safe = re.sub(r'(://[^:]+:)([^@]+)(@)', r'\1***\3', clean)
    print(f"\n1. URL limpia: {safe}")

    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        print("2. ✅ SQLAlchemy + asyncpg instalados")
    except ImportError:
        print("2. ❌ Falta: pip install sqlalchemy[asyncio] asyncpg")
        sys.exit(1)

    print("3. Conectando...")
    engine = create_async_engine(
        clean,
        echo=False,
        pool_pre_ping=True,
        connect_args={"ssl": True, "timeout": 10}  # ✅ SSL para Neon
    )

    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version(), now()"))
            row = result.fetchone()
            print(f"   ✅ Conectado!")
            print(f"   🗄️  {row[0][:60]}...")
            print(f"   🕐 Servidor: {row[1]}")

        print("\n4. Test de tabla:")
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_conexion (
                    id SERIAL PRIMARY KEY,
                    mensaje TEXT,
                    creado TIMESTAMP DEFAULT NOW()
                )
            """))
            await conn.execute(text("INSERT INTO test_conexion (mensaje) VALUES ('ISA ChatCommerce OK')"))
            result = await conn.execute(text("SELECT COUNT(*) FROM test_conexion"))
            count = result.scalar()
            print(f"   ✅ {count} fila(s) insertada(s)")
            await conn.execute(text("DROP TABLE test_conexion"))
            print(f"   ✅ Tabla de test eliminada")

        await engine.dispose()
        print("\n" + "=" * 60)
        print("✅ TODO CORRECTO - Tu DB funciona con asyncpg")
        print("=" * 60)

    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("\nPosibles causas:")
        print("   - Password incorrecto")
        print("   - Endpoint de Neon no activo")
        print("   - IP bloqueada en Neon (Settings → IP Allow → 0.0.0.0/0)")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test())
