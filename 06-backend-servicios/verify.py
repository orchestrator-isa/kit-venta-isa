#!/usr/bin/env python3
"""
Verificación de archivos ISA ChatCommerce
Ejecuta esto en tu carpeta 06-backend-servicios
"""
import os
import sys

print("=" * 60)
print("VERIFICACIÓN DE ARCHIVOS")
print("=" * 60)

files_to_check = {
    "database.py": ["init_db", "test_connection", "get_db", "engine", "clean_database_url"],
    "models.py": ["LeadScrap", "Reservacion"],
    "admin_router.py": ["admin_panel", "api_list_leads", "ADMIN_HTML"],
    "main.py": ["lifespan", "app", "FastAPI"],
    "requirements.txt": ["fastapi", "asyncpg", "sqlalchemy"],
}

all_ok = True
for filename, required in files_to_check.items():
    print(f"\n📄 {filename}:")
    if not os.path.exists(filename):
        print(f"   ❌ NO EXISTE")
        all_ok = False
        continue

    with open(filename, 'r') as f:
        content = f.read()

    size = len(content)
    print(f"   Tamaño: {size} bytes")

    missing = [r for r in required if r not in content]
    if missing:
        print(f"   ❌ Faltan: {', '.join(missing)}")
        all_ok = False
    else:
        print(f"   ✅ OK")

print("\n" + "=" * 60)
if all_ok:
    print("✅ TODOS LOS ARCHIVOS ESTÁN CORRECTOS")
    print("   Ejecuta: python -m uvicorn main:app --reload")
else:
    print("❌ FALTAN ARCHIVOS O ESTÁN INCOMPLETOS")
    print("   Descarga el ZIP y reemplaza TODO:")
    print("   rm -f database.py models.py admin_router.py main.py requirements.txt")
    print("   unzip ~/Downloads/isa_chatcommerce_fix.zip")
print("=" * 60)
