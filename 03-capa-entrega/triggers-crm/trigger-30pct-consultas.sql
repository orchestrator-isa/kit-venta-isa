-- TRIGGER: +30% consultas en 15 días → Upsell
-- Ejecutar diariamente

SELECT 
    c.id,
    c.nombre_negocio,
    c.pack_actual,
    m.conversaciones_ultimos_15d,
    m.conversaciones_15d_anterior,
    CASE 
        WHEN m.conversaciones_15d_anterior > 0 
        THEN ((m.conversaciones_ultimos_15d - m.conversaciones_15d_anterior) * 100.0 / m.conversaciones_15d_anterior)
        ELSE 0 
    END as pct_cambio
FROM clientes c
JOIN metricas_cliente m ON c.id = m.cliente_id
WHERE c.estado = 'ACTIVO'
  AND m.conversaciones_ultimos_15d > m.conversaciones_15d_anterior * 1.30
  AND c.pack_actual IN ('presencia', 'whatsapp-pro')
ORDER BY pct_cambio DESC;

-- ACCIÓN: Notificar consultor para ofrecer upsell
