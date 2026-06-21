#!/usr/bin/env python3
"""
ISA ChatCommerce - Orquestrator v13.1
FastAPI + asyncpg + Neon + Landing Page + Panel Admin
Todo en uno: landing estática + API + admin + webhook
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func

from database import init_db, test_connection, get_db, engine
from models import LeadScrap, Reservacion
from admin_router import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] ISA ChatCommerce v13.1...")
    ok = await test_connection()
    if ok:
        await init_db()
        print("[STARTUP] ✅ DB lista")
    else:
        print("[STARTUP] ⚠️ DB no disponible")
    yield
    print("[SHUTDOWN] Cerrando...")
    await engine.dispose()

app = FastAPI(title="ISA ChatCommerce", version="13.1", lifespan=lifespan)

# CORS para que el formulario de la landing haga fetch a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# LANDING PAGE (archivos estáticos)
# ============================================
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def landing_page():
    """Sirve la landing page en la raíz"""
    return FileResponse("static/index.html")

# ============================================
# API PARA LANDING PAGE (guarda leads en Neon)
# ============================================
@app.post("/api/landing-lead")
async def create_landing_lead(data: dict, db: AsyncSession = Depends(get_db)):
    """
    Recibe leads desde el formulario de la landing page
    y los guarda en la base de datos Neon.
    """
    # Verificar si ya existe el teléfono
    result = await db.execute(
        select(LeadScrap).where(LeadScrap.telefono == data.get("telefono", ""))
    )
    existing = result.scalar_one_or_none()

    if existing:
        return {"status": "exists", "id": existing.id, "message": "Lead ya registrado"}

    # Crear nuevo lead desde la landing
    lead = LeadScrap(
        nombre_negocio=data.get("negocio", "Sin nombre"),
        telefono=data.get("telefono", ""),
        ciudad=data.get("ciudad", "Tetuán"),
        caso=data.get("caso", "G"),
        pack_asignado=data.get("pack_interesado", "Basico"),
        estado="nuevo",
        fuente="landing_page",
        mensaje_personalizado=data.get("mensaje", None),
        notas=f"Tipo: {data.get('tipo_negocio', 'No especificado')}. Interesado en: {data.get('pack_interesado', 'No especificado')}"
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    print(f"[LANDING] Nuevo lead: {lead.nombre_negocio} ({lead.telefono})")

    return {
        "status": "created",
        "id": lead.id,
        "message": "Lead registrado",
        "whatsapp_link": f"https://wa.me/212786120081?text=Hola%2C%20soy%20{data.get('nombre', '')}%20de%20{data.get('negocio', '')}"
    }

@app.get("/api/landing-stats")
async def landing_stats(db: AsyncSession = Depends(get_db)):
    """Stats públicos para la landing page"""
    total = await db.execute(select(func.count()).select_from(LeadScrap))
    return {
        "total_leads": total.scalar(),
        "negocios_activos": 50,
        "satisfaccion": "4.9/5"
    }

# ============================================
# ADMIN ROUTER
# ============================================
app.include_router(admin_router)

# ============================================
# HEALTH
# ============================================
@app.get("/health")
async def health():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected", "version": "13.1"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "error", "database": str(e)})

# ============================================
# WEBHOOK WHATSAPP
# ============================================
@app.get("/webhook")
async def webhook_verify(request: Request):
    params = dict(request.query_params)
    VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "isa_dev_token")
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params.get("hub.challenge", 0))
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def webhook_receive(request: Request):
    body = await request.json()
    print(f"[WEBHOOK] Recibido: {body}")
    return {"status": "received"}

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
