# Template de Output — Calculadora de Segmentación

## Ejemplo de resultado en pantalla:

```
┌─────────────────────────────────────────┐
│  ✅ RESULTADO ISA                        │
├─────────────────────────────────────────┤
│                                          │
│  Segmento:      ESTÁNDAR                │
│  Pack:          Completo (1.200 MAD)    │
│  Flujo:         1A.1 → 1B → 1C → 2A    │
│                 → 2B → 3A → 3B → 3C    │
│  Tiempo:        3 semanas               │
│  Inversión:     1.200 MAD + 600/mes   │
│                                          │
│  📄 Documento a sacar:                  │
│     Contrato_Completo_v3.pdf            │
│                                          │
│  🎁 Oferta Gancho: NO (pack > 400 MAD)  │
│                                          │
└─────────────────────────────────────────┘
```

## Reglas de decisión:
- Si setup <= 400 MAD → Ofrecer Oferta Gancho
- Si setup > 400 MAD → Ofrecer pack normal con 50% inicial
- Si P0 = NO → No continuar, ofrecer ayuda con trámites
