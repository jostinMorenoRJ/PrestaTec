const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[c]));
const fmt = s => s ? new Date(s).toLocaleString('es-CO', {
  dateStyle: 'short', timeStyle: 'short'
}) : '—';

let perfil = null;
const permisos = new Set();
const puede = accion => permisos.has(accion);

// C12: navegación derivada del rol. El backend ya no emite otros perfiles.
const PERFILES = {
  Consulta: { inicio: 'mis', nav: [['mis', 'Mis préstamos']] },
  Guarda: { inicio: 'porteria', nav: [
    ['porteria', 'Portería'], ['reservas', 'Préstamos']
  ] },
  Encargado: { inicio: 'panel', nav: [
    ['panel', 'Resumen'], ['equipos', 'Inventario'], ['reservas', 'Préstamos'],
    ['porteria', 'Portería'], ['usuarios', 'Usuarios']
  ] },
};

async function api(ruta, metodo, cuerpo) {
  const opciones = metodo
    ? { method: metodo, credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cuerpo ?? {}) }
    : { credentials: 'same-origin' };
  const respuesta = await fetch('/api' + ruta, opciones);
  const texto = await respuesta.text();
  let datos = texto;
  try { datos = JSON.parse(texto); } catch (_e) { /* texto plano */ }
  if (!respuesta.ok) {
    if (respuesta.status === 401 && ruta !== '/auth/login' && ruta !== '/auth/me') {
      perfil = null; permisos.clear(); aplicarPermisos();
    }
    throw { status: respuesta.status, data: datos };
  }
  return datos;
}

const msg = e => typeof e.data === 'string' ? e.data
  : (e.data?.mensaje || 'Ocurrió un error. Intente de nuevo.');
function toast(texto, ok = true) {
  const el = $('#toast');
  el.textContent = texto;
  el.className = 'show ' + (ok ? 'ok' : 'err');
  setTimeout(() => el.className = '', 3500);
}
function dialog(html) {
  const d = $('#dlg');
  d.innerHTML = html + '<p><button id="cerrarDlg" class="sec">Cerrar</button></p>';
  d.showModal();
  $('#cerrarDlg').onclick = () => d.close();
}
function vacio(titulo, texto) {
  return `<div class="empty"><span aria-hidden="true">◌</span><b>${esc(titulo)}</b><p>${esc(texto)}</p></div>`;
}
const CLASES_ESTADO = {
  'Disponible': 'ok', 'Devuelta': 'ok', 'Confirmada': 'info',
  'Prestado': 'warn', 'Entregada': 'warn', 'Mantenimiento': 'warn',
  'Atrasada': 'bad', 'Fuera de servicio': 'bad',
  'Cancelada': 'apagado', 'No se presentó': 'apagado',
};
const badge = estado => `<span class="badge ${CLASES_ESTADO[estado] || ''}">${esc(estado)}</span>`;
const lista = (datos, textoVacio) => datos.length
  ? `<ul class="list">${datos.map(x => `<li><b>${esc(x.equipo)}</b> ${esc(x.usuario)}<small>${fmt(x.inicio)} → ${fmt(x.fin)}</small>${badge(x.estado)}</li>`).join('')}</ul>`
  : vacio('Sin elementos', textoVacio);

const views = { mis, panel, equipos, reservas, porteria, usuarios };

function aplicarPermisos() {
  const config = perfil ? PERFILES[perfil.rol] : null;
  document.body.classList.toggle('sin-sesion', !perfil);
  document.body.classList.toggle('con-sesion', !!perfil);
  $('#acceso').hidden = !!perfil;
  if (!perfil) {
    $('#error-acceso').hidden = true;
    $('#error-acceso').textContent = '';
    $('#usuario').focus();
  }
  $('#quien').innerHTML = perfil
    ? `<span class="rol-chip rol-${esc(perfil.rol.toLowerCase())}">${esc(perfil.rol)}</span><span>${esc(perfil.nombre)}</span>`
    : '';
  $('#salir').hidden = !perfil;
  $('#titulo-vista').textContent = {
    Consulta: 'Mi espacio', Guarda: 'Control de portería',
    Encargado: 'Panel general',
  }[perfil?.rol] || 'Panel general';
  $$('nav button').forEach(b => {
    const opcion = config?.nav.find(x => x[0] === b.dataset.v);
    b.hidden = !opcion;
    if (opcion) b.textContent = opcion[1];
  });
  $('.report-link').hidden = !puede('EXPORTAR');
}

