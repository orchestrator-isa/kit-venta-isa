// kit-venta-isa v3.0 — Datos de configuración
const ISA_CONFIG = {
  version: '3.0',
  ciudad: 'Tetuán',
  moneda: 'MAD',
  consultor: {
    nombre: 'Consultor ISA',
    telefono: '+212 612-345-678',
    whatsapp: 'https://wa.me/212612345678'
  },

  // P0 — Filtro de clientes válidos
  p0: {
    titulo: 'Validación de Cliente',
    descripcion: 'Antes de empezar, verificamos que el negocio puede operar legalmente.',
    preguntas: [
      { id: 'cin', texto: '¿Tiene CIN (Carte d'Identité Nationale) válido?', tipo: 'si_no', obligatorio: true },
      { id: 'rib', texto: '¿Tiene RIB bancario activo?', tipo: 'si_no', obligatorio: true },
      { id: 'local', texto: '¿Tiene local físico o negocio registrado?', tipo: 'si_no', obligatorio: true }
    ],
    mensaje_rechazo: 'Hermano, necesitamos una base legal para empezar. Te ayudo a tramitar el RIB en 3 días. ¿Empezamos?'
  },

  // P1 — Segmentación por facturación
  p1_facturacion: {
    titulo: 'Facturación Mensual',
    descripcion: '¿Cuánto factura su negocio al mes aproximadamente?',
    opciones: [
      { 
        id: 'pobre', 
        label: '< 5.000 MAD', 
        descripcion: 'Negocio pequeño, recién iniciado',
        pack: 'presencia',
        setup: 250,
        mantenimiento: 200,
        flujo: ['1A', '1B', '1C'],
        tiempo: '1 semana',
        recomendacion: 'Empezar con presencia básica. El 80% de los negocios en esta etapa no aparecen en Google Maps.'
      },
      { 
        id: 'pobre-medio', 
        label: '5.000 — 15.000 MAD', 
        descripcion: 'Negocio establecido, clientes regulares',
        pack: 'whatsapp-pro',
        setup: 400,
        mantenimiento: 250,
        flujo: ['1A', '1B', '1C', '2A'],
        tiempo: '2 semanas',
        recomendacion: 'WhatsApp Pro le permite tener catálogo de productos y responder automáticamente.'
      },
      { 
        id: 'estandar', 
        label: '15.000 — 40.000 MAD', 
        descripcion: 'Negocio con buen flujo, quiere crecer',
        pack: 'completo',
        setup: 1200,
        mantenimiento: 600,
        flujo: ['1A', '1B', '1C', '2A', '2B', '3A', '3B', '3C'],
        tiempo: '3 semanas',
        recomendacion: 'Pack Completo: bot IA 24/7, landing page profesional, dashboard de ROI.'
      },
      { 
        id: 'premium', 
        label: '> 40.000 MAD', 
        descripcion: 'Negocio grande, quiere dominar el mercado',
        pack: 'growth',
        setup: 1500,
        mantenimiento: 600,
        flujo: ['1A', '1B', '1C', '2A', '2B', '3A', '3B', '3C', '4A', '5A'],
        tiempo: '4 semanas',
        recomendacion: 'Pack Growth: todo lo anterior + Google Ads + SEO avanzado + formación de equipo.'
      }
    ]
  },

  // P2 — WhatsApp Business
  p2_whatsapp: {
    titulo: 'WhatsApp Business',
    descripcion: '¿Qué nivel de WhatsApp tiene su negocio?',
    opciones: [
      { id: 'no', label: 'No tiene WhatsApp Business', accion: 'incluir-1a2', descripcion: 'Instalamos y configuramos desde cero' },
      { id: 'basico', label: 'Sí, versión básica', accion: 'saltar-1a2', descripcion: 'Optimizamos lo que tiene' },
      { id: 'catalogo', label: 'Sí, con catálogo de productos', accion: 'saltar-1a2-1b', descripcion: 'Saltamos a automatización avanzada' }
    ]
  },

  // P3 — Google Maps
  p3_maps: {
    titulo: 'Google Maps',
    descripcion: '¿Cómo está su presencia en Google Maps?',
    opciones: [
      { id: 'no', label: 'No aparece en Google Maps', accion: 'incluir-1a1', descripcion: 'Creamos ficha desde cero' },
      { id: 'sin-optimizar', label: 'Sí, pero sin fotos ni reseñas', accion: 'optimizar-1a1', descripcion: 'Optimizamos fotos, horarios, descripción' },
      { id: 'optimizado', label: 'Sí, está optimizado', accion: 'saltar-1a1', descripcion: 'Saltamos a siguiente fase' }
    ]
  },

  // P4 — Clientes por día
  p4_clientes: {
    titulo: 'Clientes por Día',
    descripcion: '¿Cuántos clientes atiende aproximadamente por día?',
    opciones: [
      { id: 'pocos', label: '< 10 clientes/día', recomendacion: 'Fase 1 + 2: Presencia + Persuasión' },
      { id: 'moderado', label: '10 — 30 clientes/día', recomendacion: 'Fase 1 + 2 + 3A: Añadir WhatsApp Pro' },
      { id: 'muchos', label: '> 30 clientes/día', recomendacion: 'Fase 3 directo: Automatización completa' }
    ]
  },

  // Oferta Gancho
  oferta_gancho: {
    activa: true,
    limite_clientes: 10,
    setup_gratis: true,
    mantenimiento_mes: 200,
    periodo_prueba_dias: 30,
    condicion: 'Solo paga si ve resultados (más mensajes, más clientes, más ventas)',
    materiales: 50,
    compromiso_post_prueba: '3 meses de mantenimiento si continúa'
  },

  // Packs detallados
  packs: {
    presencia: {
      nombre: 'Presencia',
      setup: 250,
      mantenimiento: 200,
      entrega: '48 horas',
      incluye: [
        'Google Maps optimizado',
        'WhatsApp Business básico',
        'QR Code para puerta/mostrador',
        '1 red social configurada',
        '10 fotos profesionales'
      ],
      resultado: '"Me encuentran"'
    },
    'whatsapp-pro': {
      nombre: 'WhatsApp Pro',
      setup: 400,
      mantenimiento: 250,
      entrega: '72 horas',
      incluye: [
        'Todo lo de Presencia',
        'Catálogo de productos en WhatsApp',
        'Respuestas automáticas básicas',
        '2 redes sociales configuradas',
        'Linktree personalizado'
      ],
      resultado: '"Me escriben"'
    },
    completo: {
      nombre: 'Completo',
      setup: 1200,
      mantenimiento: 600,
      entrega: '1 semana',
      incluye: [
        'Todo lo de WhatsApp Pro',
        'Landing page profesional (Vercel)',
        'Dominio + email corporativo',
        'Chatbot IA 24/7 (GPT-4)',
        'Dashboard Looker con ROI',
        'HubSpot CRM integrado',
        '4 posts + 2 reels/mes',
        'Reportes mensuales detallados'
      ],
      resultado: '"Venden solos"'
    },
    growth: {
      nombre: 'Growth',
      setup: 1500,
      mantenimiento: 600,
      entrega: '2 semanas',
      incluye: [
        'Todo lo de Completo',
        'Google Ads Local (campañas optimizadas)',
        'SEO Avanzado (Top 3 Google Maps)',
        'Programa Referidos Premium',
        '1 sesión formación equipo',
        'Soporte prioritario WhatsApp'
      ],
      resultado: '"Crecemos juntos"'
    },
    enterprise: {
      nombre: 'Enterprise',
      setup: 2500,
      mantenimiento: 1000,
      entrega: '3 semanas',
      incluye: [
        'Todo lo de Growth',
        'Google Ads Avanzado + seguimiento',
        'SEO Multilingüe (AR/FR/ES/EN)',
        '8 posts + 4 reels/mes',
        'Gestión comunidad redes privadas',
        'Formación avanzada 4 horas',
        'Soporte 24/7 prioritario'
      ],
      resultado: '"Dominamos el mercado"'
    }
  },

  // Benchmarks por tipo de negocio
  benchmarks: {
    restaurante: { conversaciones_mes: '800-1500', pedidos_mes: '60-120', roi: '1500-3000%' },
    clinica: { conversaciones_mes: '200-400', pedidos_mes: '15-30', roi: '800-1500%' },
    tienda: { conversaciones_mes: '300-600', pedidos_mes: '20-50', roi: '1000-2000%' },
    peluqueria: { conversaciones_mes: '150-300', pedidos_mes: '10-25', roi: '500-1200%' },
    gimnasio: { conversaciones_mes: '100-250', pedidos_mes: '5-15', roi: '400-800%' }
  }
};

// Exportar para módulos (si se usa como módulo)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ISA_CONFIG;
}
