-- TRIGGER: Cliente en riesgo de abandono 🔴

SELECT 
    c.id,
    c.nombre_negocio,
    c.pack_actual,
    c.ultimo_contacto,
    c.ultimo_pago,
    m.conversaciones_diarias,
    CASE 
        WHEN m.conversaciones_diarias = 0 AND c.ultimo_contacto < CURRENT_DATE - INTERVAL '7 days' THEN 'CRITICO'
        WHEN m.conversaciones_diarias < 5 AND c.ultimo_pago < CURRENT_DATE - INTERVAL '15 days' THEN 'RIESGO'
        ELSE 'ESTABLE'
    END as nivel_riesgo
FROM clientes c
LEFT JOIN metricas_diarias m ON c.id = m.cliente_id AND m.fecha = CURRENT_DATE
WHERE c.estado = 'ACTIVO'
  AND (
    (m.conversaciones_diarias = 0 AND c.ultimo_contacto < CURRENT_DATE - INTERVAL '7 days')
    OR (m.conversaciones_diarias < 5 AND c.ultimo_pago < CURRENT_DATE - INTERVAL '15 days')
  )
ORDER BY nivel_riesgo, c.ultimo_contacto;

-- ACCIÓN: 
-- CRITICO → Llamada urgente + email + WhatsApp
-- RIESGO → Llamada de retención + oferta descuento
