from typing import Dict, Any
from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self):
        pass

    async def calcular_roi(self, ingresos: float, costos: float) -> float:
        if costos == 0:
            return 0.0
        return round(((ingresos - costos) / costos) * 100, 2)

    async def calcular_metricas_dashboard(self, db_pool) -> Dict[str, Any]:
        # En producción: queries reales a la DB
        return {
            "total_clientes": 0,
            "clientes_activos": 0,
            "clientes_riesgo": 0,
            "mensajes_hoy": 0,
            "reservaciones_hoy": 0,
            "ingresos_mes": 0.0,
            "roi_promedio": 0.0,
            "fecha_actualizacion": datetime.utcnow().isoformat()
        }

    async def detectar_trigger(self, metricas: Dict[str, Any]) -> list:
        triggers = []

        # +30% consultas en 15 días → upsell
        if metricas.get("pct_consultas", 0) >= 0.30:
            triggers.append({
                "tipo": "upsell",
                "mensaje": "El cliente tiene +30% de consultas. Oportunidad de upsell.",
                "accion": "contactar_ventas"
            })

        # >30 mensajes/día → semi-digital
        if metricas.get("mensajes_dia", 0) >= 30:
            triggers.append({
                "tipo": "semi_digital",
                "mensaje": ">30 mensajes/día. Recomendar pack digital.",
                "accion": "ofrecer_whatsapp_pro"
            })

        # 3 señales → growth
        señales = metricas.get("señales_positivas", 0)
        if señales >= 3:
            triggers.append({
                "tipo": "escalamiento_growth",
                "mensaje": "3 señales positivas. Escalar a pack Growth.",
                "accion": "reunion_growth"
            })

        # Cliente crítico
        dias_sin_respuesta = metricas.get("dias_sin_respuesta", 0)
        if dias_sin_respuesta >= 7:
            triggers.append({
                "tipo": "cliente_critico",
                "mensaje": "Cliente sin respuesta 7+ días. Intervención urgente.",
                "accion": "llamada_urgente",
                "prioridad": "alta"
            })

        return triggers

analytics = AnalyticsService()
