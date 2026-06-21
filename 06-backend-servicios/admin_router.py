"""
Admin Panel Router for ISA ChatCommerce
Endpoints API + HTML panel embebido (sin bot, solo admin)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional

from database import get_db
from models import LeadScrap

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/", response_class=HTMLResponse)
async def admin_panel():
    return ADMIN_HTML

@router.get("/api/leads")
async def api_list_leads(
    caso: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    pack: Optional[str] = Query(None),
    busqueda: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(LeadScrap).order_by(desc(LeadScrap.fecha_scrap))
    if caso: query = query.where(LeadScrap.caso == caso.upper())
    if estado: query = query.where(LeadScrap.estado == estado)
    if pack: query = query.where(LeadScrap.pack_asignado == pack)
    if busqueda:
        query = query.where(
            (LeadScrap.nombre_negocio.ilike(f"%{busqueda}%")) |
            (LeadScrap.telefono.ilike(f"%{busqueda}%")) |
            (LeadScrap.ciudad.ilike(f"%{busqueda}%"))
        )
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    result = await db.execute(query.offset(offset).limit(limit))
    leads = result.scalars().all()
    return {
        "total": total, "limit": limit, "offset": offset,
        "leads": [{"id": l.id, "nombre_negocio": l.nombre_negocio, "telefono": l.telefono,
                   "direccion": l.direccion, "ciudad": l.ciudad, "caso": l.caso,
                   "pack_asignado": l.pack_asignado, "fuente": l.fuente, "categoria": l.categoria,
                   "estado": l.estado, "mensaje_personalizado": l.mensaje_personalizado,
                   "fecha_scrap": l.fecha_scrap.isoformat() if l.fecha_scrap else None,
                   "fecha_contacto": l.fecha_contacto.isoformat() if l.fecha_contacto else None,
                   "notas": l.notas} for l in leads]
    }

@router.get("/api/leads/{lead_id}")
async def api_get_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LeadScrap).where(LeadScrap.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead: raise HTTPException(404, "Lead no encontrado")
    return {"id": lead.id, "nombre_negocio": lead.nombre_negocio, "telefono": lead.telefono,
            "direccion": lead.direccion, "ciudad": lead.ciudad, "caso": lead.caso,
            "pack_asignado": lead.pack_asignado, "fuente": lead.fuente, "categoria": lead.categoria,
            "estado": lead.estado, "mensaje_personalizado": lead.mensaje_personalizado,
            "notas": lead.notas, "extra_data": lead.extra_data,
            "fecha_scrap": lead.fecha_scrap.isoformat() if lead.fecha_scrap else None}

@router.put("/api/leads/{lead_id}")
async def api_update_lead(lead_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LeadScrap).where(LeadScrap.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead: raise HTTPException(404, "Lead no encontrado")
    for campo in ["nombre_negocio", "telefono", "direccion", "ciudad", "caso", "pack_asignado", "fuente", "categoria", "estado", "mensaje_personalizado", "notas"]:
        if campo in data: setattr(lead, campo, data[campo])
    await db.commit(); await db.refresh(lead)
    return {"status": "updated", "id": lead.id}

@router.delete("/api/leads/{lead_id}")
async def api_delete_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LeadScrap).where(LeadScrap.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead: raise HTTPException(404, "Lead no encontrado")
    await db.delete(lead); await db.commit()
    return {"status": "deleted", "id": lead_id}

@router.get("/api/stats")
async def api_stats(db: AsyncSession = Depends(get_db)):
    total = await db.execute(select(func.count()).select_from(LeadScrap))
    por_caso = await db.execute(select(LeadScrap.caso, func.count()).group_by(LeadScrap.caso).order_by(LeadScrap.caso))
    por_estado = await db.execute(select(LeadScrap.estado, func.count()).group_by(LeadScrap.estado).order_by(desc(func.count())))
    return {"total_leads": total.scalar(), "por_caso": {r[0] or "Sin caso": r[1] for r in por_caso.all()}, "por_estado": {r[0] or "Sin estado": r[1] for r in por_estado.all()}}

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ISA ChatCommerce - Admin Leads</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>body{font-family:'Inter',sans-serif;}</style>
</head>
<body class="bg-slate-50 text-slate-800">
<nav class="bg-slate-900 text-white px-6 py-4 shadow-lg">
  <div class="max-w-7xl mx-auto flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center font-bold text-sm">ISA</div>
      <h1 class="font-semibold text-lg tracking-tight">ChatCommerce Admin</h1>
    </div>
    <div class="flex items-center gap-4 text-sm">
      <span id="stats-total" class="bg-slate-800 px-3 py-1 rounded-full">Cargando...</span>
      <span class="text-slate-400">v13.1</span>
    </div>
  </div>
</nav>
<div class="max-w-7xl mx-auto px-6 py-8">
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8" id="stats-cards">
    <div class="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
      <p class="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Leads</p>
      <p class="text-2xl font-bold text-slate-900 mt-1" id="stat-total">-</p>
    </div>
    <div class="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
      <p class="text-xs font-medium text-slate-500 uppercase tracking-wider">Nuevos</p>
      <p class="text-2xl font-bold text-emerald-600 mt-1" id="stat-nuevos">-</p>
    </div>
    <div class="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
      <p class="text-xs font-medium text-slate-500 uppercase tracking-wider">Contactados</p>
      <p class="text-2xl font-bold text-amber-600 mt-1" id="stat-contactados">-</p>
    </div>
    <div class="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
      <p class="text-xs font-medium text-slate-500 uppercase tracking-wider">Contratados</p>
      <p class="text-2xl font-bold text-blue-600 mt-1" id="stat-contratados">-</p>
    </div>
  </div>
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6">
    <div class="flex flex-wrap gap-3 items-end">
      <div class="flex-1 min-w-[200px]">
        <label class="block text-xs font-medium text-slate-500 mb-1">Buscar</label>
        <input type="text" id="filtro-busqueda" placeholder="Nombre, teléfono, ciudad..." class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none">
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-500 mb-1">Caso</label>
        <select id="filtro-caso" class="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none">
          <option value="">Todos</option>
          <option value="A">A</option><option value="B">B</option><option value="C">C</option>
          <option value="D">D</option><option value="E">E</option><option value="F">F</option><option value="G">G</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-500 mb-1">Estado</label>
        <select id="filtro-estado" class="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none">
          <option value="">Todos</option>
          <option value="nuevo">Nuevo</option>
          <option value="contactado">Contactado</option>
          <option value="interesado">Interesado</option>
          <option value="contratado">Contratado</option>
          <option value="rechazado">Rechazado</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-500 mb-1">Pack</label>
        <select id="filtro-pack" class="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none">
          <option value="">Todos</option>
          <option value="Basico">Básico</option>
          <option value="Pro">Pro</option>
          <option value="Elite">Elite</option>
        </select>
      </div>
      <button onclick="cargarLeads()" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium transition">Filtrar</button>
      <button onclick="resetFiltros()" class="px-5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition">Reset</button>
    </div>
  </div>
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 border-b border-slate-200">
          <tr>
            <th class="px-4 py-3 text-left font-semibold text-slate-600">ID</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600">Negocio</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600">Teléfono</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600">Caso</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600">Pack</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600">Estado</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600">Ciudad</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600">Fecha</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600">Acciones</th>
          </tr>
        </thead>
        <tbody id="tabla-leads" class="divide-y divide-slate-100">
          <tr><td colspan="9" class="px-4 py-8 text-center text-slate-400">Cargando leads...</td></tr>
        </tbody>
      </table>
    </div>
    <div class="px-4 py-3 border-t border-slate-200 flex items-center justify-between bg-slate-50">
      <span class="text-xs text-slate-500" id="pagina-info">Página 1</span>
      <div class="flex gap-2">
        <button onclick="paginaAnterior()" id="btn-prev" class="px-3 py-1 bg-white border border-slate-300 rounded text-xs hover:bg-slate-50 disabled:opacity-50">Anterior</button>
        <button onclick="paginaSiguiente()" id="btn-next" class="px-3 py-1 bg-white border border-slate-300 rounded text-xs hover:bg-slate-50 disabled:opacity-50">Siguiente</button>
      </div>
    </div>
  </div>
</div>
<div id="modal-editar" class="fixed inset-0 bg-black/50 hidden items-center justify-center z-50 p-4">
  <div class="bg-white rounded-xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
    <div class="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
      <h3 class="font-semibold text-lg">Editar Lead</h3>
      <button onclick="cerrarModal()" class="text-slate-400 hover:text-slate-600 text-2xl leading-none">&times;</button>
    </div>
    <div class="p-6 space-y-4" id="form-editar"></div>
    <div class="px-6 py-4 border-t border-slate-200 flex justify-end gap-3">
      <button onclick="cerrarModal()" class="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg text-sm">Cancelar</button>
      <button onclick="guardarLead()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium">Guardar</button>
    </div>
  </div>
</div>
<div id="toast" class="fixed bottom-6 right-6 px-4 py-3 rounded-lg shadow-lg text-white text-sm font-medium transform translate-y-20 opacity-0 transition-all duration-300 z-50"></div>
<script>
// FIX: API_BASE detecta automáticamente el path correcto
// En local: /admin  |  En Render con trailing slash: /admin/
const API_BASE = (window.location.pathname.endsWith('/') ? window.location.pathname.slice(0,-1) : window.location.pathname) || '/admin';

let leadsData = [], currentOffset = 0, currentLimit = 50, currentTotal = 0, editingId = null;

function showToast(msg, type='success') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `fixed bottom-6 right-6 px-4 py-3 rounded-lg shadow-lg text-white text-sm font-medium transform transition-all duration-300 z-50 ${type==='error'?'bg-red-600':'bg-emerald-600'}`;
  t.style.transform = 'translateY(0)'; t.style.opacity = '1';
  setTimeout(() => { t.style.transform='translateY(20px)'; t.style.opacity='0'; }, 3000);
}

async function cargarStats() {
  try {
    const r = await fetch(`${API_BASE}/api/stats`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    document.getElementById('stat-total').textContent = d.total_leads || 0;
    document.getElementById('stat-nuevos').textContent = d.por_estado['nuevo'] || 0;
    document.getElementById('stat-contactados').textContent = d.por_estado['contactado'] || 0;
    document.getElementById('stat-contratados').textContent = d.por_estado['contratado'] || 0;
    document.getElementById('stats-total').textContent = `${d.total_leads} leads`;
  } catch(e) { 
    console.error('Stats error:', e);
    document.getElementById('stats-total').textContent = 'Error stats';
  }
}

async function cargarLeads() {
  const params = new URLSearchParams();
  params.set('limit', currentLimit); params.set('offset', currentOffset);
  const caso = document.getElementById('filtro-caso').value;
  const estado = document.getElementById('filtro-estado').value;
  const pack = document.getElementById('filtro-pack').value;
  const busqueda = document.getElementById('filtro-busqueda').value;
  if (caso) params.set('caso', caso);
  if (estado) params.set('estado', estado);
  if (pack) params.set('pack', pack);
  if (busqueda) params.set('busqueda', busqueda);

  try {
    const url = `${API_BASE}/api/leads?${params}`;
    console.log('Fetching:', url);
    const r = await fetch(url);
    if (!r.ok) {
      const err = await r.text();
      throw new Error(`HTTP ${r.status}: ${err}`);
    }
    const d = await r.json();
    leadsData = d.leads; currentTotal = d.total;
    renderTabla(); renderPaginacion();
  } catch(e) {
    console.error('Leads error:', e);
    document.getElementById('tabla-leads').innerHTML = `<tr><td colspan="9" class="px-4 py-8 text-center text-red-500">Error: ${e.message}</td></tr>`;
  }
}

function badgeEstado(estado) {
  const map = {'nuevo':'bg-emerald-100 text-emerald-700','contactado':'bg-amber-100 text-amber-700','interesado':'bg-blue-100 text-blue-700','contratado':'bg-indigo-100 text-indigo-700','rechazado':'bg-slate-100 text-slate-600'};
  return map[estado] || 'bg-slate-100 text-slate-600';
}
function badgeCaso(caso) {
  const colors = ['bg-rose-100 text-rose-700','bg-orange-100 text-orange-700','bg-amber-100 text-amber-700','bg-yellow-100 text-yellow-700','bg-lime-100 text-lime-700','bg-emerald-100 text-emerald-700','bg-teal-100 text-teal-700'];
  const idx = (caso || 'G').charCodeAt(0) - 65;
  return colors[Math.min(Math.max(idx,0),6)] || 'bg-slate-100 text-slate-600';
}
function renderTabla() {
  const tbody = document.getElementById('tabla-leads');
  if (!leadsData.length) { tbody.innerHTML = `<tr><td colspan="9" class="px-4 py-8 text-center text-slate-400">No hay leads</td></tr>`; return; }
  tbody.innerHTML = leadsData.map(l => `
    <tr class="hover:bg-slate-50 transition">
      <td class="px-4 py-3 font-mono text-xs text-slate-500">#${l.id}</td>
      <td class="px-4 py-3 font-medium text-slate-900">${l.nombre_negocio}</td>
      <td class="px-4 py-3 text-slate-600">${l.telefono}</td>
      <td class="px-4 py-3"><span class="px-2 py-0.5 rounded text-xs font-semibold ${badgeCaso(l.caso)}">${l.caso || '-'}</span></td>
      <td class="px-4 py-3 text-slate-600">${l.pack_asignado || '-'}</td>
      <td class="px-4 py-3"><span class="px-2 py-0.5 rounded text-xs font-semibold ${badgeEstado(l.estado)}">${l.estado}</span></td>
      <td class="px-4 py-3 text-slate-600">${l.ciudad || '-'}</td>
      <td class="px-4 py-3 text-xs text-slate-500">${l.fecha_scrap ? new Date(l.fecha_scrap).toLocaleDateString('es-ES') : '-'}</td>
      <td class="px-4 py-3">
        <div class="flex gap-2">
          <button onclick="editarLead(${l.id})" class="text-blue-600 hover:text-blue-800 text-xs font-medium">Editar</button>
          <button onclick="eliminarLead(${l.id})" class="text-red-600 hover:text-red-800 text-xs font-medium">Eliminar</button>
        </div>
      </td>
    </tr>
  `).join('');
}
function renderPaginacion() {
  const totalPages = Math.ceil(currentTotal / currentLimit);
  const currentPage = Math.floor(currentOffset / currentLimit) + 1;
  document.getElementById('pagina-info').textContent = `Página ${currentPage} de ${totalPages} (${currentTotal} total)`;
  document.getElementById('btn-prev').disabled = currentOffset === 0;
  document.getElementById('btn-next').disabled = currentOffset + currentLimit >= currentTotal;
}
function paginaAnterior() { currentOffset -= currentLimit; if(currentOffset<0)currentOffset=0; cargarLeads(); }
function paginaSiguiente() { currentOffset += currentLimit; cargarLeads(); }
function resetFiltros() {
  document.getElementById('filtro-caso').value='';
  document.getElementById('filtro-estado').value='';
  document.getElementById('filtro-pack').value='';
  document.getElementById('filtro-busqueda').value='';
  currentOffset=0; cargarLeads();
}
async function editarLead(id) {
  try {
    const r = await fetch(`${API_BASE}/api/leads/${id}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const l = await r.json();
    editingId = id;
    document.getElementById('form-editar').innerHTML = `
      <div><label class="block text-xs font-medium text-slate-500 mb-1">Nombre Negocio</label><input id="edit-nombre" value="${l.nombre_negocio||''}" class="w-full px-3 py-2 border rounded-lg text-sm"></div>
      <div><label class="block text-xs font-medium text-slate-500 mb-1">Teléfono</label><input id="edit-telefono" value="${l.telefono||''}" class="w-full px-3 py-2 border rounded-lg text-sm"></div>
      <div class="grid grid-cols-2 gap-3">
        <div><label class="block text-xs font-medium text-slate-500 mb-1">Caso</label>
          <select id="edit-caso" class="w-full px-3 py-2 border rounded-lg text-sm">
            <option value="">-</option><option value="A" ${l.caso==='A'?'selected':''}>A</option><option value="B" ${l.caso==='B'?'selected':''}>B</option><option value="C" ${l.caso==='C'?'selected':''}>C</option><option value="D" ${l.caso==='D'?'selected':''}>D</option><option value="E" ${l.caso==='E'?'selected':''}>E</option><option value="F" ${l.caso==='F'?'selected':''}>F</option><option value="G" ${l.caso==='G'?'selected':''}>G</option>
          </select>
        </div>
        <div><label class="block text-xs font-medium text-slate-500 mb-1">Pack</label>
          <select id="edit-pack" class="w-full px-3 py-2 border rounded-lg text-sm">
            <option value="">-</option><option value="Basico" ${l.pack_asignado==='Basico'?'selected':''}>Básico</option><option value="Pro" ${l.pack_asignado==='Pro'?'selected':''}>Pro</option><option value="Elite" ${l.pack_asignado==='Elite'?'selected':''}>Elite</option>
          </select>
        </div>
      </div>
      <div><label class="block text-xs font-medium text-slate-500 mb-1">Estado</label>
        <select id="edit-estado" class="w-full px-3 py-2 border rounded-lg text-sm">
          <option value="nuevo" ${l.estado==='nuevo'?'selected':''}>Nuevo</option>
          <option value="contactado" ${l.estado==='contactado'?'selected':''}>Contactado</option>
          <option value="interesado" ${l.estado==='interesado'?'selected':''}>Interesado</option>
          <option value="contratado" ${l.estado==='contratado'?'selected':''}>Contratado</option>
          <option value="rechazado" ${l.estado==='rechazado'?'selected':''}>Rechazado</option>
        </select>
      </div>
      <div><label class="block text-xs font-medium text-slate-500 mb-1">Ciudad</label><input id="edit-ciudad" value="${l.ciudad||''}" class="w-full px-3 py-2 border rounded-lg text-sm"></div>
      <div><label class="block text-xs font-medium text-slate-500 mb-1">Dirección</label><input id="edit-direccion" value="${l.direccion||''}" class="w-full px-3 py-2 border rounded-lg text-sm"></div>
      <div><label class="block text-xs font-medium text-slate-500 mb-1">Mensaje Personalizado</label><textarea id="edit-mensaje" rows="3" class="w-full px-3 py-2 border rounded-lg text-sm">${l.mensaje_personalizado||''}</textarea></div>
      <div><label class="block text-xs font-medium text-slate-500 mb-1">Notas</label><textarea id="edit-notas" rows="2" class="w-full px-3 py-2 border rounded-lg text-sm">${l.notas||''}</textarea></div>
    `;
    document.getElementById('modal-editar').classList.remove('hidden');
    document.getElementById('modal-editar').classList.add('flex');
  } catch(e) { showToast('Error cargando lead: ' + e.message, 'error'); }
}
function cerrarModal() { document.getElementById('modal-editar').classList.add('hidden'); document.getElementById('modal-editar').classList.remove('flex'); editingId = null; }
async function guardarLead() {
  if (!editingId) return;
  const payload = {
    nombre_negocio: document.getElementById('edit-nombre').value,
    telefono: document.getElementById('edit-telefono').value,
    caso: document.getElementById('edit-caso').value,
    pack_asignado: document.getElementById('edit-pack').value,
    estado: document.getElementById('edit-estado').value,
    ciudad: document.getElementById('edit-ciudad').value,
    direccion: document.getElementById('edit-direccion').value,
    mensaje_personalizado: document.getElementById('edit-mensaje').value,
    notas: document.getElementById('edit-notas').value,
  };
  try {
    const r = await fetch(`${API_BASE}/api/leads/${editingId}`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    if (r.ok) { showToast('Lead actualizado'); cerrarModal(); cargarLeads(); cargarStats(); }
    else { const err = await r.text(); showToast('Error al guardar: ' + err, 'error'); }
  } catch(e) { showToast('Error de red: ' + e.message, 'error'); }
}
async function eliminarLead(id) {
  if (!confirm('¿Eliminar lead #' + id + '?')) return;
  try {
    const r = await fetch(`${API_BASE}/api/leads/${id}`, { method: 'DELETE' });
    if (r.ok) { showToast('Lead eliminado'); cargarLeads(); cargarStats(); }
    else showToast('Error al eliminar', 'error');
  } catch(e) { showToast('Error de red', 'error'); }
}
cargarStats(); cargarLeads();
</script>
</body>
</html>
"""
