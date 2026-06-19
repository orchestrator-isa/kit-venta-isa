-- Dashboard Semáforo — Salud del Cliente
-- Ejecutar cada hora

SELECT 
    c.id,
    c.nombre_negocio,
    c.pack_actual,
    c.telefono,
    COALESCE(m.conversaciones_diarias, 0) as consultas_hoy,
    COALESCE(m.reseñas_nuevas_mes, 0) as reseñas_mes,
    COALESCE(m.ingresos_pct_cambio, 0) as ingresos_pct,
    c.ultimo_contacto,
    CASE 
        WHEN COALESCE(m.conversaciones_diarias, 0) > 30 
             AND COALESCE(m.reseñas_nuevas_mes, 0) > 5 
             AND COALESCE(m.ingresos_pct_cambio, 0) > 0 
        THEN 'VERDE'
        WHEN (COALESCE(m.conversaciones_diarias, 0) BETWEEN 10 AND 30)
             OR (COALESCE(m.reseñas_nuevas_mes, 0) BETWEEN 3 AND 5)
        THEN 'AMARILLO'
        ELSE 'ROJO'
    END as semaforo,
    CASE 
        WHEN COALESCE(m.conversaciones_diarias, 0) > 30 THEN '🔄 Upgradear'
        WHEN COALESCE(m.conversaciones_diarias, 0) BETWEEN 10 AND 30 THEN '📞 Llamar'
        ELSE '🚨 Intervenir'
    END as accion_recomendada
FROM clientes c
LEFT JOIN metricas_vista m ON c.id = m.cliente_id
WHERE c.estado = 'ACTIVO'
ORDER BY 
    CASE semaforo 
        WHEN 'ROJO' THEN 1 
        WHEN 'AMARILLO' THEN 2 
        WHEN 'VERDE' THEN 3 
    END,
    c.ultimo_contacto ASC;