async function iniciar() {
  try {
    perfil = await api('/auth/me');
    permisos.clear();
    (perfil.permisos || []).forEach(p => permisos.add(p));
    aplicarPermisos();
    show(perfil.vistaInicial === 'gestion' ? 'panel' : perfil.vistaInicial);
  } catch (_e) {
    perfil = null; permisos.clear(); aplicarPermisos();
  }
}

$('#fl').onsubmit = async ev => {
  ev.preventDefault();
  $('#error-acceso').hidden = true;
  try {
    await api('/auth/login', 'POST', Object.fromEntries(new FormData(ev.target)));
    ev.target.reset();
    await iniciar();
    toast(`Bienvenido, ${perfil?.nombre || ''}`);
  } catch (e) {
    $('#error-acceso').textContent = msg(e);
    $('#error-acceso').hidden = false;
    toast(msg(e), false);
  }
};
$('#salir').onclick = async () => {
  try { await api('/auth/logout', 'POST', {}); } catch (_e) { /* sesión local */ }
  perfil = null; permisos.clear(); aplicarPermisos();
  toast('Sesión cerrada');
};

function show(v) {
  if (!perfil) return;
  const permitidas = (PERFILES[perfil.rol]?.nav || []).map(x => x[0]);
  if (!permitidas.includes(v)) return;
  $$('nav button').forEach(b => b.classList.toggle('on', b.dataset.v === v));
  $$('main section.view').forEach(s => s.hidden = s.id !== 'v-' + v);
  views[v]().catch(e => toast(msg(e), false));
}

/* ---------- Consulta: Mis préstamos ---------- */

function filasMis(prestamos) {
  if (!prestamos.length) {
    return vacio('Todavía no tienes préstamos',
      'Cuando solicites un equipo, aparecerá aquí con su estado y fechas.');
  }
  return `<div class="tabla-wrap"><table><thead><tr><th>Equipo</th><th>Desde</th><th>Hasta</th><th>Estado</th><th></th></tr></thead><tbody>
    ${prestamos.map(p => `<tr><td><b>${esc(p.equipo)}</b><small>${esc(p.equipoId)}</small></td>
      <td>${fmt(p.inicio)}</td><td>${fmt(p.fin)}</td><td>${badge(p.estado)}</td>
      <td class="act">${puede('CONSULTAR_HISTORIAL') ? `<button class="link" data-h="${esc(p.equipoId)}">Historial</button>` : ''}</td></tr>`).join('')}
  </tbody></table></div>`;
}

