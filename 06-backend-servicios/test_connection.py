#!/usr/bin/env python3
"""
Script de diagnóstico para verificar conexión a Neon DB
Ejecutar: python test_connection.py
"""
import asyncio
import sys

async def main():
    print("=" * 60)
    print("DIAGNÓSTICO DE CONEXIÓN NEON + asyncpg")
    print("=" * 60)

    # Importar después de verificar que existe
    try:
        from database import test_connection, init_db, engine, DATABASE_URL
        from models import LeadScrap, Reservacion
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Asegúrate de tener instalado: pip install asyncpg sqlalchemy[asyncio]")
        sys.exit(1)

    # 1. Verificar URL
    print(f"\n1. URL de conexión:")
    if not DATABASE_URL or "TU_PASSWORD" in DATABASE_URL:
        print("   ❌ URL no configurada o tiene placeholder de password")
        print("   → Edita database.py y pon tu password real")
        sys.exit(1)
    else:
        safe_url = DATABASE_URL.replace(DATABASE_URL.split(":")[2].split("@")[0], "***")
        print(f"   ✅ {safe_url}")

    # 2. Test de conexión
    print(f"\n2. Test de conexión:")
    ok = await test_connection()
    if not ok:
        print("   ❌ No se pudo conectar. Revisa:")
        print("      - Password correcto")
        print("      - Endpoint pooler de Neon activo")
        print("      - IP permitida en Neon (Settings → IP Allow)")
        sys.exit(1)

    # 3. Crear tablas
    print(f"\n3. Creando tablas:")
    await init_db()

    # 4. Test insert
    print(f"\n4. Test de escritura:")
    from database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        # Insertar lead de prueba
        lead = LeadScrap(
            nombre_negocio="Test Conexión",
            telefono="+212600000000",
            caso="A",
            pack_asignado="Basico",
            estado="nuevo"
        )
        session.add(lead)
        await session.commit()
        print(f"   ✅ Lead insertado: ID={lead.id}")

        # Leer de vuelta
        result = await session.execute(select(LeadScrap).where(LeadScrap.id == lead.id))
        found = result.scalar_one()
        print(f"   ✅ Lead recuperado: {found.nombre_negocio}")

        # Contar total
        result = await session.execute(select(func.count()).select_from(LeadScrap))
        count = result.scalar()
        print(f"   ✅ Total leads en DB: {count}")

    print(f"\n" + "=" * 60)
    print("✅ TODO CORRECTO - La base de datos funciona")
    print("=" * 60)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
