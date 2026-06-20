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