async function mis() {
  const prestamos = await api('/mis-prestamos');
  const activos = prestamos.filter(p => ['Entregada', 'Atrasada'].includes(p.estado));
  const proximas = prestamos.filter(p => p.estado === 'Confirmada');
  const ahora = new Date(Date.now() - new Date().getTimezoneOffset() * 6e4);
  const inicio = ahora.toISOString().slice(0, 16);
  const fin = new Date(ahora.getTime() + 2 * 3600 * 1000).toISOString().slice(0, 16);

  $('#v-mis').innerHTML = `<div class="saludo">
      <div><span class="eyebrow">ESPACIO DEL ESTUDIANTE</span>
        <h2>Hola, ${esc(perfil.nombre.split(' ')[0])}</h2>
        <p>Consulta tus equipos y solicita uno nuevo en menos de un minuto.</p></div>
      <div class="saludo-icono" aria-hidden="true">💻</div>
    </div>
    <div class="cards">
      <div class="card warn"><b>${activos.length}</b><span>En tu poder</span></div>
      <div class="card info"><b>${proximas.length}</b><span>Reservas activas</span></div>
      <div class="card bad"><b>${prestamos.filter(p => p.estado === 'Atrasada').length}</b><span>Por devolver</span></div>
    </div>
    <div class="solicitud card">
      <div class="card-head"><div><span class="eyebrow">NUEVA SOLICITUD</span><h3>¿Qué equipo necesitas?</h3></div><span class="pill">Paso 1 de 2</span></div>
      <form id="fs" class="row">
        <label>Tipo<select name="tipo"><option>Portátil</option><option>Proyector</option></select></label>
        <label>Desde<input type="datetime-local" name="inicio" value="${inicio}" required></label>
        <label>Hasta<input type="datetime-local" name="fin" value="${fin}" required></label>
        <button type="submit">Buscar disponibles</button>
      </form>
      <div id="disp" class="disp">${vacio('Elige un horario', 'Selecciona tipo y fechas para ver los equipos libres.')}</div>
    </div>
    <div class="card"><div class="card-head"><div><span class="eyebrow">SEGUIMIENTO</span><h3>Mis movimientos</h3></div></div>
      ${filasMis(prestamos)}</div>`;

  $('#fs').onsubmit = async ev => {
    ev.preventDefault();
    const datos = Object.fromEntries(new FormData(ev.target));
    $('#disp').innerHTML = '<p class="cargando">Buscando equipos libres…</p>';
    try {
      const consulta = new URLSearchParams(datos);
      const libres = await api('/disponibilidad?' + consulta);
      if (!libres.length) {
        $('#disp').innerHTML = vacio('Sin equipos libres',
          'No hay unidades del tipo seleccionado en ese horario. Pruebe con otras fechas.');
        return;
      }
      $('#disp').innerHTML = `<p class="ayuda">Paso 2: elige una de las ${libres.length} opciones libres.</p>
        <div class="chips">${libres.map(e => `<button class="chip" data-id="${esc(e.id)}" data-nombre="${esc(e.nombre)}"><b>${esc(e.id)}</b>${esc(e.nombre)}</button>`).join('')}</div>`;
      $$('#disp [data-id]').forEach(b => b.onclick = () => reservar(b, datos));
    } catch (e) { $('#disp').innerHTML = vacio('No se pudo consultar', msg(e)); }
  };

  $$('#v-mis [data-h]').forEach(b => b.onclick = async () => {
    const historial = await api(`/equipos/${b.dataset.h}/historial`);
    dialog(`<h3>Historial de ${esc(b.dataset.h)}</h3>` + (historial.length
      ? `<ul class="list">${historial.map(x => `<li><small>${fmt(x.fecha)}</small>${esc(x.texto)}</li>`).join('')}</ul>`
      : vacio('Sin movimientos', 'Este equipo todavía no registra eventos.')));
  });
}

async function reservar(boton, datos) {
  boton.disabled = true;
  try {
    await api('/reservas', 'POST', {
      equipoId: boton.dataset.id,
      documento: perfil.documento,
      inicio: datos.inicio,
      fin: datos.fin,
    });
    toast(`Solicitud enviada para ${boton.dataset.nombre}`);
    mis();
  } catch (e) {
    if (e.status === 409 && e.data?.alternativas) {
      const alternativas = e.data.alternativas;
      $('#disp').innerHTML = `<div class="aviso">${esc(e.data.mensaje)}</div>` +
        (alternativas.length
          ? `<p class="ayuda">Estas unidades sí están libres:</p><div class="chips">${alternativas.map(a => `<button class="chip" data-id="${esc(a.id)}" data-nombre="${esc(a.nombre)}"><b>${esc(a.id)}</b>${esc(a.nombre)}</button>`).join('')}</div>`
          : vacio('Sin alternativas', 'No hay otro equipo del mismo tipo libre en ese horario.'));
      $$('#disp [data-id]').forEach(b => b.onclick = () => reservar(b, datos));
    } else {
      toast(msg(e), false);
      boton.disabled = false;
    }
  }
}

/* ---------- Encargado: resumen e inventario ---------- */

