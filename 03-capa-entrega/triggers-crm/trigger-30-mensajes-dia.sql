-- TRIGGER: >30 mensajes/día → Semi-Digital Pro

SELECT 
    c.id,
    c.nombre_negocio,
    AVG(m.conversaciones_diarias) as promedio_diario
FROM clientes c
JOIN metricas_diarias m ON c.id = m.cliente_id
WHERE c.estado = 'ACTIVO'
  AND m.fecha >= CURRENT_DATE - INTERVAL '7 days'
  AND c.pack_actual = 'whatsapp-pro'
GROUP BY c.id, c.nombre_negocio
HAVING AVG(m.conversaciones_diarias) > 30;

-- ACCIÓN: Proponer upgrade a Semi-Digital Pro (950 MAD)
