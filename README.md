# 🚀 KIT-VENTA-ISA v3.0
## Orchestrator ISA ChatCommerce — Kit completo para consultores

**Versión:** 3.0 | **Fecha:** 2026-06-20 | **Ciudad:** Tetuán, Marruecos

---

## 📁 ESTRUCTURA DEL KIT

```
kit-venta-isa-v3/
│
├── 📂 01-capa-decision/              # Calculadora de segmentación (PWA)
│   ├── calculadora-segmentacion.html
│   ├── calculadora-segmentacion.js
│   ├── calculadora-segmentacion.css
│   ├── filtros-cliente.json
│   └── output-decision.md
│
├── 📂 02-capa-venta/                 # Todo para la reunión de venta
│   ├── infografias/                  # 3 infografías (PDF + Canva)
│   ├── contratos/                    # 5 contratos listos para firmar
│   ├── scripts/                      # Guiones palabra por palabra
│   └── material-fisico/              # Stickers, tarjetas, posters
│
├── 📂 03-capa-entrega/               # Post-venta y ejecución
│   ├── checklists/                   # Uno por subfase
│   ├── onboarding/                   # Día 0 al día 30
│   ├── triggers-crm/                 # Alertas SQL automáticas
│   └── reportes-mensuales/           # Templates automáticos
│
├── 📂 04-programas-transversales/    # Aplica a todos los clientes
│   ├── referidos/                    # "Traes 1, Ganas 1"
│   ├── dashboard-looker/             # Config + queries
│   ├── suscripcion/                  # Modelo híbrido
│   └── captacion-medvi/              # Landing page + flujo
│
├── 📂 05-documentacion-tecnica/      # Para dev y consultor avanzado
│   ├── diagramas-uml/                # 24 diagramas
│   ├── arquitectura-real/            # Tu código actual
│   ├── plan-b-herramientas/          # Alternativas
│   └── kit-emergencia/               # Crisis: bot caído, Meta bloquea...
│
├── 📂 06-backend-servicios/          # FastAPI + Neon DB
│   ├── main.py                       # Webhook + API completa
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/
│   └── routers/ services/ models/ database/
│
├── 📂 07-recursos/                   # Assets compartidos
│   ├── logo-isa-chatcommerce.svg
│   └── colores-isa.json
│
├── README.md                         # Este archivo
├── CHANGELOG.md                      # Historial de versiones
└── MANIFEST.json                     # Índice maestro
```

---

## 🚀 CÓMO EMPEZAR

### 1. Instalar la PWA (Calculadora)

```bash
# Opción A: Servir localmente
cd app/
python -m http.server 8000
# Abrir http://localhost:8000 en Chrome
# "Añadir a pantalla de inicio"

# Opción B: Subir a Netlify
# Arrastra la carpeta 'app/' en https://app.netlify.com/drop

# Opción C: Subir a GitHub Pages
# Push la carpeta 'app/' a un repo y activar GitHub Pages
```

### 2. Deployar el backend (Render)

```bash
cd 06-backend-servicios/

# Crear virtualenv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar local
uvicorn main:app --reload

# Deploy en Render:
# 1. Crear cuenta en render.com
# 2. New Web Service → Connect GitHub repo
# 3. Build command: pip install -r requirements.txt
# 4. Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
# 5. Añadir environment variables desde .env
```

### 3. Configurar WhatsApp Cloud API

1. Crear app en [Meta Developers](https://developers.facebook.com)
2. Añadir producto "WhatsApp"
3. Verificar número de teléfono
4. Configurar webhook: `https://tu-render-url/webhook`
5. Suscribirse a eventos: `messages`

### 4. Configurar Neon DB

1. Crear cuenta en [Neon](https://neon.tech)
2. Crear proyecto y base de datos
3. Copiar connection string a `NEON_DB_URL`

---

## 📱 USO EN CAMPO (Consultor)

### Mañana (preparación)
1. Abrir app en tablet/móvil
2. Revisar historial de ayer
3. Preparar contratos que necesitarás

### Reunión (15-30 min)
1. **P0** → Validar CIN + RIB
2. **P1-P4** → Calculadora de segmentación
3. **Infografía 1** → Embudo visual (5 min)
4. **Infografía 2** → Ventana 24h (5 min)
5. **Infografía 3** → Comparador de packs (10 min)
6. **Oferta Gancho** → Cierre (5 min)
7. **Firma + material físico**

### Tarde (entrega)
1. Ejecutar checklist de subfase
2. Enviar mensaje de bienvenida
3. Actualizar dashboard

---

## 🛠️ PERSONALIZACIÓN

### Cambiar precios
Editar `06-backend-servicios/config/config.json`:
```json
"pricing": {
  "presencia": {"setup": 250, "mantenimiento": 200},
  "whatsapp-pro": {"setup": 400, "mantenimiento": 250}
}
```

### Cambiar ciudad
Editar `app/assets/data.js`:
```javascript
ciudad: 'Tetuán',
```

### Añadir tipo de negocio
Editar `app/assets/data.js` → `benchmarks`:
```javascript
ferreteria: { conversaciones_mes: '400-800', pedidos_mes: '30-60', roi: '600-1200%' }
```

---

## 📞 SOPORTE

- WhatsApp: +212 612-345-678
- Email: consultor@isa-chatcommerce.ma
- Dashboard: [Looker Studio](https://lookerstudio.google.com)

---

**ISA ChatCommerce — Transformando negocios locales en Tetuán, un WhatsApp a la vez.** 🚀
