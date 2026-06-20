from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ClienteCreate(BaseModel):
    telefono: str = Field(..., pattern=r"^\+?[0-9]{8,15}$")
    nombre: Optional[str] = None
    nombre_negocio: Optional[str] = None
    tipo_negocio: Optional[str] = None
    segmento: Optional[str] = None
    pack_asignado: Optional[str] = None

class ClienteResponse(ClienteCreate):
    id: int
    estado: str
    fecha_registro: datetime
    mensajes_dia: int

    class Config:
        from_attributes = True

class ReservacionCreate(BaseModel):
    cliente_id: int
    codigo_reserva: str
    hora_reserva: datetime
    mesa_asignada: Optional[str] = None
    zona: Optional[str] = None

class ReservacionResponse(ReservacionCreate):
    id: int
    ai_confirmada: bool
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class MensajeWhatsApp(BaseModel):
    telefono: str
    contenido: str
    tipo: str = "texto"
    metadata: Optional[Dict[str, Any]] = None

class WebhookPayload(BaseModel):
    object: str
    entry: list

class LeadScrapCreate(BaseModel):
    telefono: str
    nombre: Optional[str] = None
    nombre_negocio: Optional[str] = None
    tipo_negocio: Optional[str] = None
    segmento: Optional[str] = None
    pack_asignado: Optional[str] = None
    caso: Optional[str] = None
    mensaje_personalizado: Optional[str] = None
    fuente: Optional[str] = None

class LeadScrapResponse(LeadScrapCreate):
    id: int
    estado_contacto: str
    fecha_scrap: datetime

    class Config:
        from_attributes = True

class DashboardMetrics(BaseModel):
    total_clientes: int
    clientes_activos: int
    clientes_riesgo: int
    mensajes_hoy: int
    reservaciones_hoy: int
    ingresos_mes: float
    roi_promedio: float
