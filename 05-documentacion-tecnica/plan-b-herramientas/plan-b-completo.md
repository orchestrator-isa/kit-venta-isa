# PLAN B — ALTERNATIVAS POR HERRAMIENTA
## Si falla algo, tenemos respaldo

| Herramienta | Alternativa 1 | Alternativa 2 | Costo migración | Datos preservables |
|-------------|---------------|---------------|-----------------|-------------------|
| **ManyChat** | Chatfuel | Botpress (self-hosted) | 2-3 días | Flujos (export JSON), suscriptores |
| **Make.com** | N8N (self-hosted) | Zapier | 1-2 días | Escenarios, conexiones API |
| **OpenAI GPT-4** | Claude API (Anthropic) | Mistral / local LLM | Variable | Prompts, contexto de negocio |
| **HubSpot** | Airtable + Notion | CRM propio (FastAPI) | 1 semana | Contactos, deals, historial |
| **Looker Studio** | Metabase (self-hosted) | Grafana | 2-3 días | Queries, dashboards |
| **Supabase** | PostgreSQL self-hosted | PlanetScale | 1 día | Tablas, RLS policies |
| **Vercel** | Netlify | Render | 1 hora | Código, variables de entorno |
| **Meta WhatsApp** | WhatsApp Business API directo | Twilio WhatsApp | 2-3 días | Templates, números |

## Migración de emergencia (ManyChat → Chatfuel)

### Paso 1: Exportar de ManyChat
1. ManyChat → Settings → Export
2. Descargar: subscribers.json, flows.json, tags.json

### Paso 2: Importar a Chatfuel
1. Crear cuenta en chatfuel.com
2. Conectar página Facebook
3. Importar flows manualmente (no hay import automático)
4. Recrear botones y respuestas

### Paso 3: Actualizar webhook
1. Meta Developer → Webhooks → Editar URL
2. Cambiar a webhook de Chatfuel
3. Verificar con token

### Paso 4: Notificar clientes
```
"Hemos mejorado nuestro sistema de chat. 
Tu experiencia será aún mejor. ¡Gracias por tu paciencia!"
```

## Migración de emergencia (Make.com → N8N)

### Paso 1: Instalar N8N
```bash
# Docker (más rápido)
docker run -it --rm   --name n8n   -p 5678:5678   -v ~/.n8n:/home/node/.n8n   n8nio/n8n
```

### Paso 2: Recrear flujos manualmente
- N8N no tiene import de Make.com
- Recrear nodo por nodo (típico: 4-8 horas)

### Paso 3: Ventajas de N8N
- Self-hosted = sin costo mensual
- Más nodos nativos que Make.com
- Código personalizable (JavaScript)
