const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = s => s ? new Date(s).toLocaleString('es-CO', {dateStyle:'short', timeStyle:'short'}) : '—';

let perfil = null;
const permisos = new Set();
const puede = accion => permisos.has(accion);

async function api(u, m, b) {
  const opciones = m
    ? {method:m, credentials:'same-origin', headers:{'Content-Type':'application/json'}, body:JSON.stringify(b ?? {})}
    : {credentials:'same-origin'};
  const r = await fetch('/api' + u, opciones);
  const t = await r.text(); let d = t; try { d = JSON.parse(t); } catch {}
  if (!r.ok) {
    if (r.status === 401 && u !== '/auth/login' && u !== '/auth/me') {
      perfil = null; permisos.clear(); aplicarPermisos();
    }
    throw {status:r.status, data:d};
  }
  return d;
}
const msg = e => typeof e.data === 'string' ? e.data : (e.data?.mensaje || 'Ocurrió un error');
function toast(t, ok = true) { const el = $('#toast'); el.textContent = t; el.className = 'show ' + (ok ? 'ok' : 'err'); setTimeout(() => el.className = '', 3500); }
const bd = e => `<span class="badge ${esc(e).replace(/\s/g,'-')}">${esc(e)}</span>`;
const list = (a, v) => a.length ? `<ul class="list">${a.map(x => `<li><b>${esc(x.equipo)}</b> ${esc(x.usuario)}<small>${fmt(x.inicio)} → ${fmt(x.fin)}</small>${bd(x.estado)}</li>`).join('')}</ul>` : `<p class="empty">${v}</p>`;
const views = {panel, equipos, reservas, porteria, usuarios};
document.querySelectorAll('nav button').forEach(b => b.onclick = () => show(b.dataset.v));

function aplicarPermisos() {
  document.body.classList.toggle('sin-sesion', !perfil);
  document.body.classList.toggle('con-sesion', !!perfil);
  $('#quien').textContent = perfil ? `${perfil.nombre} · ${perfil.rol}` : '';
  $('#salir').hidden = !perfil;
  $('nav button[data-v="porteria"]').hidden = !puede('VERIFICAR_PORTERIA');
  $('.report-link').hidden = !puede('EXPORTAR');
}
async function iniciar() {
  try {
    perfil = await api('/auth/me');
    permisos.clear();
    (perfil.permisos || []).forEach(p => permisos.add(p));
    aplicarPermisos();
    show('panel');
  } catch (_e) {
    perfil = null; permisos.clear(); aplicarPermisos();
  }
}
$('#fl').onsubmit = async ev => {
  ev.preventDefault();
  try {
    await api('/auth/login', 'POST', Object.fromEntries(new FormData(ev.target)));
    ev.target.reset();
    await iniciar();
    toast('Sesión iniciada');
  } catch (e) { toast(msg(e), false); }
};
$('#salir').onclick = async () => {
  try { await api('/auth/logout', 'POST', {}); } catch (_e) {}
  perfil = null; permisos.clear(); aplicarPermisos();
};

function show(v) {
  if (!perfil) return;
  document.querySelectorAll('nav button').forEach(b => b.classList.toggle('on', b.dataset.v === v));
  document.querySelectorAll('main section').forEach(s => s.hidden = s.id !== 'v-' + v);
  views[v]().catch(e => toast(msg(e), false));
}
function dialog(html) { const d = $('#dlg'); d.innerHTML = html + '<p><button class="sec" onclick="this.closest(\'dialog\').close()">Cerrar</button></p>'; d.showModal(); }

async function panel() {
  const [r, res] = await Promise.all([api('/resumen'), api('/reservas')]);
  const k = [['Equipos en total', r.total, ''], ['Disponibles', r.disponibles, 'ok'], ['Prestados', r.prestados, ''],
             ['En mantenimiento', r.mantenimiento, 'warn'], ['Devoluciones atrasadas', r.atrasados, 'bad'], ['Reservas de hoy', r.reservasHoy, '']];
  $('#v-panel').innerHTML = `<div class="cards">${k.map(x => `<div class="card ${x[2]}"><b>${x[1]}</b><span>${x[0]}</span></div>`).join('')}</div>
    <h2>Devoluciones atrasadas</h2>${list(res.filter(x => x.estado === 'Atrasada'), 'No hay préstamos atrasados.')}
    <h2>Próximas reservas</h2>${list(res.filter(x => x.estado === 'Confirmada').reverse().slice(0, 6), 'No hay reservas pendientes.')}`;
}

