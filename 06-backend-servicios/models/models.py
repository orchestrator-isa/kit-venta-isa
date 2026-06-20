from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    telefono = Column(String(20), unique=True, index=True)
    nombre = Column(String(100))
    nombre_negocio = Column(String(100))
    tipo_negocio = Column(String(50))  # restaurante, clinica, tienda
    segmento = Column(String(20))  # pobre, pobre-medio, estandar, premium
    pack_asignado = Column(String(50))
    setup_pagado = Column(Float, default=0)
    mensualidad = Column(Float, default=0)
    estado = Column(String(20), default="prospecto")  # prospecto, activo, riesgo, cancelado
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    ultima_interaccion = Column(DateTime)
    mensajes_dia = Column(Integer, default=0)
    metadata = Column(JSON, default=dict)

class Reservacion(Base):
    __tablename__ = "reservaciones"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, index=True)
    codigo_reserva = Column(String(20), unique=True)
    hora_reserva = Column(DateTime)
    mesa_asignada = Column(String(10))
    zona = Column(String(50))
    ai_confirmada = Column(Boolean, default=False)
    estado = Column(String(20), default="pendiente")  # pendiente, confirmada, cancelada
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, index=True)
    telefono = Column(String(20), index=True)
    direccion = Column(String(10))  # inbound, outbound
    contenido = Column(Text)
    tipo = Column(String(20), default="texto")  # texto, imagen, boton
    fecha = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default=dict)

class LeadScrap(Base):
    __tablename__ = "leads_scrap"

    id = Column(Integer, primary_key=True, index=True)
    telefono = Column(String(20), index=True)
    nombre = Column(String(100))
    nombre_negocio = Column(String(100))
    tipo_negocio = Column(String(50))
    segmento = Column(String(20))
    pack_asignado = Column(String(50))
    caso = Column(String(5))  # A, B, C, D, E, F, G
    mensaje_personalizado = Column(Text)
    fuente = Column(String(50))  # maps, referido, ads
    estado_contacto = Column(String(20), default="no_contactado")
    fecha_scrap = Column(DateTime, default=datetime.utcnow)
    fecha_contacto = Column(DateTime)
