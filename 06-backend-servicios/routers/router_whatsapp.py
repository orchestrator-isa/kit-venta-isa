from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import PlainTextResponse
import os
import json
import httpx
from typing import Dict, Any

router = APIRouter(prefix="/webhook", tags=["whatsapp"])

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")

@router.get("")
async def verify_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Verificación del webhook por Meta"""
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("")
async def receive_message(request: Request):
    """Recibe mensajes de WhatsApp"""
    try:
        body = await request.json()

        if body.get("object") != "whatsapp_business_account":
            return {"status": "ignored"}

        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})

        if "messages" not in value:
            return {"status": "no_messages"}

        message = value["messages"][0]
        from_number = message.get("from")
        msg_type = message.get("type")

        if msg_type == "text":
            text = message.get("text", {}).get("body", "")
            # Aquí procesarías con chatbot_service
            return {
                "status": "received",
                "from": from_number,
                "message": text
            }

        return {"status": "received", "type": msg_type}

    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.post("/send")
async def send_message(telefono: str, mensaje: str):
    """Envía mensaje por WhatsApp Cloud API"""
    if not WHATSAPP_TOKEN or not PHONE_ID:
        raise HTTPException(status_code=500, detail="WhatsApp no configurado")

    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": telefono,
        "type": "text",
        "text": {"body": mensaje}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        return response.json()
