#!/usr/bin/env python3
"""
Diagnóstico de Render + Neon
Ejecutar local o como endpoint temporal
"""
import os
import sys

print("=" * 60)
print("DIAGNÓSTICO RENDER + NEON")
print("=" * 60)

# 1. Verificar variables de entorno
print("
1. VARIABLES DE ENTORNO:")
db_url = os.getenv("DATABASE_URL", "NO SETEADA")
if db_url == "NO SETEADA":
    print("   ❌ DATABASE_URL: NO SETEADA")
    print("   → Ve a Render Dashboard → Environment → Agrega DATABASE_URL")
else:
    safe = db_url.replace(db_url.split(":")[2].split("@")[0], "***")
    print(f"   ✅ DATABASE_URL: {safe}")

verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "NO SETEADA")
print(f"   WHATSAPP_VERIFY_TOKEN: {verify_token}")

# 2. Verificar archivos
print("
2. ARCHIVOS DEL PROYECTO:")
files = ["main.py", "database.py", "models.py", "admin_router.py", "static/index.html"]
for f in files:
    exists = "✅" if os.path.exists(f) else "❌"
    print(f"   {exists} {f}")

# 3. Test de conexión
print("
3. TEST DE CONEXIÓN:")
try:
    from database import test_connection
    import asyncio
    result = asyncio.run(test_connection())
    if result:
        print("   ✅ Conexión OK")
    else:
        print("   ❌ Conexión falló")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("
" + "=" * 60)
