#!/usr/bin/env python3
"""
ISA ChatCommerce - Orquestrator v13.2
FastAPI + asyncpg + Neon + 2 Landing Pages + Admin + Seguridad
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException,Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
import time
from collections import defaultdict
from fastapi.templating import Jinja2Templates
from database import init_db, test_connection, get_db, engine
from models import LeadScrap, Reservacion
from admin_router import router as admin_router

# Rate limiting
request_counts = defaultdict(list)
templates = Jinja2Templates(directory="templates")

async def rate_limit(request: Request, max_requests: int = 30, window: int = 60):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    request_counts[client_ip] = [t for t in request_counts[client_ip] if now - t < window]
    if len(request_counts[client_ip]) >= max_requests:
        raise HTTPException(status_code=429, detail="Too many requests")
    request_counts[client_ip].append(now)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] ISA ChatCommerce v13.2...")
    ok = await test_connection()
    if ok:
        await init_db()
        print("[STARTUP] ✅ DB lista")
    else:
        print("[STARTUP] ⚠️ DB no disponible")
    yield
    print("[SHUTDOWN] Cerrando...")
    await engine.dispose()

app = FastAPI(title="ISA ChatCommerce", version="13.2", lifespan=lifespan, docs_url=None, redoc_url=None)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Landing 1: Principal
@app.get("/", response_class=FileResponse)
async def landing_principal():
    return FileResponse("static/index.html")

# Landing 2: MEDVi v2.0
@app.get("/medvi", response_class=FileResponse)
async def landing_medvi():
    return FileResponse("static/medvi/index.html")

@app.get("/medvi/", response_class=FileResponse)
async def landing_medvi_slash():
    return FileResponse("static/medvi/index.html")

# API para ambas landings
@app.post("/api/landing-lead")
async def create_landing_lead(
    request: Request,
    nombre: str = Form(""),
    telefono: str = Form(""),
    negocio: str = Form(""),
    ciudad: str = Form("Tetuán"),
    caso: str = Form("G"),
    pack_interesado: str = Form("Basico"),
    pack_recomendado: str = Form(""),
    score_segmentacion: int = Form(0),
    tipo_negocio: str = Form(""),
    fuente: str = Form("landing_principal"),
    mensaje: str = Form(""),
    whatsapp: str = Form(""),
    maps: str = Form(""),
    facturacion: str = Form(""),
    clientes_dia: str = Form(""),
    redes: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    """
    Guarda un lead desde formularios HTML (application/x-www-form-urlencoded).
    ANTES estaba como 'data: dict' (JSON) → causaba 405/422 en formularios HTML.
    """
    # Rate limiting (si tienes la función)
    # await rate_limit(request, max_requests=10, window=60)
    
    # Verificar si ya existe
    result = await db.execute(
        select(LeadScrap).where(LeadScrap.telefono == telefono)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return {"status": "exists", "id": existing.id}

    # Crear lead
    lead = LeadScrap(
        nombre_negocio=negocio or "Sin nombre",
        nombre_contacto=nombre or None,  # ← NUEVO
        telefono=telefono,
        ciudad=ciudad,
        caso=caso,
        pack_asignado=pack_interesado or pack_recomendado or "Basico",
        estado="nuevo",
        fuente=fuente,
        mensaje_personalizado=mensaje,
        score_segmentacion=score_segmentacion,  # ← NUEVO
        notas=(
            f"Tipo: {tipo_negocio or 'No especificado'}. "
            f"Landing: {fuente}. "
            f"WhatsApp: {whatsapp}. Maps: {maps}. "
            f"Facturación: {facturacion}. Clientes/día: {clientes_dia}. "
            f"Redes: {redes}. Score: {score_segmentacion}"
        )
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    
    # Generar link WhatsApp
    nombre_url = (nombre or "").replace(" ", "%20")
    negocio_url = (negocio or "").replace(" ", "%20")
    whatsapp_text = f"Hola, soy {nombre_url} de {negocio_url}"
    
    return {
        "status": "created",
        "id": lead.id,
        "whatsapp_link": f"https://wa.me/212786120081?text={whatsapp_text}"
    }

@app.get("/api/landing-stats")
async def landing_stats(db: AsyncSession = Depends(get_db)):
    total = await db.execute(select(func.count()).select_from(LeadScrap))
    return {"total_leads": total.scalar(), "negocios_activos": 50, "satisfaccion": "4.9/5"}

@app.get("/calculadora")
async def calculadora_page():
    """Sirve calculadora.html desde templates o static"""
    for path in ["templates/calculadora.html", "static/calculadora.html"]:
        if os.path.exists(path):
            return FileResponse(path)
    raise HTTPException(status_code=404, detail="calculadora.html not found. Asegurate de subirlo a templates/ o static/")

# Diagnóstico
@app.get("/diagnostic")
async def diagnostic():
    db_url = os.getenv("DATABASE_URL", "NO SETEADA")
    safe_url = "NO SETEADA" if db_url == "NO SETEADA" else "***@" + db_url.split("@")[1]
    return {"database_url_set": db_url != "NO SETEADA", "database_url_preview": safe_url, "whatsapp_verify_token_set": os.getenv("WHATSAPP_VERIFY_TOKEN") is not None, "static_folder_exists": os.path.exists("static/index.html"), "medvi_folder_exists": os.path.exists("static/medvi/index.html"), "version": "13.2"}

# Admin
app.include_router(admin_router)

# Health
@app.get("/health")
async def health():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected", "version": "13.2"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "error", "database": str(e), "hint": "Check DATABASE_URL in Render Environment"})

# Webhook
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