async function equipos() {
  const d = await api('/equipos');
  const formulario = puede('CREAR_RECURSO')
    ? `<form id="fe" class="row"><select name="tipo"><option>Portátil</option><option>Proyector</option></select>
       <input name="nombre" placeholder="Nombre, ej. Dell Latitude 5420" required><input name="ubicacion" placeholder="Ubicación" required><button>Agregar equipo</button></form>`
    : '';
  $('#v-equipos').innerHTML = `${formulario}
    <table><tr><th>Código</th><th>Equipo</th><th>Ubicación</th><th>Estado</th><th>Lo tiene</th><th></th></tr>
    ${d.map(e => `<tr><td>${e.id}</td><td>${e.tipo === 'Proyector' ? '📽️' : '💻'} ${esc(e.nombre)}</td><td>${esc(e.ubicacion)}</td><td>${bd(e.estado)}</td><td>${esc(e.poseedor || '—')}</td>
    <td class="act"><button data-qr="${e.id}">Etiqueta QR</button>${puede('CONSULTAR_HISTORIAL') ? `<button data-h="${e.id}">Historial</button>` : ''}
    ${(puede('HABILITAR') || puede('REGISTRAR_DANO')) ? `<select data-st="${e.id}"><option value="">Cambiar estado</option><option>Disponible</option><option>Mantenimiento</option><option>Fuera de servicio</option></select>` : ''}</td></tr>`).join('')}</table>`;
  if ($('#fe')) $('#fe').onsubmit = async ev => { ev.preventDefault(); try { await api('/equipos', 'POST', Object.fromEntries(new FormData(ev.target))); toast('Equipo agregado'); equipos(); } catch (e) { toast(msg(e), false); } };
  document.querySelectorAll('[data-qr]').forEach(b => b.onclick = () => {
    dialog(`<h3>${b.dataset.qr}</h3><div id="qrbox"></div><p>Pegue esta etiqueta en el equipo. Portería la escanea para validar la salida.</p><button onclick="window.print()">Imprimir</button>`);
    new QRCode($('#qrbox'), {text: b.dataset.qr, width: 200, height: 200});
  });
  document.querySelectorAll('[data-h]').forEach(b => b.onclick = async () => {
    const h = await api(`/equipos/${b.dataset.h}/historial`);
    dialog(`<h3>Historial de ${b.dataset.h}</h3>` + (h.length ? `<ul class="list">${h.map(x => `<li><small>${fmt(x.fecha)}</small>${esc(x.texto)}</li>`).join('')}</ul>` : '<p class="empty">Sin movimientos.</p>'));
  });
  document.querySelectorAll('[data-st]').forEach(s => s.onchange = async () => {
    if (!s.value) return;
    const nota = prompt('Motivo o nota (opcional):') || '';
    try { await api(`/equipos/${s.dataset.st}/estado`, 'PUT', {estado: s.value, nota}); toast('Estado actualizado'); equipos(); } catch (e) { toast(msg(e), false); }
  });
}

async function reservas() {
  const [u, e, r] = await Promise.all([api('/usuarios'), api('/equipos'), api('/reservas')]);
  const gestionar = puede('ENTREGAR_DEVOLVER');
  const ahora = new Date(Date.now() - new Date().getTimezoneOffset() * 6e4).toISOString().slice(0, 16);
  $('#v-reservas').innerHTML = `<form id="fr" class="row">
    <select name="documento">${u.map(x => `<option value="${esc(x.documento)}">${esc(x.nombre)} (${esc(x.rol)})</option>`).join('')}</select>
    <select name="equipoId">${e.filter(x => x.estado !== 'Mantenimiento' && x.estado !== 'Fuera de servicio').map(x => `<option value="${x.id}">${x.id} · ${esc(x.nombre)}</option>`).join('')}</select>
    <input type="datetime-local" name="inicio" value="${ahora}" required><input type="datetime-local" name="fin" required><button>Reservar</button></form>
    <div id="alt"></div>
    <table><tr><th>Equipo</th><th>Usuario</th><th>Desde</th><th>Hasta</th><th>Estado</th><th></th></tr>
    ${r.map(x => `<tr><td>${esc(x.equipoId)} ${esc(x.equipo)}</td><td>${esc(x.usuario)}</td><td>${fmt(x.inicio)}</td><td>${fmt(x.fin)}</td><td>${bd(x.estado)}</td><td class="act">${
      gestionar && x.estado === 'Confirmada' ? `<button data-a="entregar" data-id="${x.id}">Entregar</button><button data-a="noshow" data-id="${x.id}">No llegó</button><button data-a="cancelar" data-id="${x.id}">Cancelar</button>`
      : gestionar && (x.estado === 'Entregada' || x.estado === 'Atrasada') ? `<button data-a="devolver" data-id="${x.id}">Recibir devolución</button>` : ''}</td></tr>`).join('')}</table>`;
  $('#fr').onsubmit = async ev => {
    ev.preventDefault(); $('#alt').innerHTML = '';
    try { await api('/reservas', 'POST', Object.fromEntries(new FormData(ev.target))); toast('Reserva creada'); reservas(); }
    catch (er) {
      if (er.status === 409 && er.data.alternativas) {
        const a = er.data.alternativas;
        $('#alt').innerHTML = `<div class="alt">${esc(er.data.mensaje)} ${a.length ? 'Libres en ese horario:' : 'No hay otro equipo del mismo tipo libre en ese horario. Pruebe otra hora.'}</div>` +
          `<div class="chips">${a.map(x => `<button class="sec" data-alt="${x.id}">Reservar ${x.id} · ${esc(x.nombre)}</button>`).join('')}</div>`;
        document.querySelectorAll('[data-alt]').forEach(b => b.onclick = () => { $('#fr [name=equipoId]').value = b.dataset.alt; $('#fr').requestSubmit(); });
      } else toast(msg(er), false);
    }
  };
  document.querySelectorAll('[data-a]').forEach(b => b.onclick = async () => {
    const id = b.dataset.id, a = b.dataset.a; let body = {};
    if (a === 'entregar') {
      const responsable = prompt('Nombre de quien entrega el equipo:'); if (!responsable) return;
      body = {responsable, estadoEntrega: prompt('Estado del equipo al entregarlo:', 'Bueno') || 'Bueno'};
    }
    if (a === 'devolver') { const nota = prompt('¿Hay daños o novedades? Déjelo vacío si no hay.'); if (nota === null) return; body = {danio: !!nota.trim(), nota}; }
    try { await api(`/reservas/${id}/${a}`, 'POST', body); toast('Listo'); reservas(); } catch (e) { toast(msg(e), false); }
  });
}

