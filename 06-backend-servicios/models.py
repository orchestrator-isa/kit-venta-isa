"""
SQLAlchemy Models for ISA ChatCommerce
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, func
from database import Base

class LeadScrap(Base):
    __tablename__ = "leads_scrap"

    id = Column(Integer, primary_key=True, index=True)
    nombre_negocio = Column(String(255), nullable=False)
    nombre_contacto = Column(String(255), nullable=True)
    telefono = Column(String(50), nullable=False, index=True)
    direccion = Column(Text, nullable=True)
    ciudad = Column(String(100), nullable=True)
    caso = Column(String(10), nullable=True, index=True)
    pack_asignado = Column(String(50), nullable=True)
    fuente = Column(String(100), nullable=True)
    url_perfil = Column(Text, nullable=True)
    categoria = Column(String(100), nullable=True)
    estado = Column(String(50), default="nuevo", index=True)
    mensaje_personalizado = Column(Text, nullable=True)
    fecha_scrap = Column(DateTime(timezone=True), server_default=func.now())
    fecha_contacto = Column(DateTime(timezone=True), nullable=True)
    notas = Column(Text, nullable=True)
    score_segmentacion = Column(Integer, default=0)
    extra_data = Column(JSON, nullable=True)

class Reservacion(Base):
    __tablename__ = "reservaciones"

    id = Column(Integer, primary_key=True, index=True)
    codigo_reserva = Column(String(50), unique=True, nullable=False, index=True)
    cliente_nombre = Column(String(255), nullable=False)
    cliente_telefono = Column(String(50), nullable=False)
    fase = Column(String(20), default="res_p", index=True)
    hora_reserva = Column(DateTime(timezone=True), nullable=True)
    mesa_asignada = Column(String(50), nullable=True)
    zona = Column(String(100), nullable=True)
    ai_confirmada = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
