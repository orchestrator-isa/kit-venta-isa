#!/usr/bin/env python3
# main.py — Orchestrator ISA ChatCommerce v3.1
# FastAPI + asyncpg + Neon DB + WhatsApp Cloud API

import os
import json
import asyncpg
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import httpx

# ===== CONFIGURACIÓN =====
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v20.0")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "isa_verify_2026")
NEON_DB_URL = os.getenv("NEON_DB_URL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "config.json")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH) as f:
        CONFIG = json.load(f)
else:
    CONFIG = {}

# ===== MODELOS =====
class ClienteCreate(BaseModel):
    nombre_negocio: str
    nombre_dueno: str
    cin: str
    telefono: str
    email: Optional[str] = None
    rib: str
    direccion: str
    facturacion_mensual: float
    pack_id: str
    tipo_negocio: str = "restaurante"

# ===== BASE DE DATOS =====
pool: Optional[asyncpg.Pool] = None

async def init_db():
    global pool
    if not NEON_DB_URL:
        print("⚠️ NEON_DB_URL no configurada. DB deshabilitada.")
        return
    try:
        for intento in range(5):
            try:
                pool = await asyncpg.create_pool(NEON_DB_URL, min_size=1, max_size=5, command_timeout=10)
                break
            except Exception as e:
                print(f"⚠️ Intento {intento+1}/5 falló: {e}")
                if intento < 4:
                    await asyncio.sleep(2)
                else:
                    raise

        async with pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id SERIAL PRIMARY KEY,
                    nombre_negocio VARCHAR(200) NOT NULL,
                    nombre_dueno VARCHAR(200) NOT NULL,
                    cin VARCHAR(20) UNIQUE NOT NULL,
                    telefono VARCHAR(20) UNIQUE NOT NULL,
                    email VARCHAR(200),
                    rib VARCHAR(50) NOT NULL,
                    direccion TEXT,
                    facturacion_mensual DECIMAL(12,2),
                    pack_id VARCHAR(50) NOT NULL,
                    tipo_negocio VARCHAR(50) DEFAULT 'restaurante',
                    estado VARCHAR(20) DEFAULT 'ACTIVO',
                    nivel VARCHAR(20) DEFAULT 'BRONCE',
                    fecha_alta TIMESTAMP DEFAULT NOW(),
                    ultimo_contacto TIMESTAMP DEFAULT NOW(),
                    ultimo_pago TIMESTAMP,
                    referidos_hechos INTEGER DEFAULT 0,
                    referidos_recibidos INTEGER DEFAULT 0
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS conversaciones (
                    id SERIAL PRIMARY KEY,
                    cliente_id INTEGER REFERENCES clientes(id),
                    wa_id VARCHAR(50) NOT NULL,
                    mensaje TEXT,
                    intencion VARCHAR(50),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS metricas_diarias (
                    id SERIAL PRIMARY KEY,
                    cliente_id INTEGER REFERENCES clientes(id),
                    fecha DATE DEFAULT CURRENT_DATE,
                    conversaciones INTEGER DEFAULT 0,
                    pedidos INTEGER DEFAULT 0,
                    valor_ventas DECIMAL(12,2) DEFAULT 0,
                    resenas_nuevas INTEGER DEFAULT 0,
                    posicion_maps INTEGER,
                    UNIQUE(cliente_id, fecha)
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS reservaciones (
                    id SERIAL PRIMARY KEY,
                    cliente_id INTEGER REFERENCES clientes(id),
                    codigo_reserva VARCHAR(20) UNIQUE NOT NULL,
                    hora_reserva TIMESTAMP NOT NULL,
                    mesa_asignada VARCHAR(20),
                    zona VARCHAR(50),
                    ai_confirmada BOOLEAN DEFAULT FALSE,
                    estado VARCHAR(20) DEFAULT 'PENDIENTE',
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS leads_scrap (
                    id SERIAL PRIMARY KEY,
                    telefono VARCHAR(20),
                    nombre VARCHAR(100),
                    nombre_negocio VARCHAR(100),
                    tipo_negocio VARCHAR(50),
                    segmento VARCHAR(20),
                    pack_asignado VARCHAR(50),
                    caso VARCHAR(5),
                    fuente VARCHAR(50) DEFAULT 'calculadora',
                    estado_contacto VARCHAR(20) DEFAULT 'no_contactado',
                    cin VARCHAR(20),
                    rib VARCHAR(50),
                    direccion TEXT,
                    notas TEXT,
                    fecha_scrap TIMESTAMP DEFAULT NOW(),
                    fecha_contacto TIMESTAMP
                )
            ''')
        print("✅ Base de datos conectada")
    except Exception as e:
        print(f"⚠️ Error conectando a DB: {e}")
        pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    if pool:
        await pool.close()

app = FastAPI(title="ISA ChatCommerce API", version="3.1", lifespan=lifespan)

# Static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/admin", StaticFiles(directory=os.path.join(static_path, "admin"), html=True), name="admin")

async def get_db():
    if not pool:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")
    async with pool.acquire() as conn:
        yield conn

# ===== CALCULADORA DE SEGMENTACIÓN =====
@app.get("/calculadora", response_class=HTMLResponse)
async def calculadora():
    calculadora_path = os.path.join(os.path.dirname(__file__), "static", "calculadora-segmentacion.html")
    if os.path.exists(calculadora_path):
        with open(calculadora_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    raise HTTPException(status_code=404, detail="Calculadora no encontrada")

# ===== ENDPOINT RAÍZ =====
@app.get("/", response_class=JSONResponse)
async def root():
    return {
        "status": "online",
        "service": "ISA ChatCommerce",
        "version": "3.1",
        "region": "Marruecos",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook",
            "clientes": "/api/clientes",
            "leads": "/api/leads",
            "admin": "/admin",
            "calculadora": "/calculadora"
        }
    }

# ===== WHATSAPP WEBHOOK =====
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    entry = body.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})
    if "messages" in value:
        message = value["messages"][0]
        phone = message.get("from")
        msg_type = message.get("type")
        if pool:
            async with pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO conversaciones (wa_id, mensaje, intencion, metadata)
                    VALUES ($1, $2, $3, $4)
                ''', phone,
                    message.get("text", {}).get("body") if msg_type == "text" else None,
                    msg_type,
                    json.dumps({"raw": message})
                )
        if msg_type == "text":
            text = message.get("text", {}).get("body", "").lower()
            await procesar_mensaje_texto(phone, text)
    return {"status": "received"}

# ===== PROCESAMIENTO =====
async def procesar_mensaje_texto(phone: str, text: str):
    if any(w in text for w in ["salam", "labas", "bghit", "ch7al", "wa3er"]):
        idioma = "darija"
    elif any(w in text for w in ["bonjour", "combien", "je veux", "merci"]):
        idioma = "frances"
    else:
        idioma = "espanol"

    if any(w in text for w in ["menu", "menú", "carte", "lista"]):
        await enviar_whatsapp(phone, "📋 MENÚ\n\n1. Tajine de pollo — 45 MAD\n2. Couscous royal — 55 MAD\n3. Pizza margherita — 40 MAD\n4. Ensalada mixta — 25 MAD\n\nResponde con el número para pedir.")
    elif any(w in text for w in ["pedido", "commande", "order"]):
        await enviar_whatsapp(phone, "🛒 Perfecto. ¿Qué deseas pedir?")
    elif any(w in text for w in ["reserva", "reserver", "rendez-vous"]):
        await enviar_whatsapp(phone, "📅 Para reservar, dime: ¿cuántas personas, qué día y hora?")
    elif any(w in text for w in ["humano", "operador", "personne"]):
        await enviar_whatsapp(phone, "👤 Te conecto con un humano. Un momento...")
    else:
        await enviar_whatsapp(phone, "🤔 No entendí. Escribe MENU para ver opciones.")

async def enviar_whatsapp(to: str, message: str):
    if not PHONE_NUMBER_ID or not ACCESS_TOKEN:
        print(f"[MOCK] WhatsApp a {to}: {message[:50]}...")
        return
    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }, timeout=10.0)
            return response.json()
        except Exception as e:
            print(f"Error enviando WhatsApp: {e}")

# ===== API LEADS =====
@app.post("/api/leads")
async def crear_lead(request: Request):
    data = await request.json()
    print(f"Nuevo lead: {data}")
    if pool:
        try:
            async with pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO leads_scrap 
                    (telefono, nombre, nombre_negocio, tipo_negocio, segmento, 
                     pack_asignado, caso, fuente, estado_contacto, cin, rib, 
                     direccion, notas)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                ''', 
                    data.get("telefono"),
                    data.get("nombre_dueno"),
                    data.get("nombre_negocio"),
                    data.get("tipo_negocio"),
                    data.get("segmento"),
                    data.get("pack_asignado"),
                    data.get("caso"),
                    data.get("fuente", "calculadora"),
                    data.get("estado_contacto", "no_contactado"),
                    data.get("cin"),
                    data.get("rib"),
                    data.get("direccion"),
                    data.get("notas")
                )
                return {"status": "guardado_en_db"}
        except Exception as e:
            print(f"Error guardando en DB: {e}")
            return {"status": "recibido", "error": str(e), "nota": "Guardar manualmente"}
    return {"status": "recibido", "nota": "DB no disponible, guardar manualmente"}

@app.get("/api/leads")
async def listar_leads():
    if not pool:
        return {"error": "Base de datos no disponible", "leads": []}
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM leads_scrap ORDER BY fecha_scrap DESC")
            return [dict(r) for r in rows]
    except Exception as e:
        return {"error": str(e), "leads": []}

# ===== API CLIENTES =====
@app.post("/api/clientes")
async def crear_cliente(cliente: ClienteCreate, conn=Depends(get_db)):
    row = await conn.fetchrow('''
        INSERT INTO clientes (nombre_negocio, nombre_dueno, cin, telefono, email, rib, direccion, facturacion_mensual, pack_id, tipo_negocio)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING id
    ''', cliente.nombre_negocio, cliente.nombre_dueno, cliente.cin, cliente.telefono,
        cliente.email, cliente.rib, cliente.direccion, cliente.facturacion_mensual,
        cliente.pack_id, cliente.tipo_negocio)
    return {"id": row["id"], "status": "creado"}

@app.get("/api/clientes")
async def listar_clientes(conn=Depends(get_db)):
    rows = await conn.fetch('SELECT * FROM clientes WHERE estado = $1 ORDER BY fecha_alta DESC', 'ACTIVO')
    return [dict(r) for r in rows]

@app.get("/api/clientes/{cliente_id}/metricas")
async def metricas_cliente(cliente_id: int, conn=Depends(get_db)):
    row = await conn.fetchrow('SELECT * FROM metricas_diarias WHERE cliente_id = $1 AND fecha = CURRENT_DATE', cliente_id)
    return dict(row) if row else {}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "3.1", "db_connected": pool is not None, "timestamp": datetime.now().isoformat()}

@app.get("/api/debug/db")
async def debug_db():
    """Endpoint de diagnóstico para ver estado de la base de datos"""
    if not pool:
        return {
            "db_connected": False,
            "error": "Pool no inicializado. NEON_DB_URL puede estar vacía o la DB no respondió.",
            "neon_db_url_set": bool(NEON_DB_URL),
            "tip": "Espera 30 segundos y recarga. Neon free tier se duerme."
        }
    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT COUNT(*) FROM leads_scrap")
            return {
                "db_connected": True,
                "leads_count": result,
                "pool_status": "active"
            }
    except Exception as e:
        return {
            "db_connected": False,
            "error": str(e),
            "tip": "La tabla leads_scrap puede no existir todavía. Espera el primer deploy."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
