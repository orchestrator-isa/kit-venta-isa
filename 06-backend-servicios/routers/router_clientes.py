from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models.schemas import ClienteCreate, ClienteResponse, LeadScrapCreate, LeadScrapResponse
import asyncpg
from database.database import get_db_pool

router = APIRouter(prefix="/clientes", tags=["clientes"])

async def get_db():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        yield conn

@router.get("/", response_model=List[ClienteResponse])
async def listar_clientes(estado: Optional[str] = None, db: asyncpg.Connection = Depends(get_db)):
    if estado:
        rows = await db.fetch("SELECT * FROM clientes WHERE estado = $1 ORDER BY fecha_registro DESC", estado)
    else:
        rows = await db.fetch("SELECT * FROM clientes ORDER BY fecha_registro DESC")
    return [dict(row) for row in rows]

@router.post("/", response_model=ClienteResponse)
async def crear_cliente(cliente: ClienteCreate, db: asyncpg.Connection = Depends(get_db)):
    query = """
        INSERT INTO clientes (telefono, nombre, nombre_negocio, tipo_negocio, segmento, pack_asignado)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING *
    """
    row = await db.fetchrow(query, cliente.telefono, cliente.nombre, cliente.nombre_negocio,
                            cliente.tipo_negocio, cliente.segmento, cliente.pack_asignado)
    return dict(row)

@router.get("/{telefono}", response_model=ClienteResponse)
async def obtener_cliente(telefono: str, db: asyncpg.Connection = Depends(get_db)):
    row = await db.fetchrow("SELECT * FROM clientes WHERE telefono = $1", telefono)
    if not row:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return dict(row)

# Leads Scrap (sin bot)
@router.get("/leads/scrap", response_model=List[LeadScrapResponse])
async def listar_leads_scrap(caso: Optional[str] = None, db: asyncpg.Connection = Depends(get_db)):
    if caso:
        rows = await db.fetch("SELECT * FROM leads_scrap WHERE caso = $1 ORDER BY fecha_scrap DESC", caso)
    else:
        rows = await db.fetch("SELECT * FROM leads_scrap ORDER BY fecha_scrap DESC")
    return [dict(row) for row in rows]

@router.post("/leads/scrap", response_model=LeadScrapResponse)
async def crear_lead_scrap(lead: LeadScrapCreate, db: asyncpg.Connection = Depends(get_db)):
    query = """
        INSERT INTO leads_scrap (telefono, nombre, nombre_negocio, tipo_negocio, segmento, 
                                pack_asignado, caso, mensaje_personalizado, fuente)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING *
    """
    row = await db.fetchrow(query, lead.telefono, lead.nombre, lead.nombre_negocio,
                            lead.tipo_negocio, lead.segmento, lead.pack_asignado,
                            lead.caso, lead.mensaje_personalizado, lead.fuente)
    return dict(row)
