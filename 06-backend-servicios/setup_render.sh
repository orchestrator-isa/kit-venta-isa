#!/bin/bash
# ============================================================
# SCRIPT: Migrar estructura para Render
# Ejecutar en la RAÍZ de tu repositorio local
# ============================================================

echo "🚀 Preparando repo para Render..."
echo ""

# 1. Verificar que estamos en la raíz del repo
if [ ! -d ".git" ]; then
    echo "❌ Error: No estás en la raíz del repositorio Git"
    echo "   Ve a la carpeta raíz donde está .git/"
    exit 1
fi

# 2. Verificar que existe la carpeta app/
if [ ! -d "app" ]; then
    echo "❌ Error: No existe la carpeta app/"
    echo "   Tu código debe estar en app/"
    exit 1
fi

echo "✅ Repo verificado"
echo ""

# 3. Crear requirements.txt en raíz
echo "📄 Creando requirements.txt en raíz..."
cat > requirements.txt << 'EOF'
fastapi==0.111.0
uvicorn[standard]==0.30.0
asyncpg==0.29.0
sqlalchemy[asyncio]==2.0.30
python-dotenv==1.0.1
pydantic==2.7.4
pydantic-settings==2.3.4
python-multipart==0.0.9
httpx==0.27.0
aiofiles==23.2.1
jinja2==3.1.4
EOF
echo "   ✅ requirements.txt creado"

# 4. Crear main.py en raíz (wrapper)
echo "📄 Creando main.py wrapper en raíz..."
cat > main.py << 'EOF'
# Entry point para Render
# Importa la app desde el paquete app/

import sys
import os

# Asegurar que app/ está en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app  # Tu main.py original dentro de app/

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF
echo "   ✅ main.py creado"

# 5. Crear render.yaml
echo "📄 Creando render.yaml..."
cat > render.yaml << 'EOF'
services:
  - type: web
    name: isa-chatcommerce
    runtime: python
    region: frankfurt
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: isa-db
          property: connectionString
      - key: WHATSAPP_TOKEN
        sync: false
      - key: WHATSAPP_PHONE_ID
        sync: false
      - key: META_VERIFY_TOKEN
        sync: false
      - key: NEON_DB_URL
        sync: false

databases:
  - name: isa-db
    region: frankfurt
    plan: free
    ipAllowList: []
EOF
echo "   ✅ render.yaml creado"

echo ""
echo "📤 Subiendo cambios a Git..."
git add requirements.txt main.py render.yaml
git commit -m "deploy: add Render config files at repo root"
git push origin main

echo ""
echo "🎉 ¡Listo! Ahora en Render:"
echo "   • Root Directory: (vacío)"
echo "   • Build Command: pip install -r requirements.txt"
echo "   • Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo ""
echo "   Ve a Render Dashboard → Manual Deploy → Deploy Latest Commit"
