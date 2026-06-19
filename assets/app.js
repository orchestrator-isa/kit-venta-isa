// kit-venta-isa v3.0 — App completa (PWA)
// Compatible con: Chrome Android, Safari iOS, Samsung Internet

(function() {
  'use strict';

  // ===== ESTADO =====
  const state = {
    step: 0,
    totalSteps: 5,
    respuestas: {},
    historial: [],
    cliente: null
  };

  // ===== DOM ELEMENTS =====
  const $ = id => document.getElementById(id);
  const $$ = sel => document.querySelectorAll(sel);

  // ===== INICIALIZACIÓN =====
  document.addEventListener('DOMContentLoaded', () => {
    renderStepper();
    renderP0();
    initServiceWorker();
    loadHistorial();
  });

  // ===== SERVICE WORKER (PWA) =====
  function initServiceWorker() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('sw.js')
        .then(reg => console.log('SW registrado'))
        .catch(err => console.log('SW error:', err));
    }
  }

  // ===== RENDER STEPPER =====
  function renderStepper() {
    const container = $('stepper');
    if (!container) return;

    let html = '';
    for (let i = 0; i < state.totalSteps; i++) {
      const isActive = i === state.step;
      const isCompleted = i < state.step;
      const stepClass = isActive ? 'active' : (isCompleted ? 'completed' : '');
      const stepNum = isCompleted ? '✓' : (i + 1);

      html += `<div class="step ${stepClass}">${stepNum}</div>`;
      if (i < state.totalSteps - 1) {
        const lineClass = isCompleted ? 'completed' : '';
        html += `<div class="step-line ${lineClass}"></div>`;
      }
    }
    container.innerHTML = html;
  }

  // ===== P0 — FILTRO DE CLIENTE =====
  function renderP0() {
    const config = ISA_CONFIG.p0;
    const container = $('main-content');

    container.innerHTML = `
      <div class="card animate-in">
        <div class="card-title">🔍 ${config.titulo}</div>
        <div class="card-subtitle">${config.descripcion}</div>
        <div id="p0-preguntas"></div>
        <button class="btn btn-primary hidden" id="btn-p0-continuar" onclick="app.validarP0()">
          Continuar →
        </button>
      </div>
    `;

    const pregContainer = $('p0-preguntas');
    config.preguntas.forEach((preg, idx) => {
      pregContainer.innerHTML += `
        <div class="option-btn" id="p0-preg-${idx}" onclick="app.toggleP0(${idx})">
          <span class="opt-label">${preg.texto}</span>
          <span class="opt-desc">Toca para seleccionar</span>
        </div>
      `;
    });
  }

  function toggleP0(idx) {
    const btn = $(`p0-preg-${idx}`);
    const isSelected = btn.classList.contains('selected');

    // Toggle visual
    if (isSelected) {
      btn.classList.remove('selected');
      btn.querySelector('.opt-desc').textContent = 'Toca para seleccionar';
      delete state.respuestas[`p0_${idx}`];
    } else {
      btn.classList.add('selected');
      btn.querySelector('.opt-desc').textContent = '✓ Seleccionado';
      state.respuestas[`p0_${idx}`] = true;
    }

    // Mostrar botón continuar si todas están seleccionadas
    const config = ISA_CONFIG.p0;
    const obligatorias = config.preguntas.filter(p => p.obligatorio).length;
    const seleccionadas = Object.keys(state.respuestas).filter(k => k.startsWith('p0_')).length;

    const btnContinuar = $('btn-p0-continuar');
    if (seleccionadas >= obligatorias) {
      btnContinuar.classList.remove('hidden');
    } else {
      btnContinuar.classList.add('hidden');
    }
  }

  function validarP0() {
    const config = ISA_CONFIG.p0;
    const todasSi = config.preguntas.every((preg, idx) => state.respuestas[`p0_${idx}`]);

    if (!todasSi) {
      showToast(config.mensaje_rechazo);
      return;
    }

    state.step = 1;
    renderStepper();
    renderP1();
  }

  // ===== P1 — FACTURACIÓN =====
  function renderP1() {
    const config = ISA_CONFIG.p1_facturacion;
    const container = $('main-content');

    let opcionesHtml = '';
    config.opciones.forEach((opt, idx) => {
      opcionesHtml += `
        <button class="option-btn" onclick="app.seleccionarP1(${idx})">
          <span class="opt-label">${opt.label}</span>
          <span class="opt-desc">${opt.descripcion}</span>
          <span class="opt-price">Setup: ${opt.setup} MAD + ${opt.mantenimiento}/mes</span>
        </button>
      `;
    });

    container.innerHTML = `
      <div class="card animate-in">
        <div class="card-title">💰 ${config.titulo}</div>
        <div class="card-subtitle">${config.descripcion}</div>
        ${opcionesHtml}
      </div>
    `;
  }

  function seleccionarP1(idx) {
    state.respuestas.p1 = idx;
    state.step = 2;
    renderStepper();
    renderP2();
  }

  // ===== P2 — WHATSAPP =====
  function renderP2() {
    const config = ISA_CONFIG.p2_whatsapp;
    const container = $('main-content');

    let opcionesHtml = '';
    config.opciones.forEach((opt, idx) => {
      opcionesHtml += `
        <button class="option-btn" onclick="app.seleccionarP2(${idx})">
          <span class="opt-label">${opt.label}</span>
          <span class="opt-desc">${opt.descripcion}</span>
        </button>
      `;
    });

    container.innerHTML = `
      <div class="card animate-in">
        <div class="card-title">💬 ${config.titulo}</div>
        <div class="card-subtitle">${config.descripcion}</div>
        ${opcionesHtml}
      </div>
    `;
  }

  function seleccionarP2(idx) {
    state.respuestas.p2 = idx;
    state.step = 3;
    renderStepper();
    renderP3();
  }

  // ===== P3 — GOOGLE MAPS =====
  function renderP3() {
    const config = ISA_CONFIG.p3_maps;
    const container = $('main-content');

    let opcionesHtml = '';
    config.opciones.forEach((opt, idx) => {
      opcionesHtml += `
        <button class="option-btn" onclick="app.seleccionarP3(${idx})">
          <span class="opt-label">${opt.label}</span>
          <span class="opt-desc">${opt.descripcion}</span>
        </button>
      `;
    });

    container.innerHTML = `
      <div class="card animate-in">
        <div class="card-title">🗺️ ${config.titulo}</div>
        <div class="card-subtitle">${config.descripcion}</div>
        ${opcionesHtml}
      </div>
    `;
  }

  function seleccionarP3(idx) {
    state.respuestas.p3 = idx;
    state.step = 4;
    renderStepper();
    renderP4();
  }

  // ===== P4 — CLIENTES/DÍA =====
  function renderP4() {
    const config = ISA_CONFIG.p4_clientes;
    const container = $('main-content');

    let opcionesHtml = '';
    config.opciones.forEach((opt, idx) => {
      opcionesHtml += `
        <button class="option-btn" onclick="app.seleccionarP4(${idx})">
          <span class="opt-label">${opt.label}</span>
          <span class="opt-desc">${opt.recomendacion}</span>
        </button>
      `;
    });

    container.innerHTML = `
      <div class="card animate-in">
        <div class="card-title">👥 ${config.titulo}</div>
        <div class="card-subtitle">${config.descripcion}</div>
        ${opcionesHtml}
      </div>
    `;
  }

  function seleccionarP4(idx) {
    state.respuestas.p4 = idx;
    state.step = 5;
    renderStepper();
    renderResultado();
  }

  // ===== RESULTADO =====
  function renderResultado() {
    const p1Opt = ISA_CONFIG.p1_facturacion.opciones[state.respuestas.p1];
    const pack = ISA_CONFIG.packs[p1Opt.pack];
    const oferta = ISA_CONFIG.oferta_gancho;

    const container = $('main-content');

    // Calcular flujo personalizado
    let flujoPersonalizado = p1Opt.flujo;
    const p2Opt = ISA_CONFIG.p2_whatsapp.opciones[state.respuestas.p2];
    const p3Opt = ISA_CONFIG.p3_maps.opciones[state.respuestas.p3];

    // Ajustar flujo según respuestas
    if (p2Opt.id === 'catalogo') {
      flujoPersonalizado = flujoPersonalizado.filter(f => f !== '1A.2' && f !== '1B');
    }
    if (p3Opt.id === 'optimizado') {
      flujoPersonalizado = flujoPersonalizado.filter(f => f !== '1A.1');
    }

    const ahora = new Date();
    const fecha = ahora.toLocaleDateString('es-MA');
    const hora = ahora.toLocaleTimeString('es-MA', {hour: '2-digit', minute:'2-digit'});

    // Guardar en historial
    const resultado = {
      id: Date.now(),
      fecha: fecha,
      hora: hora,
      negocio: 'Sin nombre',
      segmento: p1Opt.id,
      pack: p1Opt.pack,
      setup: p1Opt.setup,
      mantenimiento: p1Opt.mantenimiento,
      flujo: flujoPersonalizado,
      calificaGancho: oferta.activa && p1Opt.setup <= 400
    };

    state.cliente = resultado;
    guardarHistorial(resultado);

    container.innerHTML = `
      <div class="card animate-in">
        <div class="text-center mb-2">
          <span class="badge badge-green">✓ RESULTADO LISTO</span>
        </div>

        <div class="result-box">
          <div class="result-title">📊 DIAGNÓSTICO ISA</div>

          <div class="result-row">
            <span class="result-label">Segmento</span>
            <span class="result-value highlight">${p1Opt.id.toUpperCase()}</span>
          </div>

          <div class="result-row">
            <span class="result-label">Pack recomendado</span>
            <span class="result-value">${pack.nombre}</span>
          </div>

          <div class="result-row">
            <span class="result-label">Setup</span>
            <span class="result-value price">${p1Opt.setup} MAD</span>
          </div>

          <div class="result-row">
            <span class="result-label">Mantenimiento</span>
            <span class="result-value">${p1Opt.mantenimiento} MAD/mes</span>
          </div>

          <div class="result-row">
            <span class="result-label">Tiempo de entrega</span>
            <span class="result-value">${p1Opt.tiempo}</span>
          </div>

          <div class="result-row">
            <span class="result-label">Flujo</span>
            <span class="result-value">${flujoPersonalizado.join(' → ')}</span>
          </div>
        </div>

        <div class="card animate-in mt-2">
          <div class="card-title">📋 ¿Qué incluye?</div>
          <ul class="include-list">
            ${pack.incluye.map(item => `<li>${item}</li>`).join('')}
          </ul>
          <div class="text-center mt-2">
            <span class="badge badge-cyan">${pack.resultado}</span>
          </div>
        </div>

        ${oferta.activa && p1Opt.setup <= 400 ? `
        <div class="card animate-in mt-2" style="border-color: var(--gold);">
          <div class="text-center mb-2">
            <span class="badge badge-gold">🎁 OFERTA GANCHO</span>
          </div>
          <div class="card-title text-center" style="color: var(--gold);">
            Setup GRATIS
          </div>
          <div class="card-subtitle text-center">
            Solo paga <strong>${oferta.mantenimiento_mes} MAD/mes</strong> si ves resultados en ${oferta.periodo_prueba_dias} días.
            <br><br>
            <small style="color: var(--text-muted);">${oferta.condicion}</small>
          </div>
          <button class="btn btn-gold mt-2" onclick="app.generarContrato('gancho')">
            📄 Generar Contrato Oferta Gancho
          </button>
        </div>
        ` : ''}

        <button class="btn btn-primary mt-2" onclick="app.generarContrato('normal')">
          📄 Generar Contrato ${pack.nombre}
        </button>

        <button class="btn btn-secondary" onclick="app.compartirResultado()">
          📤 Compartir Resultado
        </button>

        <button class="btn btn-secondary" onclick="app.reiniciar()">
          🔄 Nueva Calculadora
        </button>
      </div>

      <div class="card animate-in mt-2">
        <div class="card-title">💡 Recomendación del consultor</div>
        <div class="card-subtitle">${p1Opt.recomendacion}</div>
      </div>
    `;
  }

  // ===== CONTRATO =====
  function generarContrato(tipo) {
    const cliente = state.cliente;
    const pack = ISA_CONFIG.packs[cliente.pack];
    const oferta = ISA_CONFIG.oferta_gancho;

    let contratoTexto = '';

    if (tipo === 'gancho') {
      contratoTexto = `
CONTRATO OFERTA GANCHO — ISA CHATCOMMERCE
==========================================

Fecha: ${cliente.fecha}
Hora: ${cliente.hora}

CLIENTE:
Nombre del negocio: _________________________
Nombre del dueño: ___________________________
CIN: _______________________________________
Teléfono: __________________________________
RIB: _______________________________________

OFERTA:
• Setup GRATIS (valor: ${cliente.setup} MAD)
• Mantenimiento: ${oferta.mantenimiento_mes} MAD/mes
• Período de prueba: ${oferta.periodo_prueba_dias} días
• Condición: Solo paga si ve resultados

RESULTADOS ESPERADOS:
• Más mensajes en WhatsApp
• Más clientes nuevos
• Más ventas

COMPROMISO:
Si al día ${oferta.periodo_prueba_dias} el cliente confirma resultados,
se compromete a ${oferta.compromiso_post_prueba}.

Materiales: ${oferta.materiales} MAD (pagados hoy)

FIRMA CLIENTE: _________________  FECHA: ________
FIRMA CONSULTOR: ______________  FECHA: ________
      `;
    } else {
      contratoTexto = `
CONTRATO PACK ${pack.nombre.toUpperCase()} — ISA CHATCOMMERCE
===============================================

Fecha: ${cliente.fecha}
Hora: ${cliente.hora}

CLIENTE:
Nombre del negocio: _________________________
Nombre del dueño: ___________________________
CIN: _______________________________________
Teléfono: __________________________________
RIB: _______________________________________

PACK: ${pack.nombre}
Setup: ${cliente.setup} MAD
Mantenimiento: ${cliente.mantenimiento} MAD/mes
Tiempo de entrega: ${pack.entrega}

INCLUYE:
${pack.incluye.map(i => '• ' + i).join('\n')}

PAGO:
50% inicial: ${cliente.setup / 2} MAD (hoy)
50% final: ${cliente.setup / 2} MAD (al entregar)

FIRMA CLIENTE: _________________  FECHA: ________
FIRMA CONSULTOR: ______________  FECHA: ________
      `;
    }

    // Crear blob y descargar
    const blob = new Blob([contratoTexto], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `contrato-${tipo}-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);

    showToast('📄 Contrato descargado. Imprime 2 copias.');
  }

  // ===== COMPARTIR =====
  function compartirResultado() {
    const cliente = state.cliente;
    const pack = ISA_CONFIG.packs[cliente.pack];

    const texto = `📊 DIAGNÓSTICO ISA — ${cliente.fecha}

🏪 Negocio: ${cliente.segmento.toUpperCase()}
📦 Pack: ${pack.nombre}
💰 Setup: ${cliente.setup} MAD
🔧 Mantenimiento: ${cliente.mantenimiento} MAD/mes
⏱️ Entrega: ${pack.entrega}

${pack.resultado}

¿Empezamos?`;

    if (navigator.share) {
      navigator.share({
        title: 'Diagnóstico ISA ChatCommerce',
        text: texto
      });
    } else {
      navigator.clipboard.writeText(texto).then(() => {
        showToast('📋 Resultado copiado al portapapeles');
      });
    }
  }

  // ===== HISTORIAL =====
  function guardarHistorial(resultado) {
    let hist = JSON.parse(localStorage.getItem('isa_historial') || '[]');
    hist.unshift(resultado);
    if (hist.length > 50) hist = hist.slice(0, 50);
    localStorage.setItem('isa_historial', JSON.stringify(hist));
    state.historial = hist;
  }

  function loadHistorial() {
    state.historial = JSON.parse(localStorage.getItem('isa_historial') || '[]');
  }

  function renderHistorial() {
    const container = $('main-content');

    if (state.historial.length === 0) {
      container.innerHTML = `
        <div class="card animate-in">
          <div class="card-title text-center">📋 Historial vacío</div>
          <div class="card-subtitle text-center">Aún no has realizado diagnósticos.</div>
          <button class="btn btn-primary mt-2" onclick="app.reiniciar()">Empezar ahora</button>
        </div>
      `;
      return;
    }

    let itemsHtml = state.historial.map(h => `
      <div class="option-btn" style="margin-bottom: 8px;">
        <span class="opt-label">${h.negocio || 'Sin nombre'} — ${h.pack}</span>
        <span class="opt-desc">${h.fecha} ${h.hora} | Setup: ${h.setup} MAD</span>
        <span class="opt-price">${h.calificaGancho ? '🎁 Califica Gancho' : ''}</span>
      </div>
    `).join('');

    container.innerHTML = `
      <div class="card animate-in">
        <div class="card-title">📋 Historial (${state.historial.length})</div>
        ${itemsHtml}
        <button class="btn btn-danger mt-2" onclick="app.limpiarHistorial()">
          🗑️ Limpiar historial
        </button>
      </div>
    `;
  }

  function limpiarHistorial() {
    if (confirm('¿Borrar todo el historial?')) {
      localStorage.removeItem('isa_historial');
      state.historial = [];
      renderHistorial();
      showToast('Historial borrado');
    }
  }

  // ===== HERRAMIENTAS =====
  function renderHerramientas() {
    const container = $('main-content');
    container.innerHTML = `
      <div class="card animate-in">
        <div class="card-title">🛠️ Herramientas</div>

        <button class="btn btn-secondary" onclick="app.renderBenchmarks()">
          📊 Benchmarks por sector
        </button>

        <button class="btn btn-secondary" onclick="app.renderCalculadoraROI()">
          🧮 Calculadora de ROI
        </button>

        <button class="btn btn-secondary" onclick="app.renderReferidos()">
          🤝 Programa "Traes 1, Ganas 1"
        </button>

        <button class="btn btn-secondary" onclick="app.renderVentana24h()">
          ⏰ Explicador Ventana 24h
        </button>
      </div>
    `;
  }

  function renderBenchmarks() {
    const container = $('main-content');
    const benchmarks = ISA_CONFIG.benchmarks;

    let html = '';
    for (const [tipo, data] of Object.entries(benchmarks)) {
      html += `
        <div class="option-btn" style="margin-bottom: 8px;">
          <span class="opt-label">${tipo.charAt(0).toUpperCase() + tipo.slice(1)}</span>
          <span class="opt-desc">💬 ${data.conversaciones_mes} conversaciones/mes</span>
          <span class="opt-desc">🛒 ${data.pedidos_mes} pedidos/mes</span>
          <span class="opt-price">📈 ROI: ${data.roi}</span>
        </div>
      `;
    }

    container.innerHTML = `
      <div class="card animate-in">
        <div class="card-title">📊 Benchmarks por Tipo de Negocio</div>
        <div class="card-subtitle">Expectativas realistas para Tetuán</div>
        ${html}
        <button class="btn btn-secondary mt-2" onclick="app.renderHerramientas()">← Volver</button>
      </div>
    `;
  }

  function renderCalculadoraROI() {
    const container = $('main-content');
    container.innerHTML = `
      <div class="card animate-in">
        <div class="card-title">🧮 Calculadora de ROI</div>

        <div class="option-btn" style="flex-direction: row; align-items: center;">
          <span class="opt-label">Inversión mensual (MAD):</span>
          <input type="number" id="roi-inversion" value="500" 
            style="background: var(--darker); border: 1px solid var(--cyan); color: var(--text); 
                   padding: 8px 12px; border-radius: 8px; width: 120px; text-align: right; font-size: 16px;">
        </div>

        <div class="option-btn" style="flex-direction: row; align-items: center;">
          <span class="opt-label">Ventas generadas (MAD):</span>
          <input type="number" id="roi-ventas" value="12000" 
            style="background: var(--darker); border: 1px solid var(--cyan); color: var(--text); 
                   padding: 8px 12px; border-radius: 8px; width: 120px; text-align: right; font-size: 16px;">
        </div>

        <div class="result-box mt-2">
          <div class="result-title">RESULTADO</div>
          <div class="result-row">
            <span class="result-label">ROI</span>
            <span class="result-value price" id="roi-resultado">2.300%</span>
          </div>
        </div>

        <button class="btn btn-primary" onclick="app.calcularROI()">Calcular</button>
        <button class="btn btn-secondary" onclick="app.renderHerramientas()">← Volver</button>
      </div>
    `;
  }

  function calcularROI() {
    const inversion = parseFloat($('roi-inversion').value) || 0;
    const ventas = parseFloat($('roi-ventas').value) || 0;
    const roi = inversion > 0 ? ((ventas - inversion) / inversion * 100).toFixed(0) : 0;
    $('roi-resultado').textContent = roi + '%';
  }

  function renderReferidos() {
    const container = $('main-content');
    container.innerHTML = `
      <div class="card animate-in">
        <div class="card-title">🤝 Programa "Traes 1, Ganas 1"</div>

        <div class="result-box">
          <div class="result-title">🥉 NIVEL 1 — Traes 1</div>
          <div class="result-row">
            <span class="result-label">Tú ganas</span>
            <span class="result-value">1 mes GRATIS mantenimiento</span>
          </div>
          <div class="result-row">
            <span class="result-label">Nuevo cliente</span>
            <span class="result-value">10% descuento setup</span>
          </div>
        </div>

        <div class="result-box">
          <div class="result-title">🥈 NIVEL 2 — Traes 3</div>
          <div class="result-row">
            <span class="result-label">Tú ganas</span>
            <span class="result-value">Setup siguiente fase GRATIS</span>
          </div>
        </div>

        <div class="result-box">
          <div class="result-title">🥇 NIVEL 3 — Traes 5</div>
          <div class="result-row">
            <span class="result-label">Tú ganas</span>
            <span class="result-value">3 meses mantenimiento GRATIS</span>
          </div>
        </div>

        <div class="result-box" style="border-color: var(--gold);">
          <div class="result-title" style="color: var(--gold);">💎 NIVEL DIAMANTE — Traes 10</div>
          <div class="result-row">
            <span class="result-label">Tú ganas</span>
            <span class="result-value" style="color: var(--gold);">1 año GRATIS + caso de éxito publicado</span>
          </div>
        </div>

        <button class="btn btn-secondary" onclick="app.renderHerramientas()">← Volver</button>
      </div>
    `;
  }

  function renderVentana24h() {
    const container = $('main-content');
    container.innerHTML = `
      <div class="card animate-in">
        <div class="card-title">⏰ La Ventana de 24h</div>
        <div class="card-subtitle">Por qué el bot responde GRATIS</div>

        <div style="background: var(--darker); border-radius: var(--radius-sm); padding: 16px; margin: 12px 0;">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <div style="width: 12px; height: 12px; background: var(--success); border-radius: 50%; box-shadow: 0 0 10px var(--success);"></div>
            <span style="font-size: 13px; color: var(--success); font-weight: 600;">VENTANA GRATIS (0-24h)</span>
          </div>
          <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6;">
            Si el cliente escribe primero, el bot puede responder durante 24 horas <strong style="color: var(--text);">SIN COSTO</strong>.
            <br><br>
            📊 El 85% de los pedidos se cierran en la primera hora.<br>
            📊 El 95% se cierran en las primeras 6 horas.
          </p>
        </div>

        <div style="background: var(--darker); border-radius: var(--radius-sm); padding: 16px; margin: 12px 0; border: 1px solid rgba(239,68,68,0.2);">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <div style="width: 12px; height: 12px; background: var(--danger); border-radius: 50%;"></div>
            <span style="font-size: 13px; color: var(--danger); font-weight: 600;">COSTO (24h+)</span>
          </div>
          <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6;">
            Si TÚ inicias la conversación después de 24h: ~0.05€ por mensaje.
            <br><br>
            ✅ <strong style="color: var(--text);">Solución:</strong> Ponemos el botón de WhatsApp en Google Maps y tu web. El cliente siempre escribe primero.
          </p>
        </div>

        <button class="btn btn-secondary" onclick="app.renderHerramientas()">← Volver</button>
      </div>
    `;
  }

  // ===== UTILIDADES =====
  function reiniciar() {
    state.step = 0;
    state.respuestas = {};
    state.cliente = null;
    renderStepper();
    renderP0();
  }

  function showToast(msg) {
    const toast = $('toast');
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
  }

  function navegar(pagina) {
    // Actualizar nav activo
    $$('.nav-item').forEach(el => el.classList.remove('active'));
    $(`nav-${pagina}`)?.classList.add('active');

    switch(pagina) {
      case 'calculadora': reiniciar(); break;
      case 'historial': renderHistorial(); break;
      case 'herramientas': renderHerramientas(); break;
      case 'config': renderConfig(); break;
    }
  }

  function renderConfig() {
    const container = $('main-content');
    container.innerHTML = `
      <div class="card animate-in">
        <div class="card-title">⚙️ Configuración</div>

        <div class="option-btn" style="flex-direction: row; justify-content: space-between; align-items: center;">
          <span class="opt-label">Nombre del consultor</span>
          <input type="text" id="config-nombre" value="${ISA_CONFIG.consultor.nombre}" 
            style="background: var(--darker); border: 1px solid var(--cyan); color: var(--text); 
                   padding: 8px 12px; border-radius: 8px; width: 160px; font-size: 14px;">
        </div>

        <div class="option-btn" style="flex-direction: row; justify-content: space-between; align-items: center;">
          <span class="opt-label">Teléfono WhatsApp</span>
          <input type="text" id="config-telefono" value="${ISA_CONFIG.consultor.telefono}" 
            style="background: var(--darker); border: 1px solid var(--cyan); color: var(--text); 
                   padding: 8px 12px; border-radius: 8px; width: 160px; font-size: 14px;">
        </div>

        <button class="btn btn-primary mt-2" onclick="app.guardarConfig()">Guardar</button>

        <div class="mt-2" style="font-size: 12px; color: var(--text-muted); text-align: center;">
          Versión ${ISA_CONFIG.version} | ISA ChatCommerce
        </div>
      </div>
    `;
  }

  function guardarConfig() {
    ISA_CONFIG.consultor.nombre = $('config-nombre').value;
    ISA_CONFIG.consultor.telefono = $('config-telefono').value;
    localStorage.setItem('isa_config', JSON.stringify(ISA_CONFIG.consultor));
    showToast('✓ Configuración guardada');
  }

  // ===== EXPONER FUNCIONES GLOBALES =====
  window.app = {
    toggleP0,
    validarP0,
    seleccionarP1,
    seleccionarP2,
    seleccionarP3,
    seleccionarP4,
    generarContrato,
    compartirResultado,
    reiniciar,
    navegar,
    renderHerramientas,
    renderBenchmarks,
    renderCalculadoraROI,
    calcularROI,
    renderReferidos,
    renderVentana24h,
    limpiarHistorial,
    guardarConfig
  };

})();
