# 🚨 CRISIS: El bot no responde

## Síntomas
- Cliente reporta: "El bot no contesta"
- Dashboard muestra 0 conversaciones en última hora
- ManyChat status page muestra incidente

## Protocolo (5 minutos)

### Paso 1: Verificar (1 min)
```bash
# Enviar mensaje de prueba al bot
curl -X POST https://graph.facebook.com/v20.0/{PHONE_ID}/messages   -H "Authorization: Bearer {TOKEN}"   -d '{"messaging_product":"whatsapp","to":"{TEST_NUMBER}","type":"text","text":{"body":"TEST"}}'
```

### Paso 2: Activar mensaje de ausencia (1 min)
En WhatsApp Business App del cliente:
1. Abrir Configuración → Herramientas para la empresa
2. Activar "Mensaje fuera del horario de atención"
3. Texto: "⚠️ Estamos teniendo problemas técnicos. Llama al {TELÉFONO_DUEÑO} para atención inmediata."

### Paso 3: Notificar al cliente (1 min)
```
"[Nombre del dueño], estamos solucionando un problema técnico con el bot. 
Tus clientes pueden llamarte directamente mientras tanto. 
Disculpa las molestias. Esto se arregla en 1-4 horas máximo."
```

### Paso 4: Verificar ManyChat status (1 min)
- https://status.manychat.com
- Si es caída general: Esperar (típico 1-4h)
- Si es solo tu cuenta: Revisar configuración webhook

### Paso 5: Compensación (1 min)
- Ofrecer 1 día gratis de mantenimiento
- Registrar en CRM como "incidente técnico"

## Checklist post-crisis
- [ ] Bot vuelve a responder
- [ ] Mensaje de ausencia desactivado
- [ ] Cliente notificado de resolución
- [ ] Compensación aplicada
- [ ] Lección aprendida documentada