async function panel() {
  const [r, res] = await Promise.all([api('/resumen'), api('/reservas')]);
  const tarjetas = [
    ['Equipos en total', r.total, '', '▦'], ['Disponibles', r.disponibles, 'ok', '✓'],
    ['Prestados', r.prestados, 'warn', '↗'], ['En mantenimiento', r.mantenimiento, 'warn', '⚙'],
    ['Devoluciones atrasadas', r.atrasados, 'bad', '!'], ['Reservas de hoy', r.reservasHoy, 'info', '◷'],
  ];
  $('#v-panel').innerHTML = `<div class="cards">${tarjetas.map(x => `<div class="card ${x[2]}"><span class="icono">${x[3]}</span><b>${x[1]}</b><span>${x[0]}</span></div>`).join('')}</div>
    <div class="card"><div class="card-head"><div><span class="eyebrow">ATENCIÓN</span><h3>Devoluciones atrasadas</h3></div></div>
      ${lista(res.filter(x => x.estado === 'Atrasada'), 'No hay préstamos atrasados.')}</div>
    <div class="card"><div class="card-head"><div><span class="eyebrow">AGENDA</span><h3>Próximas reservas</h3></div></div>
      ${lista(res.filter(x => x.estado === 'Confirmada').reverse().slice(0, 6), 'No hay reservas pendientes.')}</div>`;
}

async function equipos() {
  const datos = await api('/equipos');
  const formulario = puede('CREAR_RECURSO')
    ? `<form id="fe" class="row"><label>Tipo<select name="tipo"><option>Portátil</option><option>Proyector</option></select></label>
       <label>Nombre<input name="nombre" placeholder="Ej. Dell Latitude 5420" required></label>
       <label>Ubicación<input name="ubicacion" placeholder="Biblioteca" required></label>
       <button type="submit">Agregar equipo</button></form>`
    : '';
  const puedeEstado = puede('HABILITAR') || puede('REGISTRAR_DANO');
  $('#v-equipos').innerHTML = `<div class="card"><div class="card-head"><div><span class="eyebrow">INVENTARIO</span><h3>Equipos registrados</h3></div><span class="pill">${datos.length} unidades</span></div>
    ${formulario}
    <div class="tabla-wrap"><table><thead><tr><th>Código</th><th>Equipo</th><th>Ubicación</th><th>Estado</th><th>Lo tiene</th><th></th></tr></thead><tbody>
    ${datos.map(e => `<tr><td><b>${e.id}</b></td><td>${e.tipo === 'Proyector' ? '📽️' : '💻'} ${esc(e.nombre)}</td>
      <td>${esc(e.ubicacion)}</td><td>${badge(e.estado)}</td><td>${esc(e.poseedor || '—')}</td>
      <td class="act"><button class="link" data-qr="${e.id}">QR</button>
      ${puede('CONSULTAR_HISTORIAL') ? `<button class="link" data-h="${e.id}">Historial</button>` : ''}
      ${puedeEstado ? `<select data-st="${e.id}" aria-label="Cambiar estado de ${e.id}"><option value="">Cambiar estado</option><option>Disponible</option><option>Mantenimiento</option><option>Fuera de servicio</option></select>` : ''}</td></tr>`).join('')}
    </tbody></table></div></div>`;

  if ($('#fe')) $('#fe').onsubmit = async ev => {
    ev.preventDefault();
    try {
      await api('/equipos', 'POST', Object.fromEntries(new FormData(ev.target)));
      toast('Equipo agregado'); equipos();
    } catch (e) { toast(msg(e), false); }
  };
  $$('[data-qr]').forEach(b => b.onclick = () => {
    dialog(`<h3>Etiqueta ${esc(b.dataset.qr)}</h3><div id="qrbox" class="qr"></div>
      <p>Pegue esta etiqueta en el equipo. Portería la escanea para validar la salida.</p>
      <button id="imprimirQR">Imprimir</button>`);
    $('#imprimirQR').onclick = () => window.print();
    new QRCode($('#qrbox'), { text: b.dataset.qr, width: 200, height: 200 });
  });
  $$('[data-h]').forEach(b => b.onclick = async () => {
    const historial = await api(`/equipos/${b.dataset.h}/historial`);
    dialog(`<h3>Historial de ${esc(b.dataset.h)}</h3>` + (historial.length
      ? `<ul class="list">${historial.map(x => `<li><small>${fmt(x.fecha)}</small>${esc(x.texto)}</li>`).join('')}</ul>`
      : vacio('Sin movimientos', 'Este equipo todavía no registra eventos.')));
  });
  $$('[data-st]').forEach(s => s.onchange = async () => {
    if (!s.value) return;
    const nota = prompt('Motivo o nota (opcional):') || '';
    try {
      await api(`/equipos/${s.dataset.st}/estado`, 'PUT', { estado: s.value, nota });
      toast('Estado actualizado'); equipos();
    } catch (e) { toast(msg(e), false); }
  });
}

