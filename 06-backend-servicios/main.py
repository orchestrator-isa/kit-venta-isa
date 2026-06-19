#!/usr/bin/env python3
# main.py — Orchestrator ISA ChatCommerce v3.0
# FastAPI + asyncpg + Neon DB + WhatsApp Cloud API

import os
import json
import asyncpg
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import httpx

# ===== CONFIGURACIÓN =====
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v20.0")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "isa_webhook_2026")
NEON_DB_URL = os.getenv("NEON_DB_URL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Cargar configuración de packs
with open("config/config.json") as f:
    CONFIG = json.load(f)

# ===== MODELOS Pydantic =====
class WebhookEntry(BaseModel):
    id: str
    changes: List[dict]

class WebhookPayload(BaseModel):
    object: str
    entry: List[WebhookEntry]

class MensajeEntrante(BaseModel):
    wa_id: str
    nombre: Optional[str] = None
    tipo: str
    texto: Optional[str] = None
    button_id: Optional[str] = None
    timestamp: int

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
    pool = await asyncpg.create_pool(NEON_DB_URL, min_size=2, max_size=10)
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    if pool:
        await pool.close()

app = FastAPI(title="ISA ChatCommerce API", version="3.0", lifespan=lifespan)

# ===== DEPENDENCIAS =====
async def get_db():
    async with pool.acquire() as conn:
        yield conn

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

        # Guardar en DB
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO conversaciones (wa_id, mensaje, intencion, metadata)
                VALUES ($1, $2, $3, $4)
            ''', phone, 
                message.get("text", {}).get("body") if msg_type == "text" else None,
                msg_type,
                json.dumps({"raw": message})
            )

        # Procesar mensaje
        if msg_type == "text":
            text = message.get("text", {}).get("body", "").lower()
            await procesar_mensaje_texto(phone, text)
        elif msg_type == "interactive":
            button_id = message.get("interactive", {}).get("button_reply", {}).get("id")
            await procesar_boton(phone, button_id)

    return {"status": "received"}

# ===== PROCESAMIENTO DE MENSAJES =====
async def procesar_mensaje_texto(phone: str, text: str):
    # Detección de idioma básica
    if any(w in text for w in ["salam", "labas", "bghit", "ch7al", "wa3er"]):
        idioma = "darija"
    elif any(w in text for w in ["bonjour", "combien", "je veux", "merci"]):
        idioma = "frances"
    else:
        idioma = "espanol"

    # Router de intenciones
    if any(w in text for w in ["menu", "menú", "carte", "lista"]):
        await enviar_menu(phone, idioma)
    elif any(w in text for w in ["pedido", "commande", "order", "bghit ncommandi"]):
        await iniciar_pedido(phone, idioma)
    elif any(w in text for w in ["reserva", "reserver", "rendez-vous", "hita"]):
        await iniciar_reserva(phone, idioma)
    elif any(w in text for w in ["humano", "operador", "personne", "insan"]):
        await derivar_humano(phone)
    else:
        # IA para respuesta
        await respuesta_ia(phone, text, idioma)

async def enviar_menu(phone: str, idioma: str):
    menus = {
        "espanol": "📋 MENÚ\n\n1. Tajine de pollo — 45 MAD\n2. Couscous royal — 55 MAD\n3. Pizza margherita — 40 MAD\n4. Ensalada mixta — 25 MAD\n\nResponde con el número para pedir.",
        "frances": "📋 CARTE\n\n1. Tajine poulet — 45 MAD\n2. Couscous royal — 55 MAD\n3. Pizza margherita — 40 MAD\n4. Salade mixte — 25 MAD\n\nRéponds avec le numéro pour commander.",
        "darija": "📋 L-MENYU\n\n1. Tajine dyal djedj — 45 MAD\n2. Couscous — 55 MAD\n3. Pizza — 40 MAD\n4. Salada — 25 MAD\n\nJaweb b'r9am."
    }
    await enviar_whatsapp(phone, menus.get(idioma, menus["espanol"]))

async def iniciar_pedido(phone: str, idioma: str):
    textos = {
        "espanol": "🛒 Perfecto. ¿Qué deseas pedir? Responde con el número del menú o escribe tu pedido.",
        "frances": "🛒 Parfait. Que souhaites-tu commander? Réponds avec le numéro du menu.",
        "darija": "🛒 Mezyan. Ash bghiti tcommandi? Jaweb b'r9am."
    }
    await enviar_whatsapp(phone, textos.get(idioma, textos["espanol"]))

async def iniciar_reserva(phone: str, idioma: str):
    textos = {
        "espanol": "📅 Para reservar, dime:\n1. ¿Cuántas personas?\n2. ¿Qué día y hora?\n3. ¿Zona preferida (interior/terraza)?",
        "frances": "📅 Pour réserver, dis-moi:\n1. Combien de personnes?\n2. Quel jour et heure?\n3. Zone préférée?",
        "darija": "📅 Besh nhajzou, 3tini:\n1. Ch7al mn nes?\n2. Ash nu nhar w sa3a?\n3. Blasa?"
    }
    await enviar_whatsapp(phone, textos.get(idioma, textos["espanol"]))

async def derivar_humano(phone: str):
    await enviar_whatsapp(phone, "👤 Te conecto con un humano. Un momento por favor...")
    # TODO: Notificar a HubSpot / dashboard del dueño

async def respuesta_ia(phone: str, text: str, idioma: str):
    if not OPENAI_API_KEY:
        await enviar_whatsapp(phone, "🤔 No entendí bien. ¿Puedes reformular? O escribe MENU para ver opciones.")
        return

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": f"Eres un asistente de restaurante en Tetuán, Marruecos. Responde en {idioma}. Sé amable, conciso (máx 2 frases)."},
                        {"role": "user", "content": text}
                    ],
                    "max_tokens": 150,
                    "temperature": 0.7
                },
                timeout=10.0
            )
            data = response.json()
            respuesta = data["choices"][0]["message"]["content"]
            await enviar_whatsapp(phone, respuesta)
        except Exception as e:
            print(f"Error IA: {e}")
            await enviar_whatsapp(phone, "🤔 Perdona, no entendí. Escribe MENU para ver opciones.")

async def procesar_boton(phone: str, button_id: str):
    if button_id == "btn_menu":
        await enviar_menu(phone, "espanol")
    elif button_id == "btn_pedido":
        await iniciar_pedido(phone, "espanol")
    elif button_id == "btn_reserva":
        await iniciar_reserva(phone, "espanol")

# ===== API WHATSAPP =====
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
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )
            return response.json()
        except Exception as e:
            print(f"Error enviando WhatsApp: {e}")

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
    row = await conn.fetchrow('''
        SELECT * FROM metricas_diarias 
        WHERE cliente_id = $1 AND fecha = CURRENT_DATE
    ''', cliente_id)
    return dict(row) if row else {}

# ===== API LEADS (Landing page) =====
@app.post("/api/leads")
async def crear_lead(request: Request):
    data = await request.json()
    # TODO: Guardar en HubSpot o tabla leads
    print(f"Nuevo lead: {data}")
    return {"status": "recibido"}

# ===== HEALTH CHECK =====
@app.get("/health")
async def health():
    return {"status": "ok", "version": "3.0", "timestamp": datetime.now().isoformat()}

# ===== INICIAR =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
