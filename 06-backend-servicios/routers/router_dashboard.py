from fastapi import APIRouter, Depends
from typing import Dict, Any
from models.schemas import DashboardMetrics
import asyncpg
from database.database import get_db_pool

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

async def get_db():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        yield conn

@router.get("/metricas", response_model=DashboardMetrics)
async def get_metricas(db: asyncpg.Connection = Depends(get_db)):
    total = await db.fetchval("SELECT COUNT(*) FROM clientes")
    activos = await db.fetchval("SELECT COUNT(*) FROM clientes WHERE estado = 'activo'")
    riesgo = await db.fetchval("SELECT COUNT(*) FROM clientes WHERE estado = 'riesgo'")
    mensajes_hoy = await db.fetchval("""
        SELECT COUNT(*) FROM mensajes 
        WHERE DATE(fecha) = CURRENT_DATE
    """)
    reservas_hoy = await db.fetchval("""
        SELECT COUNT(*) FROM reservaciones 
        WHERE DATE(fecha_creacion) = CURRENT_DATE
    """)

    return {
        "total_clientes": total or 0,
        "clientes_activos": activos or 0,
        "clientes_riesgo": riesgo or 0,
        "mensajes_hoy": mensajes_hoy or 0,
        "reservaciones_hoy": reservas_hoy or 0,
        "ingresos_mes": 0.0,  # Calcular desde pagos
        "roi_promedio": 0.0   # Calcular desde analytics
    }

@router.get("/triggers")
async def get_triggers(db: asyncpg.Connection = Depends(get_db)):
    # Detectar triggers automáticos
    triggers = []

    # Clientes críticos (7+ días sin respuesta)
    criticos = await db.fetch("""
        SELECT telefono, nombre, nombre_negocio 
        FROM clientes 
        WHERE estado = 'activo' 
        AND (ultima_interaccion IS NULL OR ultima_interaccion < NOW() - INTERVAL '7 days')
    """)

    for c in criticos:
        triggers.append({
            "tipo": "cliente_critico",
            "cliente": dict(c),
            "mensaje": f"{c['nombre_negocio']} sin contacto 7+ días",
            "accion": "llamada_urgente",
            "prioridad": "alta"
        })

    return {"triggers": triggers, "total": len(triggers)}