/* ---------- Guarda y Encargado: préstamos ---------- */

async function reservas() {
  const datos = await api('/reservas');
  const gestionar = puede('ENTREGAR_DEVOLVER');
  const botones = x => {
    if (!gestionar) return '';
    if (x.estado === 'Confirmada') return `<button data-a="entregar" data-id="${x.id}">Entregar</button><button data-a="noshow" data-id="${x.id}">No llegó</button><button data-a="cancelar" data-id="${x.id}">Cancelar</button>`;
    if (['Entregada', 'Atrasada'].includes(x.estado)) return `<button data-a="devolver" data-id="${x.id}">Recibir devolución</button>`;
    return '';
  };
  $('#v-reservas').innerHTML = `<div class="card"><div class="card-head"><div><span class="eyebrow">OPERACIÓN</span><h3>Préstamos y reservas</h3></div><span class="pill">${datos.length} registros</span></div>
    ${datos.length ? `<div class="tabla-wrap"><table><thead><tr><th>Equipo</th><th>Usuario</th><th>Desde</th><th>Hasta</th><th>Estado</th><th></th></tr></thead><tbody>
    ${datos.map(x => `<tr><td><b>${esc(x.equipoId)}</b><small>${esc(x.equipo)}</small></td><td>${esc(x.usuario)}</td>
      <td>${fmt(x.inicio)}</td><td>${fmt(x.fin)}</td><td>${badge(x.estado)}</td><td class="act">${botones(x)}</td></tr>`).join('')}
    </tbody></table></div>` : vacio('Sin préstamos', 'Todavía no hay solicitudes registradas.')}</div>`;

  $$('[data-a]').forEach(b => b.onclick = async () => {
    const id = b.dataset.id, accion = b.dataset.a;
    let cuerpo = {};
    if (accion === 'entregar') {
      const responsable = prompt('Nombre de quien entrega el equipo:');
      if (!responsable) return;
      cuerpo = {
        responsable,
        estadoEntrega: prompt('Estado del equipo al entregarlo:', 'Bueno') || 'Bueno',
      };
    }
    if (accion === 'devolver') {
      const nota = prompt('¿Hay daños o novedades? Déjelo vacío si no hay.');
      if (nota === null) return;
      cuerpo = { danio: !!nota.trim(), nota };
    }
    try {
      await api(`/reservas/${id}/${accion}`, 'POST', cuerpo);
      toast('Operación registrada'); reservas();
    } catch (e) { toast(msg(e), false); }
  });
}

/* ---------- Portería ---------- */