const logs = [];
function beep(ok) { try { const c = new AudioContext(), o = c.createOscillator(); o.frequency.value = ok ? 880 : 220; o.connect(c.destination); o.start(); o.stop(c.currentTime + (ok ? .12 : .4)); } catch {} }
async function verificar(cod) {
  cod = cod.trim(); if (!cod) return;
  const t0 = performance.now();
  try {
    const r = await api('/porteria/' + encodeURIComponent(cod));
    const ms = Math.round(performance.now() - t0);
    $('#res').className = 'res ' + (r.ok ? 'ok' : 'no');
    $('#res').innerHTML = `${r.ok ? '✔ Autorizado' : '✖ No autorizado'}<br>${esc(r.mensaje)}${r.detalle.map(d => `<small>${esc(d)}</small>`).join('')}<small>Verificado en ${ms} ms</small>`;
    beep(r.ok);
    logs.unshift(`<li>${r.ok ? '✔' : '✖'} <b>${esc(cod)}</b><small>${esc(r.mensaje)}</small></li>`);
    $('#log').innerHTML = logs.slice(0, 8).join('');
  } catch (e) { toast(msg(e), false); }
  $('#cod').value = ''; $('#cod').focus();
}
async function porteria() {
  $('#v-porteria').innerHTML = `<div class="gate"><h2>Validación rápida en portería</h2>
    <p>Escanee el QR del equipo o digite la cédula del estudiante y pulse Enter.</p>
    <input id="cod" placeholder="Código o cédula" autocomplete="off"><button id="cam" class="sec">Usar cámara</button>
    <div id="res" class="res">Esperando lectura…</div><h2>Últimas verificaciones</h2><ul id="log" class="list"></ul></div>`;
  $('#cod').focus();
  $('#cod').onkeydown = e => { if (e.key === 'Enter') verificar(e.target.value); };
  $('#cam').onclick = async () => {
    if (!('BarcodeDetector' in window)) return toast('Este navegador no lee QR con la cámara. Use un lector USB o digite el código.', false);
    const v = document.createElement('video'); v.style.width = '100%'; $('#res').before(v);
    v.srcObject = await navigator.mediaDevices.getUserMedia({video: {facingMode: 'environment'}}); await v.play();
    const det = new BarcodeDetector({formats: ['qr_code']}); let last = '';
    const loop = async () => {
      if (!v.isConnected) return v.srcObject.getTracks().forEach(t => t.stop());
      const c = await det.detect(v); if (c[0] && c[0].rawValue !== last) { last = c[0].rawValue; verificar(last); }
      setTimeout(loop, 400);
    }; loop();
  };
}

async function usuarios() {
  const u = await api('/usuarios');
  const formulario = puede('CREAR_RECURSO')
    ? `<form id="fu" class="row"><input name="nombre" placeholder="Nombre completo" required><input name="documento" placeholder="Cédula" required>
       <select name="rol"><option>Estudiante</option><option>Docente</option><option>Encargado</option><option>Guarda</option></select><button>Registrar usuario</button></form>`
    : '';
  $('#v-usuarios').innerHTML = `${formulario}
    <table><tr><th>Nombre</th><th>Documento</th><th>Rol</th></tr>${u.map(x => `<tr><td>${esc(x.nombre)}</td><td>${esc(x.documento)}</td><td>${esc(x.rol)}</td></tr>`).join('')}</table>`;
  if ($('#fu')) $('#fu').onsubmit = async ev => { ev.preventDefault(); try { await api('/usuarios', 'POST', Object.fromEntries(new FormData(ev.target))); toast('Usuario registrado'); usuarios(); } catch (e) { toast(msg(e), false); } };
}

iniciar();
