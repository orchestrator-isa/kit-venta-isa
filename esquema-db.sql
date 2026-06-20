-- Esquema ISA ChatCommerce v3.1
-- Ejecutar en Neon o Render PostgreSQL

CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    telefono VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100),
    nombre_negocio VARCHAR(100),
    tipo_negocio VARCHAR(50),
    segmento VARCHAR(20),
    pack_asignado VARCHAR(50),
    setup_pagado DECIMAL(10,2) DEFAULT 0,
    mensualidad DECIMAL(10,2) DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'prospecto',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_interaccion TIMESTAMP,
    mensajes_dia INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS reservaciones (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    codigo_reserva VARCHAR(20) UNIQUE NOT NULL,
    hora_reserva TIMESTAMP NOT NULL,
    mesa_asignada VARCHAR(10),
    zona VARCHAR(50),
    ai_confirmada BOOLEAN DEFAULT FALSE,
    estado VARCHAR(20) DEFAULT 'pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mensajes (
    id SERIAL PRIMARY KEY,
    telefono VARCHAR(20) NOT NULL,
    direccion VARCHAR(10) NOT NULL,
    contenido TEXT,
    tipo VARCHAR(20) DEFAULT 'texto',
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS leads_scrap (
    id SERIAL PRIMARY KEY,
    telefono VARCHAR(20) NOT NULL,
    nombre VARCHAR(100),
    nombre_negocio VARCHAR(100),
    tipo_negocio VARCHAR(50),
    segmento VARCHAR(20),
    pack_asignado VARCHAR(50),
    caso VARCHAR(5),
    mensaje_personalizado TEXT,
    fuente VARCHAR(50),
    estado_contacto VARCHAR(20) DEFAULT 'no_contactado',
    fecha_scrap TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_contacto TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_clientes_telefono ON clientes(telefono);
CREATE INDEX IF NOT EXISTS idx_clientes_estado ON clientes(estado);
CREATE INDEX IF NOT EXISTS idx_mensajes_telefono ON mensajes(telefono);
CREATE INDEX IF NOT EXISTS idx_mensajes_fecha ON mensajes(fecha);
CREATE INDEX IF NOT EXISTS idx_leads_caso ON leads_scrap(caso);
CREATE INDEX IF NOT EXISTS idx_leads_estado ON leads_scrap(estado_contacto);
CREATE INDEX IF NOT EXISTS idx_reservaciones_cliente ON reservaciones(cliente_id);
CREATE INDEX IF NOT EXISTS idx_reservaciones_codigo ON reservaciones(codigo_reserva);