const registros = [];
function beep(ok) {
  try {
    const c = new AudioContext(), o = c.createOscillator();
    o.frequency.value = ok ? 880 : 220;
    o.connect(c.destination); o.start(); o.stop(c.currentTime + (ok ? .12 : .4));
  } catch (_e) { /* audio opcional */ }
}
async function verificar(codigo) {
  codigo = codigo.trim();
  if (!codigo) return;
  const inicio = performance.now();
  try {
    const r = await api('/porteria/' + encodeURIComponent(codigo));
    const ms = Math.round(performance.now() - inicio);
    $('#res').className = 'res ' + (r.ok ? 'ok' : 'no');
    $('#res').innerHTML = `<strong>${r.ok ? '✔ Autorizado' : '✖ No autorizado'}</strong><p>${esc(r.mensaje)}</p>${r.detalle.map(d => `<small>${esc(d)}</small>`).join('')}<small class="tiempo">Verificado en ${ms} ms</small>`;
    beep(r.ok);
    registros.unshift(`<li class="${r.ok ? 'ok' : 'no'}"><b>${esc(codigo)}</b><small>${esc(r.mensaje)}</small></li>`);
    $('#log').innerHTML = registros.slice(0, 8).join('');
  } catch (e) { toast(msg(e), false); }
  $('#cod').value = ''; $('#cod').focus();
}
async function porteria() {
  $('#v-porteria').innerHTML = `<div class="gate">
    <div class="gate-head"><span class="eyebrow">CONTROL DE ACCESO</span><h2>Validación rápida en portería</h2>
      <p>Escanee el QR del equipo o digite la cédula y pulse Enter.</p></div>
    <div class="lector"><input id="cod" placeholder="Código PT-001 o cédula" autocomplete="off" aria-label="Código o cédula">
      <button id="verificar">Verificar</button><button id="cam" class="sec">Usar cámara</button></div>
    <div id="res" class="res">Esperando lectura…</div>
    <div class="card"><div class="card-head"><div><span class="eyebrow">REGISTRO</span><h3>Últimas verificaciones</h3></div></div>
      <ul id="log" class="list">${registros.length ? registros.slice(0, 8).join('') : '<li class="vacio">Aún no hay lecturas en esta sesión.</li>'}</ul></div>
  </div>`;
  $('#cod').focus();
  $('#cod').onkeydown = e => { if (e.key === 'Enter') verificar(e.target.value); };
  $('#verificar').onclick = () => verificar($('#cod').value);
  $('#cam').onclick = async () => {
    if (!('BarcodeDetector' in window)) {
      return toast('Este navegador no lee QR con cámara. Use un lector USB o digite el código.', false);
    }
    const video = document.createElement('video');
    video.className = 'camara'; video.autoplay = true;
    $('#res').before(video);
    try {
      video.srcObject = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      await video.play();
    } catch (_e) { video.remove(); return toast('No se pudo activar la cámara.', false); }
    const detector = new BarcodeDetector({ formats: ['qr_code'] });
    let ultimo = '';
    const bucle = async () => {
      if (!video.isConnected) return video.srcObject.getTracks().forEach(t => t.stop());
      const codigos = await detector.detect(video);
      if (codigos[0] && codigos[0].rawValue !== ultimo) {
        ultimo = codigos[0].rawValue; verificar(ultimo);
      }
      setTimeout(bucle, 400);
    };
    bucle();
  };
}

/* ---------- Encargado: usuarios ---------- */

async function usuarios() {
  const datos = await api('/usuarios');
  const formulario = puede('CREAR_RECURSO')
    ? `<form id="fu" class="row"><label>Nombre<input name="nombre" placeholder="Nombre completo" required></label>
       <label>Documento<input name="documento" placeholder="Cédula" required></label>
       <label>Rol<select name="rol"><option>Estudiante</option><option>Docente</option><option>Encargado</option><option>Guarda</option></select></label>
       <button type="submit">Registrar usuario</button></form>`
    : '';
  $('#v-usuarios').innerHTML = `<div class="card"><div class="card-head"><div><span class="eyebrow">PERSONAS</span><h3>Usuarios autorizados</h3></div><span class="pill">${datos.length} registros</span></div>
    ${formulario}<div class="tabla-wrap"><table><thead><tr><th>Nombre</th><th>Documento</th><th>Rol</th></tr></thead><tbody>
    ${datos.map(x => `<tr><td>${esc(x.nombre)}</td><td>${esc(x.documento)}</td><td>${badge(x.rol)}</td></tr>`).join('')}
    </tbody></table></div></div>`;
  if ($('#fu')) $('#fu').onsubmit = async ev => {
    ev.preventDefault();
    try {
      await api('/usuarios', 'POST', Object.fromEntries(new FormData(ev.target)));
      toast('Usuario registrado'); usuarios();
    } catch (e) { toast(msg(e), false); }
  };
}

/* La navegación se enlaza una sola vez; `show` filtra por perfil. */
$$('nav button').forEach(b => b.onclick = () => show(b.dataset.v));

iniciar();
